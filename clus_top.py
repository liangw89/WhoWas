import cPickle
import time
from datetime import datetime
import MySQLdb,re

host='localhost'
user='root'
passwd='root'
db='scan'
conn=MySQLdb.connect(host=host,user=user,passwd=passwd,db=db)

tm_tb=cPickle.load(open("tm_tb.db"))
def exec_sql(sql):
	cur=conn.cursor()
	cur.execute(sql)
	tmp=cur.fetchall()
	cur.close()
	return tmp

def grab_meta(tm):
	#tm='2013-11-02'
	#tb="scanner_"+tm.replace("-","")
	tb=tm_tb[tm]
	#sql="select count(ip) from %s where time='%s' "%(tb,tm)
	#t=exec_sql(sql)
	#count=t[0][0]
	#print count
	#no=count/50000+1
	res={}
	#for i in xrange(no):
	sql="select ip,chash,gid,ctitle,ctmpl,ckws,hserver from %s where time='%s' and ip in (select ip from ip_reg) "%(tb,tm)
	t=exec_sql(sql)
	for k in t:
		k1=(k[0],tm,k[1])
		k2=k[2:]
		if k2 in res:
			res[k2].append(k1)
		else:
			res[k2]=[k1]
	print tm,len(res)
	return res	

res={}
for tm in open("xindex.db"):
#for tm in ["2013-11-06\n","2013-11-08\n"]:	
	tm=tm.strip("\n")
	#res=grab_meta(tm)
	print tm
	f=open("%s.db"%(tm))
	r=cPickle.load(f)
	#f=open("%s.db"%(tm),"w")
	#cPickle.dump(res,f)
	f.close()
	#"""
	for k in r:
		if k in res:
			res[k]=res[k]+r[k]
		else:
			res[k]=r[k]
	#"""
#"""	
print len(res)
f=open("clus_1.db","w")
cPickle.dump(res,f)
f.close()
o=[]
for k in res:
	for i in res[k]:
		o.append("%s,%s\n"%(i[0],i[1]))
o.sort()
f=open("pair_get","w")
f.writelines(o)
f.close()
#"""
