import time

#[DataBase]
DB_HOST = "localhost"
DB_USER = "root"
DB_PWD  = "xxx"
DB_NAME = "xxx"

TB_BASE_TEMPLATE = "example1"
TB_BASE_PREFIX = "example1_"
TB_ROBOT_TEMPLATE = "example2"
TB_ROBOT_PREFIX = "example2_"

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


#[Basic]
INPUT_FILE = "ip.csv"
BLACKIST_FILE = "blacklist"
WORKER_NO= 10
CONTENT_LENGTH_LIMIT=100
MAX_CONTENT_LENGTH=100
RECORD_NO_LIMIT=20
PROBE_DEFAULT_TIMEOUT=1
HTTP_DEFAULT_TIMEOUT=10
HTTP_LONG_TIMEOUT=20


HTTP_HEADER={
"User-Agent":"Mozilla/5.0 (X11; U; Linux i686)",
"From":"admin@example.com",
"Referer":"http://example.com",
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language":"en;q=0.5",
"Accept-Charset":"utf-8;q=0.7,*;q=0.7",
"Connection":"close"
}


