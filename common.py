try:
  import MySQLdb as sqldb
except:
  import pymysql as sqldb
import cPickle

def init_config():
	"""Configurations, read from config.ini"""
	global DB_HOST 
	global DB_USER
	global DB_PWD
	global DB_NAME

	global TB_BASE_TEMPLATE
	global TB_BASE_PREFIX
	global TB_ROBOT_TEMPLATE 
	global TB_ROBOT_PREFIX
	global TB_SUFFIX
	global TB_SQL
	global TB_BASE_NAME
	global TB_ROBOT_NAME
	

	global INPUT_FILE
	global WORKER_NO
	global CONTENT_LENGTH_LIMIT
	global MAX_CONTENT_LENGTH
	global RECORD_NO_LIMIT
	global BLACKIST_FILE
	global BLACLIST

	global HTTP_HEADER

	config = ConfigParser.ConfigParser()
	config.read('config.ini')

	DB_ADDR=config.get('DataBase','DB_ADDR')
	DB_USER=config.get('DataBase','DB_USER')
	DB_PWD=config.get('DataBase','DB_PWD')
	DB_NAME=config.get('DataBase','DB_NAME')

	TB_BASE_TEMPLATE=config.get('DataBase','TB_BASE_TEMPLATE')
	TB_BASE_PREFIX=config.get('DataBase','TB_BASE_PREFIX')
	TB_ROBOT_TEMPLATE=config.get('DataBase','TB_ROBOT_TEMPLATE')
	TB_ROBOT_PREFIX=config.get('DataBase','TB_ROBOT_PREFIX')	

	INPUT_FILE = config.get('Basic','INPUT_FILE')
	WORKER_NO=config.get('Basic','WORKER_NO')
	CONTENT_LENGTH_LIMIT=config.get('Basic','CONTENT_LENGTH_LIMIT')
	MAX_CONTENT_LENGTH=config.get('Basic','MAX_CONTENT_LENGTH')
	RECORD_NO_LIMIT=config.get('Basic','RECORD_NO_LIMIT')
	BLACKIST_FILE=config.get('Basic','BLACKIST_FILE')
	PROBE_DEFAULT_TIMEOUT= config.get('Basic','PROBE_DEFAULT_TIMEOUT')
	HTTP_DEFAULT_TIMEOUT=config.get('Basic','HTTP_DEFAULT_TIMEOUT')
	HTTP_LONG_TIMEOUT=config.get('Basic','HTTP_LONG_TIMEOUT')

	HTTP_HEADER={
	"User-Agent":"Mozilla/5.0 (X11; U; Linux i686)",
	"From":"admin@example.com",
	"Referer":"http://example.com",
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	"Accept-Language":"en;q=0.5",
	"Accept-Charset":"utf-8;q=0.7,*;q=0.7",
	"Connection":"close"
	}

	TB_SQL={}
	TB_SQL[TB_BASE_TEMPLATE]=(
	  "CREATE TABLE IF NOT EXISTS "+"`"+TB_BASE_TEMPLATE+"`"+" ("
	  "`tid` int(12) NOT NULL AUTO_INCREMENT,"
	  "`ip` varchar(64) DEFAULT NULL,"
	  "`port` varchar(64) DEFAULT NULL,"
	  "`code` varchar(64) DEFAULT NULL,"
	  "`header` text,"
	  "`content` text,"
	  "`time` varchar(64) DEFAULT NULL,"
	  "`rtt` varchar(64) NOT NULL,"
	  "PRIMARY KEY (`tid`),"
	  "KEY `ip` (`ip`),"
	  "KEY `time` (`time`),"
	  "KEY `iport` (`port`),"
	  "KEY `icode` (`code`),"
	  "KEY `rtt` (`rtt`)"
	  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1" )

	TB_SQL[TB_ROBOT_TEMPLATE]=(
	  "CREATE TABLE IF NOT EXISTS "+"`"+TB_ROBOT_TEMPLATE+"`"+" ("
	  "`tid` int(12) NOT NULL AUTO_INCREMENT,"
	  "`ip` varchar(64) DEFAULT NULL,"
	  "`content` text,"
	  "`time` varchar(64) DEFAULT NULL,"
	  "`rtt` varchar(64) NOT NULL,"
	  "PRIMARY KEY (`tid`),"
	  "KEY `ip` (`ip`),"
	  "KEY `time` (`time`),"
	  "KEY `rtt` (`rtt`)"
	  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1" )

	TB_SUFFIX=time.strftime('%Y%m%d%H%M')
	TB_BASE_NAME="%s%s"%(TB_BASE_PREFIX,TB_SUFFIX)
	TB_ROBOT_NAME="%s%s"%(TB_ROBOT_PREFIX,TB_SUFFIX)


def run_sql_no_return(sql,conn):
	"""
	Execute a SQL statement; no value returns
	"""
	cur=conn.cursor()
	try:
		cur.execute(sql)
		conn.commit()
	except Exception, e:
		print e #change to log
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
		print e #change to log
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

