import MySQLdb

TABLES={}
TABLES['scanner']=(
  "CREATE TABLE IF NOT EXISTS `scanner` ("
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

TABLES['scanner_robot']=(
  "CREATE TABLE IF NOT EXISTS `scanner_robot` ("
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