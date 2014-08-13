import os,sys,cPickle,time,urllib2,re,signal,commands,errno
import requests
from socket import *
import zlib,fcntl
import multiprocessing
from multiprocessing import Queue,JoinableQueue
from urlparse import urlparse,urljoin
import MySQLdb
from functools import wraps
from scapy.all import *
import robotparser
reload(sys) 
sys.setdefaultencoding('utf8')
header={
	"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Web-Security/1.0(it's for a research study,if you have questions,plz contact me liangw@cs.wisc.edu)",
	"From":"liangw@cs.wisc.edu",
	"Referer":"https://sites.google.com/site/whowasproject/",
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	"Accept-Language":"en;q=0.5",
	"Accept-Charset":"utf-8;q=0.7,*;q=0.7",
	"Connection":"close"
	}

dmbl=["www.socialrel8.com","newsnear-alpha.elasticbeanstalk.com","www.healpay.com","www.draftkings.com","r1.draftkings.com","r2.draftkings.com","r3.draftkings.com","www.brightedge.com","www.maydesigns.com","www.letstaggle.com"]
ipbl=[]
DEBUG=False
MAXDBLEN=20
CONTENT_LIMIT=512000
MAXLEN=8388608
go_worker_no=220

start_time=time.strftime('%Y-%m-%d')
str_time=time.strftime('%Y%m%d')
db_name="scanner_%s"%(str_time)
db_r_name="scanner_robot_%s"%(str_time)

"""
conn=MySQLdb.connect(host='localhost',user='root',passwd='w82776569',db='scan1')
cur=conn.cursor()
cur.execute("create table %s like scanner"%(db_name))
conn.commit()
cur.execute("create table %s like scanner_robot"%(db_r_name))
conn.commit()
cur.close()
conn.close()
"""
dbaddr="localhost"
dbuser="root"
pwd="w82776569"
dbn="scan1"

def init_db():
	global start_time
	global str_time
	global db_name
	global db_r_name
	
	start_time=time.strftime('%Y-%m-%d')
	str_time=time.strftime('%Y%m%d')
	db_name="scanner_%s"%(str_time)
	db_r_name="scanner_robot_%s"%(str_time)
	
	conn=MySQLdb.connect(host=dbaddr,user=dbuser,passwd=pwd,db=dbn)
	cur=conn.cursor()
	cur.execute("create table %s like scanner"%(db_name))
	conn.commit()
	cur.execute("create table %s like scanner_robot"%(db_r_name))
	conn.commit()
	cur.close()
	conn.close()

class UserDefinedException(Exception):
	class LongTimeout(Exception):
		args="LongTimeOut"

class MyTimeout(object):
	"""docstring for """
	def __init__(self, timeout):
		self.timeout=timeout
	def __get__(self, obj, type=None):
		return self.__class__(self.func.__get__(obj, type))

	def __call__(self, func):
		self.func=func
		
		def _handle_timeout(signum, frame,self=None):
			raise UserDefinedException.LongTimeout()

		def wrapper(*args, **kwargs):
			signal.signal(signal.SIGALRM, _handle_timeout)
			signal.alarm(self.timeout)
			try:
				result = self.func(*args, **kwargs)
			finally:
				signal.alarm(0)
			return result
		return wraps(self.func)(wrapper)

		#return decorator
	  
def open_port(ip,*ports):
		#print ports
		res=[]
		for port in ports:
			if sr1(IP(dst=ip)/TCP(dport=port, flags='S'), verbose=0, timeout=1):
				res.append(port)
		#print res
		return res

def scan_port(ip):
	res=[]
	res=open_port(ip, 80,443)
	if not res:
		res=open_port(ip, 22)
	return res
	

def worker(inq,no,sc=1):
	#print i,j
	c=Crawler()
	
	db=[]
	dbrb=[]
	dbl=0
	dbrbl=0
	for tip in iter(inq.get, 'STOP'):
		turl="http://"+tip
		res=[]
		fetch_flag=1
		try:
			if sc==1:
				try:
					res=scan_port(tip)
				except:
					continue
				if not res:
					continue
				if 80 in res:
					pass
				elif 443 in res:
					turl="https://"+tip
				else:
					fetch_flag=0
			
			rcode=""
			rheader=""
			content=""
			turl_r=turl+"/robots.txt"
			rbflag=False
			rbcontent=""
			rtt=""
			rbrtt=""
			if fetch_flag==1:
				try:
					rbflag,rbcontent,rbrtt=c.get_robot(turl_r)
					if rbcontent:
						rbcontent=unicode(rbcontent,errors='ignore').encode('utf-8')
					dbrb.append((tip,rbcontent,str(int(time.time())),str(rbrtt)))
					dbrbl=dbrbl+1
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
					content="ROOBOT"
			if content:
				content=unicode(content,errors='ignore').encode('utf-8')
			rport=sorted([str(v) for v in res])
			rport="#".join(rport)
			db.append((tip,rport,rcode,str(rheader),content,str(int(time.time())), str(rtt)))
			dbl=dbl+1

			if dbl==MAXDBLEN:
				conn=MySQLdb.connect(host=dbaddr,user=dbuser,passwd=pwd,db=dbn)
				cur=conn.cursor()
				cur.executemany("INSERT INTO "+db_name+"(ip,port,code,header,content,time,rtt) VALUES (%s,%s,%s,%s,%s,%s,%s)",db)
				conn.commit()
				cur.close()
				conn.close()
				db=[]
				dbl=0
			if dbrbl==MAXDBLEN:
				conn=MySQLdb.connect(host=dbaddr,user=dbuser,passwd=pwd,db=dbn)
				cur=conn.cursor()
				cur.executemany("INSERT INTO "+db_r_name+"(ip,content,time,rtt) VALUES (%s,%s,%s,%s)",dbrb)
				conn.commit()
				cur.close()
				conn.close()
				dbrb=[]
				dbrbl=0
		except:
			f=open("err.log","a")
			f.write("unknown:"+tip+"\n")
			f.close()
			pass
	conn=MySQLdb.connect(host=dbaddr,user=dbuser,passwd=pwd,db=dbn)
	cur=conn.cursor()
	cur.executemany("INSERT INTO "+db_name+"(ip,port,code,header,content,time,rtt) VALUES (%s,%s,%s,%s,%s,%s,%s)",db)
	conn.commit()
	cur.close()
	conn.close()
	db=[]
	dbl=0
	conn=MySQLdb.connect(host=dbaddr,user=dbuser,passwd=pwd,db=dbn)
	cur=conn.cursor()
	cur.executemany("INSERT INTO "+db_r_name+"(ip,content,time,rtt) VALUES (%s,%s,%s,%s)",dbrb)
	conn.commit()
	cur.close()
	conn.close()
	dbrb=[]
	dbrbl=0
	print no,"worker finish"
	


class Manager(object):
	"""docstring for Manager"""
	def __init__(self):
		self.inq=multiprocessing.Queue()
		self.pool=[]
		self.level=0


	def add_worker(self,func,no,sc):
		p=multiprocessing.Process(target=func, args=(self.inq,no,sc))
		self.pool.append(p)
		p.daemon = True
		p.start()


	def run_manger(self,no):
		stop_flag=0
		work_no=no
		while True:
			if stop_flag>=work_no:
				for i in range(work_no):
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
	"""docstring for """
	def __init__(self):
		self.timeout=10
		self.type_filter=['application/','audio/','image/','video/']
		#self.file_filter=['.avi','.mp3','.xml','.txt','.pdf','.wmv','.flac','.ape','.mp4','.jpg','.css','.jpeg','.bmp','.png','.as','.gif','.ico','.zip','.exe','.dmg','.rar']
		pass

	def get_header(self,url,verf=False):
		url=url
		history={}
		run_flag=True
		count=1
		try:
			r=requests.get(url,allow_redirects=True,stream=True,verify=verf,headers=header,timeout=self.timeout)
		except (requests.exceptions.SSLError,requests.exceptions.ConnectionError,UserDefinedException.LongTimeout,requests.exceptions.TooManyRedirects,requests.exceptions.HTTPError,requests.exceptions.Timeout) as e:
			#print "[EXCEPTION]",url,e.args
			return False,str(e.args)[0:15],False,False,False
		
		return True,r,r.status_code,dict(**r.headers),r.elapsed.total_seconds()

	@MyTimeout(12)
	def get_content(self,url):

		flag,r,rcode,rheader,rtt=self.get_header(url)
		if not flag:
			return flag,r,rcode,rheader,rtt
		else:
			#if r.url in dmbl:
				
			if rheader.has_key('content-length'):
				if int(rheader['content-length']) >=MAXLEN:
					return False,"TargetSizeTooLarge",rcode,rheader,rtt

			if rheader.has_key('content-type'):
				for ft in self.type_filter:
					if rheader['content-type'].find(ft)!=-1:
						return False,"TargetTypeFiltered",rcode,rheader,rtt
			try:
				content=r.content[0:CONTENT_LIMIT]
			except:
				return False,"UnexceptedError",rcode,rheader,rtt
				
			return True,content,rcode,rheader,rtt

	@MyTimeout(12)
	def get_robot(self,url):
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


def go(fin,sc):
	init_db()
	m=Manager()
	ipbl=[]
	for i in range(0,go_worker_no):
		m.add_worker(worker,i,sc)
	for d in dmbl:
		ipbl=ipbl+[v.strip("\n") for v in os.popen("dig +short %s"%(d)).readlines()]
	ipbl=ipbl+[v.strip("\n") for v in open("blacklist").readlines()]
	print ipbl
	#sys.exit()
	for i in open(fin):
		ip=i.strip("\n")
		if ip in ipbl:
			print ip,"in bl"
			continue
		m.inq.put(ip)
	
	m.run_manger(go_worker_no)
	m.wait()


def test():
	#url="http://54.232.112.62"
	#url="http://54.243.166.47"
	#url="http://www.facebook.com\\/l.php?u=http\\u00253A\\u00252F\\u00252Fbit.ly\\u00252F1as3BOz&amp;h=BAQGr-zcD&amp;s=1&quot;)"
	
	c=Crawler()
	url="http://54.245.97.184"
	url="http://54.245.231.247"
	print c.get_content(url)

	
if __name__ == '__main__':
	#url="http://54.245.231.247"
	print "start work"
	go("ec2_ip_mar.li",1)
	#go("ec2_ip_mar.li",1)
	#go("ec2_ip_mar.li",1)
	#go("ec2_ip_mar.li",1)
	#go("ec2_ip_mar.li",1)
	#go("ec2_ip_mar.li",1)
	#go("ec2_ip_mar.li",1)
	#go("ec2_ip_mar.li",1)
	#go("ip_redo","zmap_finish",0)
	#t=time.strftime('%Y-%m-%d',time.localtime(time.time()))
	#os.popen("cat crawl_finish zmap_finish > all_"+str(t)+".res")
	#os.popen("rm ip_todo ip_redo crawl_finish zmap_finish zmap_out")
	#test()




