import MySQLdb,re
from hashes.simhash import simhash
#import nilsimsa
#from hashes.simhash import simhash
#from nilsimsa import *
import sys
db_name=sys.argv[1]
#db_name="scanner_20130930"
conn=MySQLdb.connect(host='111',user='11',passwd='111',db="11")
sql="select count(*) from %s where code !='' and code !='0'"%(db_name)
cur=conn.cursor()
cur.execute(sql)
rd_no=cur.fetchall()[0][0]
page_no=5000
query_no=rd_no/page_no+1
print query_no,rd_no
def grab_content(row):
	sql="select ip,code,time,header,content from %s where code !='' and code !='0' limit %s,%s"%(db_name,row,page_no)
	cur=conn.cursor()
	cur.execute(sql)
	a=cur.fetchall()
	cur.close()
	return a

def header_sig(h):
	sig={}
	try:
		h=eval(h)
	except:
		sig["hlen"]=0
		sig["hfield"]=""
		sig["hserver"]=""
		sig["hstr"]=""
		return sig
	sig["hlen"]=len(h.keys())
	if "server" in h:
		sig["hserver"]=h["server"]
	else:
		sig["hserver"]=""
	tk=h.keys()
	tk.sort()
	sig["hfield"]="#".join(tk)
	sig["hstr"]=str(h)
	return sig

def content_sig(c):
	sig={}
	tl=re.findall("<title.*?\/title>",c)
	kw=re.findall('(?<=<meta name="keywords" content=").*(?=\/>)',c)
	tmpl=re.findall('(?<=<meta name="generator" content=").*(?=\/>)',c)
	uid=re.findall("UA-\d{5,10}-\d{1,4}",c)
	dm=re.findall("(?<=_gaq.push\(\['_setDomainName'),.*(?=\]\);)",c)
	tl="" if tl==[] else tl[0]
	kw="" if kw==[] else kw[0]
	tmpl="" if tmpl==[] else tmpl[0]
	uid="" if uid==[] else uid[0]
	dm="" if dm==[] else dm[0]
	
	sig["ctitle"]=tl
	sig["ckws"]=kw
	sig["ctmpl"]=tmpl
	sig["gid"]=uid
	sig["dm"]=dm
	sig["chash"]=str(simhash(c))
	c="".join(c.split())
	sig["clen"]=len(c)
	return sig

def ip_sig(ip,code,tm,h,c):
	d1=header_sig(h)
	d2=content_sig(c)
	d=dict(d1,**d2)
	d=(ip,code,tm,d["hlen"],d["hserver"],d["hfield"],d["hstr"],d["ctitle"],d["ckws"],d["ctmpl"],d["gid"],d["dm"],d["chash"],d["clen"])
	return d


start=0
for i in xrange(query_no):
	start=i*page_no
	print "begin offset",start
	tmp=grab_content(start)
	res=[]
	for t in tmp:
		res.append(ip_sig(t[0],t[1],t[2],t[3],t[4]))
	sql="insert into ip_sig_st values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	cur=conn.cursor()
	cur.executemany(sql,res)
	conn.commit()
	cur.close()



conn.close()
"""
t1=nilsimsa.Nilsimsa(c[0]).hexdigest()
t2=nilsimsa.Nilsimsa(c[1]).hexdigest()
print compare_hexdigests(t1,t2)
t1=simhash(c[0],hashbits=128)
t2=simhash(c[1],hashbits=128)
print t1.hex()
print t1.similarity(t2)
"""
