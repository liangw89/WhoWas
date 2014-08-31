import MySQLdb,re
from hashes.simhash import simhash
import sys


conn=sqldb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PWD,db=DB_NAME)

def get_record_no(tb):
	"""
	Returns: the total number of useful records in a table
	"""
	sql="select count(*) from %s where code !='' and code !='0' and content!='ROBOT'"%(tb)
	buff=run_sql_with_return(sql)
	return buff[0][0]

def get_query_no(tb,record_no,page_no):
	"""
	:param tb: targt table
	:param record_no: total number of records in the target table
	:param page_no : the number of records feteched in a query.
	Each query will be fetch many records.
	Returns: the number of queries will be issued 
	"""
	return record_no/page_no+1

def get_record(tb,offset,page_no):
	"""
	The Get a set of records on a given "page". 
	Each page contain the same number of records (except the last one).
	:param tb: targt table
	:param offset: the index of the first record on a given page
	:param page_no : the number of records feteched in a query.
	"""
	sql="select ip,code,time,header,content from %s where code !='' and code !='0' and content!='ROBOT' limit %s,%s"%(tb,offset,page_no)
	return run_sql_with_return(sql)

def get_feature_from_header(header):
	"""
	Generate features from a HTTP header
	Returns: a dict contains features, format is:
			<name_of_feature>:value_of_feature
	"""
	feature_dict={}
	try:
		header=eval(header)
	except:
		feature_dict["hlen"]=0
		feature_dict["hfield"]=""
		feature_dict["hserver"]=""
		feature_dict["hstr"]=""
		return feature_dict
	feature_dict["hlen"]=len(header.keys())
	if "server" in header:
		feature_dict["hserver"]=header["server"]
	else:
		feature_dict["hserver"]=""
	tk=header.keys()
	tk.sort()
	feature_dict["hfield"]="#".join(tk)
	feature_dict["hstr"]=str(header)
	return feature_dict

def get_feature_from_content(content):
	"""
	Generate features from a HTTP content
	Returns: a dict contains features, format is:
			<name_of_feature>:value_of_feature
	"""
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

	feature_dict["ctitle"]=re.findall("<title.*?\/title>",content)
	feature_dict["ckws"]=re.findall('(?<=<meta name="keywords" content=").*(?=\/>)',content)
	feature_dict["ctmpl"]=re.findall('(?<=<meta name="generator" content=").*(?=\/>)',content)
	feature_dict["gid"]=re.findall("UA-\d{5,10}-\d{1,4}",content)
	feature_dict["dm"]=re.findall("(?<=_gaq.push\(\['_setDomainName'),.*(?=\]\);)",content)

	for k in feature_dict:
		feature_dict[k]="" if not feature_dict[k] else feature_dict[k][0]

	feature_dict["chash"]=str(simhash(content))
	content="".join(content.split())
	feature_dict["clen"]=len(content)
	return feature_dict

def get_record_feature(ip,code,tm,header,content):
	"""
	Generate features from a record
	Returns: a dict contains features, format is:
			<name_of_feature>:value_of_feature
	"""
	d1=get_feature_from_header(header)
	d2=get_feature_from_content(content)
	d=dict(d1,**d2)
	d=(ip,code,tm,d["hlen"],d["hserver"],d["hfield"],d["hstr"],d["ctitle"],d["ckws"],d["ctmpl"],d["gid"],d["dm"],d["chash"],d["clen"])
	return d

def get_all_feature(src_tb, dst_tb):
	"""
	Generate features from all records in the src table, 
	and store them in the dst table
	"""
	page_no=5000
	record_no=get_record_no(src_tb)
	query_no=get_query_no(src_tb,record_no,page_no)
	offset=0
	for i in xrange(query_no):
		offset=i*page_no
		tmp=get_record(src_tb,offset,page_no)
		param=[]
		for t in tmp:
			param.append(get_record_feature(t[0],t[1],t[2],t[3],t[4]))
		sql="insert into "+dst_tb+" values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		run_sql_bulk_no_return(sql,param,conn)

