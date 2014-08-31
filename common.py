try:
  import MySQLdb as sqldb
except:
  import pymysql as sqldb
import sys
import os
import cPickle
import time
from datetime import datetime
import re
from logger import *

logger= logging.getLogger("logging")
#logger.debug("Register guard %s,%s",nid,self.tb_guards[nid].__dict__)

def run_sql_no_return(sql,conn):
	"""
	Execute a SQL statement; no value returns
	"""
	cur=conn.cursor()
	try:
		cur.execute(sql)
		conn.commit()
	except Exception, e:
		logger.error("SQL ERROR: %s",e)
	cur.close()
	conn.close()

def run_sql_bulk_no_return(sql, param,conn):
	"""
	Execute a set of SQL statements; no values return
	"""
	cur=conn.cursor()
	try:
		cur.executemany(sql,param)
		conn.commit()
	except Exception, e:
		logger.error("SQL ERROR: %s",e)
	cur.close()
	conn.close()

def run_sql_with_return(sql,conn):
	"""
	Execute a SQL statement and get return values
	"""
	cur=conn.cursor()
	cur.execute(sql)
	res=cur.fetchall()
	cur.close()
	return res

def export_res(res,dst_file):
	f=open(dst_file,"w")
	cPickle.dump(res,f)
	f.close()

def import_res(src_file):
	return cPickle.load(open(src_file))

