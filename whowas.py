import os,sys,cPickle,time,urllib2,re,signal,commands,errno
import requests
import zlib,fcntl
import multiprocessing
import robotparser
from urlparse import urlparse,urljoin
from functools import wraps
from scapy.all import *
from config import *
from common import *

reload(sys) 
sys.setdefaultencoding('utf8')

def excute_sql_no_return(sql):
	"""
	Execute a SQL statement; no value returns
	"""
	conn=sqldb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PWD,db=DB_NAME)
	run_sql_no_return(sql,conn)

def excute_sql_bulk_no_return(sql, param):
	"""
	Execute a set of SQL statements; no values return
	"""
	conn=sqldb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PWD,db=DB_NAME)
	run_sql_bulk_no_return(sql,param,conn)


def init_db():
	"""
	Init two table templates, one for basic scanning information and 
	one for robot.txt information.
	"""
	for tb in TB_SQL:
		excute_sql_no_return(TB_SQL[tb])
			
def create_tb():
	"""
	Create tables based on table template.
	"""
	excute_sql_no_return("create table %s like %s"%(TB_BASE_NAME,TB_BASE_TEMPLATE))
	excute_sql_no_return("create table %s like %s"%(TB_ROBOT_NAME,TB_ROBOT_TEMPLATE))

def init_blacklist():
	buf=[ v.strip("\n") for v in open(BLACKIST_FILE).readlines() if v[0]!="#"]
	for t in buf:
		BLACLIST=BLACLIST+[v.strip("\n") for v in os.popen("dig +short %s"%(t)).readlines()]


def probe_port(ip,*ports):
	"""
	Send TCP SYN probs to ports of a given IP.
	Returns : a Python list that contains open ports of target IP
	:param ip: target IP address
	:para ports: target ports.

	Usage::
		>> probe_port("1.1.1.1", 80,81,82)
		>> probe_port("1.1.1.1", *[80,81,82])
	"""
	res=[]
	for port in ports:
		if sr1(IP(dst=ip)/TCP(dport=port, flags='S'), verbose=0, timeout=PROBE_DEFAULT_TIMEOUT):
			res.append(port)
	return res

def get_open_ports(ip):
	"""
	First probe port 80 and 443 of an IP, if neither of them is open, 
	then probe  port 22.
	Returns : a list contains open ports of target IP, eg. [22,80,443]
	:param ip: target IP address
	"""
	res=[]
	res=probe_port(ip, 80,443)
	if not res:
		res=probe_port(ip, 22)
	return res

def worker(inq,worker_id,probe_flag=True):
	"""
	Returns : None
	:param inq: the target worker queue
	:param no : the worker id 
	:probe_flag : if probe_flag is True, the worker will probe an IP "X"
	before fetching the content, otherwise trying to fetch the content on 
	"http://X" directly
	"""
	c=Crawler()
	#buffer for webpage related records
	tb_base=[]
	#buffer for robots.txt related records
	tb_robot=[]
	tb_base_len=0
	tb_robot_len=0
	#Loop unitl get "STOP"  
	for tip in iter(inq.get, 'STOP'):
		#By default use http protocol
		turl="http://"+tip
		res=[]
		fetch_flag=1
		try:
			if probe_flag==1:
				try:
					res=get_open_ports(tip)
				except:
					continue
				if not res:
					continue
				if 80 in res:
					pass
				elif 443 in res:
					turl="https://"+tip
				else:
					#If only open 22, not fetch the content
					fetch_flag=0
			
			rcode=""
			rheader=""
			content=""
			rbcontent=""
			rtt=""
			rbrtt=""
			#Default url for robots.txt file
			turl_r=turl+"/robots.txt"
			rbflag=False
			#First check the robots.txt file, if our crawler is allowed,
			#then fetch the content hosting on that IP
			if fetch_flag==1:
				try:
					rbflag,rbcontent,rbrtt=c.get_robot(turl_r)
					if rbcontent:
						rbcontent=unicode(rbcontent,errors='ignore').encode('utf-8')
					#Generate a robot.txt related record and store in the buffer
					tb_robot.append((tip,rbcontent,str(int(time.time())),str(rbrtt)))
					tb_robot_len=tb_robot_len+1
				except:
					rbflag=True
					f=open("err.log","a")
					f.write("robot:"+tip+"\n")
					f.close()
					pass
				if rbflag:
					try:
						flag,content,rcode,rheader,rtt=c.get_content(turl)
					except:
						f=open("err.log","a")
						f.write("content:"+tip+"\n")
						f.close()
				else:
					content="ROBOT"
			if content:
				content=unicode(content,errors='ignore').encode('utf-8')

			#Generate a webpage related record and store in the buffer
			rport=sorted([str(v) for v in res])
			rport="#".join(rport)
			tb_base.append((tip,rport,rcode,str(rheader),content,str(int(time.time())), str(rtt)))
			tb_base_len=tb_base_len+1

			#Insert the results into database. Two buffers are used to store the results.
			#If the buffer is "full", which means the buffer stores a given number of records,
			#insert the records into db and clear the buffer
			if tb_base_len==RECORD_NO_LIMIT:
				excute_sql_bulk_no_return("INSERT INTO "+TB_BASE_NAME+"(ip,port,code,header,content,time,rtt) VALUES (%s,%s,%s,%s,%s,%s,%s)",tb_base)
				tb_base=[]
				tb_base_len=0
			if tb_robot_len==RECORD_NO_LIMIT:
				excute_sql_bulk_no_return("INSERT INTO "+TB_ROBOT_NAME+"(ip,content,time,rtt) VALUES (%s,%s,%s,%s)",tb_robot)
				tb_robot=[]
				tb_robot_len=0
		except:
			f=open("err.log","a")
			f.write("unknown:"+tip+"\n")
			f.close()
			pass
	#Clear the buffer.
	excute_sql_bulk_no_return("INSERT INTO "+TB_BASE_NAME+"(ip,port,code,header,content,time,rtt) VALUES (%s,%s,%s,%s,%s,%s,%s)",tb_base)
	excute_sql_bulk_no_return("INSERT INTO "+TB_ROBOT_NAME+"(ip,content,time,rtt) VALUES (%s,%s,%s,%s)",tb_robot)
	tb_base=[]
	tb_robot=[]
	tb_base_len=0
	tb_robot_len=0
	print worker_id,"worker finish"
	


def go(fin,sc):
	#init_config()
	init_db()
	create_tb()
	sys.exit()
	m=Manager()
	for i in range(0,WORKER_NO):
		m.add_job(worker,i,sc)

	for i in open(fin):
		ip=i.strip("\n")
		if ip in BLACLIST:
			print ip,"in bl"
			#log
			continue
		m.add_input(ip)
	
	m.run_manger(WORKER_NO)
	m.wait()


class UserDefinedException(Exception):
	"""User defined exception"""
	class LongTimeoutError(Exception):
		args="LongTimeOut Error"


class LongTimeout(object):
	"""A decorator, throw LongTimeoutError exception if the running time of 
	a function exceeds a specific seconds.
	:param timeout: timeout for the target function
	Usage::
		@LongTimeout(10)
		def test():
			pass
	"""
	def __init__(self, timeout):
		self.timeout=timeout

	def __get__(self, obj, type=None):
		return self.__class__(self.func.__get__(obj, type))

	def __call__(self, func):
		self.func=func
		def _handle_timeout(signum, frame,self=None):
			raise UserDefinedException.LongTimeoutError()
		def wrapper(*args, **kwargs):
			signal.signal(signal.SIGALRM, _handle_timeout)
			signal.alarm(self.timeout)
			try:
				result = self.func(*args, **kwargs)
			finally:
				signal.alarm(0)
			return result
		return wraps(self.func)(wrapper)


class Manager(object):
	"""
	This is a multiprocess framework. There are two queues: a multiprocess 
	worker queue and an input queue. The workers keep getting data from the 
	input queue and execute the specified job until a stop requirement is meet. 
	The workers share the input queue.
	Usage::
		1. Init Manager
		2. Use add_job to specific the Job (a function) a worker will execute
		3. Use add_input to add input data to the input queue. 
		4. Run the manager.
	Example :: 
		#use 10 processes to print 1-10000
		def _print(inq):
			for no in iter(inq.get, 'STOP')
				print no

		def run():
			m=Manager()
			for i in xrange(10):
				m.add_job(_print)

			for i in xrange(10000)
				m.add_input(i)
			m.run_manger(1)
			m.wait()
	"""
	def __init__(self):
		self.inq=multiprocessing.Queue()
		self.pool=[]
		self.worker_no=0

	def add_job(self,func,worker_id,probe_flag):
		self.worker_no+=1
		p=multiprocessing.Process(target=func, args=(self.inq,worker_id,probe_flag))
		self.pool.append(p)
		p.daemon = True
		p.start()

	def add_input(job):
		self.inq.put(job)

	def run_manger(self,no):
		stop_flag=0
		stop_no=no
		while True:
			if stop_flag>=stop_no:
				for i in range(self.worker_no):
					self.inq.put('STOP')
				break
			if self.inq.empty():
				time.sleep(1)
				if self.inq.empty():
					stop_flag=stop_flag+1

	def wait(self):
		for t  in self.pool:
			t.join()


class Crawler(object):
	
	def __init__(self):
		self.timeout=HTTP_DEFAULT_TIMEOUT
		self.type_filter=['application/','audio/','image/','video/']


	def get_header(self,url,verf=False):
		"""
		Use Python requests stream request, first check the header of response, 
		grab the necessary information, if no exceptions are thrown, fetch the body.
		"""
		url=url
		history={}
		run_flag=True
		count=1
		try:
			r=requests.get(url,allow_redirects=True,stream=True,verify=verf,headers=header,timeout=self.timeout)
		except (requests.exceptions.SSLError,requests.exceptions.ConnectionError,
			UserDefinedException.LongTimeoutError,requests.exceptions.TooManyRedirects,
			requests.exceptions.HTTPError,requests.exceptions.Timeout) as e:
			return False,str(e.args)[0:15],False,False,False
		return True,r,r.status_code,dict(**r.headers),r.elapsed.total_seconds()

	@LongTimeout(HTTP_LONG_TIMEOUT)
	def get_content(self,url):
		"""
		Fetch the content of a webpage 
		"""
		flag,r,rcode,rheader,rtt=self.get_header(url)
		if not flag:
			return flag,r,rcode,rheader,rtt
		else:
			if rheader.has_key('content-length'):
				if int(rheader['content-length']) >=MAX_CONTENT_LENGTH:
					return False,"TargetSizeTooLarge",rcode,rheader,rtt

			if rheader.has_key('content-type'):
				for ft in self.type_filter:
					if rheader['content-type'].find(ft)!=-1:
						return False,"TargetTypeFiltered",rcode,rheader,rtt
			try:
				content=r.content[0:CONTENT_LENGTH_LIMIT]
			except:
				return False,"UnexceptedError",rcode,rheader,rtt
				
			return True,content,rcode,rheader,rtt

	@LongTimeout(HTTP_LONG_TIMEOUT)
	def get_robot(self,url):
		"""
		Check the robots.txt 
		"""
		try:
			rp = robotparser.RobotFileParser()
			rp.set_url(url)
			rp.read()
			if rp.can_fetch("*", "/")==1:
				return True,rp.content,rp.rtt
			else:
				return False,rp.content,rp.rtt
		except:
			return True,"Timeout",rp.rtt


def main():
	print "start work"
	go("ec2_ip_mar.li",1)


	
if __name__ == '__main__':
	#url="http://54.245.231.247"
	main()





