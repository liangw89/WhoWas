import MySQLdb,re
from hashes.simhash import simhash
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

def feature_from_header(h):
	feature_dict={}
	try:
		h=eval(h)
	except:
		feature_dict["hlen"]=0
		feature_dict["hfield"]=""
		feature_dict["hserver"]=""
		feature_dict["hstr"]=""
		return feature_dict
	feature_dict["hlen"]=len(h.keys())
	if "server" in h:
		feature_dict["hserver"]=h["server"]
	else:
		feature_dict["hserver"]=""
	tk=h.keys()
	tk.sort()
	feature_dict["hfield"]="#".join(tk)
	feature_dict["hstr"]=str(h)
	return feature_dict

def feature_from_content(c):
	feature_dict={}
	"""
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
	"""

	feature_dict["ctitle"]=re.findall("<title.*?\/title>",c)
	feature_dict["ckws"]=re.findall('(?<=<meta name="keywords" content=").*(?=\/>)',c)
	feature_dict["ctmpl"]=re.findall('(?<=<meta name="generator" content=").*(?=\/>)',c)
	feature_dict["gid"]=re.findall("UA-\d{5,10}-\d{1,4}",c)
	feature_dict["dm"]=re.findall("(?<=_gaq.push\(\['_setDomainName'),.*(?=\]\);)",c)

	for k in feature_dict:
		feature_dict[k]="" if not feature_dict[k] else feature_dict[k][0]

	feature_dict["chash"]=str(simhash(c))
	c="".join(c.split())
	feature_dict["clen"]=len(c)
	return feature_dict

def ip_sig(ip,code,tm,h,c):
	d1=feature_from_header(h)
	d2=feature_from_content(c)
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

