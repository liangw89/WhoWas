import MySQLdb,re
from hashes.simhash import simhash
import sys


conn=sqldb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PWD,db=DB_NAME)
def get_record_no(tb):
	sql="select count(*) from %s where code !='' and code !='0' and content!='ROBOT'"%(tb)
	buff=run_sql_with_return(sql)
	return buff[0][0]

def get_query_no(tb,record_no,page_no):
	return record_no/page_no+1

def get_record(tb,offset,page_no):
	sql="select ip,code,time,header,content from %s where code !='' and code !='0' and content!='ROBOT' limit %s,%s"%(tb,offset,page_no)
	return run_sql_with_return(sql)

def get_feature_from_header(h):
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

def get_feature_from_content(c):
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

def get_record_feature(ip,code,tm,h,c):
	d1=get_feature_from_header(h)
	d2=get_feature_from_content(c)
	d=dict(d1,**d2)
	d=(ip,code,tm,d["hlen"],d["hserver"],d["hfield"],d["hstr"],d["ctitle"],d["ckws"],d["ctmpl"],d["gid"],d["dm"],d["chash"],d["clen"])
	return d

def get_all_feature(tb):
	page_no=5000
	record_no=get_record_no(tb)
	query_no=get_query_no(tb,record_no,page_no)
	offset=0
	for i in xrange(query_no):
		offset=i*page_no
		tmp=get_record(tb,offset,page_no)
		param=[]
		for t in tmp:
			param.append(get_record_feature(t[0],t[1],t[2],t[3],t[4]))
		sql="insert into ip_sig_st values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		run_sql_bulk_no_return(sql,param,conn)

