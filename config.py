import time

#[DataBase]
DB_HOST = "localhost"
DB_USER = "root"
DB_PWD  = "root"
DB_NAME = "whowas"

TB_BASE_TEMPLATE = "example1"
TB_BASE_PREFIX = "example1_"
TB_ROBOT_TEMPLATE = "example2"
TB_ROBOT_PREFIX = "example2_"
TB_FEATURE_TEMPLATE = "feature"
TB_FEATURE_PREFIX = "feature_"
TB_SUFFIX=time.strftime('%Y_%m_%d_%H')

TB_BASE_NAME="%s%s"%(TB_BASE_PREFIX,TB_SUFFIX)
TB_ROBOT_NAME="%s%s"%(TB_ROBOT_PREFIX,TB_SUFFIX)
TB_FEATURE_NAME = "%s%s"%(TB_FEATURE_PREFIX,TB_SUFFIX)

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
  "`code` varchar(16) DEFAULT NULL,"
  "`content` text,"
  "`time` varchar(64) DEFAULT NULL,"
  "PRIMARY KEY (`tid`),"
  "KEY `ip` (`ip`),"
  "KEY `code` (`code`),"
  "KEY `time` (`time`)"
  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1" )

TB_SQL[TB_FEATURE_TEMPLATE]=(
  "CREATE TABLE IF NOT EXISTS "+"`"+TB_FEATURE_TEMPLATE+"`"+" ("
  "`ip` varchar(64) NOT NULL,"
  "`code` varchar(32) DEFAULT NULL,"
  "`time` varchar(64) NOT NULL,"
  "`hlen` int(64) DEFAULT NULL,"
  "`hserver` varchar(256) DEFAULT NULL,"
  "`hfield` varchar(2048) DEFAULT NULL,"
  "`hstr` varchar(4096) DEFAULT NULL,"
  "`ctitle` varchar(1024) DEFAULT NULL,"
  "`ckws` varchar(2048) DEFAULT NULL,"
  "`ctmpl` varchar(1024) DEFAULT NULL,"
  "`gid` varchar(128) DEFAULT NULL,"
  "`dm` varchar(1024) DEFAULT NULL,"
  "`chash` varchar(128) DEFAULT NULL,"
  "`clen` int(255) NOT NULL,"
  "PRIMARY KEY (`ip`,`time`),"
  "KEY `chash` (`chash`),"
  "KEY `gid` (`gid`),"
  "KEY `clen` (`clen`),"
  "KEY `hserver` (`hserver`(255)),"
  "KEY `hfield` (`hfield`(255)),"
  "KEY `hstr` (`hstr`(255)),"
  "KEY `ctitle` (`ctitle`(255)),"
  "KEY `ctmpl` (`ctmpl`(255)),"
  "KEY `code` (`code`)"
  ") ENGINE=InnoDB DEFAULT CHARSET=utf8;")



#[Basic]
# IP ranges of pubic cloud
INPUT_FILE = "test_input.csv"
# exclusion list
BLACKIST_FILE = "blacklist"
# no of procress
WORKER_NO= 20
# max length of content stored in DB
CONTENT_LENGTH_LIMIT=100000
# max accepted length of a content returned by target IP
MAX_CONTENT_LENGTH=1000000
# a worker will collect RECORD_NO_LIMIT number of contents and 
# submit to DB
RECORD_NO_LIMIT=1
# timeout
PROBE_DEFAULT_TIMEOUT=2
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


#install requests==2.3.0
#install logutils
#install pymysql
#install python-hashes
