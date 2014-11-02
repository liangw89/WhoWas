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
from config import *



class API(object):
    """docstring for API"""
    def __init__(self):
        super(API, self).__init__()
        self.conn=sqldb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PWD,db=DB_NAME)
        self.logger= logging.getLogger("logging")

    def query(self, sql):
        cur = self.conn.cursor()
        res=None
        try:
            cur.execute(sql)
            res = cur.fetchall()
        except Exception, e:
            self.logger.error("SQL ERROR: %s", e)
        cur.close()
        return res

    def get_all_tb_name(self):
        tmp=[v[0]  for v in self.query("SHOW TABLES", self.conn)]
        return tmp

    def find_tb_by_tm(self, tm):
        tb_prex = "%s%s" % (TB_BASE_PREFIX, tm.replace("-", "_"))
        tbs = sorted(get_all_tb_name(self.conn))
        tb = [v for v in tbs if v.startswith(tb_prex)][0]
        return tb

    def get_content(self, tb, ip):
        sql = "SELECT content FROM %s WHERE ip = '%s'" % (tb,ip)
        tmp = self.query(sql)
        return tmp

    def str_2_timestamp(self, tm_str, format):
        return int(time.mktime(datetime.strptime(tm_str, format).timetuple()))

    def get_all_simhash(self, feature_tb):
        sql = "SELECT DISTINCT(chash) FROM %s" % (feature_tb)
        tmp = [v[0] for v in self.query(sql)]
        return tmp

    def get_ip_match_conditions(self,tb,port=None, code=None, header=None, content=None, collected_after_tm=None, collected_before_tm=None, tm_foramt="%Y-%m-%d-%H"):
        """
        Get IP that match the given conditions from scanning table
        """
        sql = "SELECT ip FROM %s WHERE  1=1 " % (tb)
        sql = sql + "AND port = '%s' " % (port) if port else sql
        sql = sql + "AND code = '%s' " % (code) if code else sql
        sql = sql + "AND header like '%" + header + "%' " if header else sql
        sql = sql + "AND content like '%" + content + "%' " if content else sql
        sql = sql + "AND time >= '%s' " % (self.str_2_timestamp(collected_after_tm, tm_foramt)) if collected_after_tm else sql
        sql = sql + "AND time <= '%s' " % (self.str_2_timestamp(collected_before_tm, tm_foramt)) if collected_before_tm else sql
        print sql
        tmp=self.query(sql)
        return [v[0] for  v in tmp]

    def stat_ip_match_features(self, feature_tb, title=None, keyword=None, template=None, GID=None, server=None, simhash=None):
        """
        Get IP that match the given conditions from feature table
        """
        sql = "SELECT count(ip) FROM  %s WHERE  1=1 " % (feature_tb)
        sql = sql + "AND ctitle like '%" + title + "%' " if title else sql
        sql = sql + "AND ckws like '%" + keyword + "%' " if keyword else sql
        sql = sql + "AND ctmpl like '%" + template + "%' " if template else sql
        sql = sql + "AND gid like '%" + GID+"%' " if GID else sql
        sql = sql + "AND hserver like '%" + server + "%' " if server else sql
        sql = sql + "AND chash = '%s' " % (simhash) if simhash else sql
        tmp=self.query(sql)
        return tmp[0][0]

if __name__ == '__main__':
    a=API()
    print a.get_ip_match_conditions("example1_2014_11_01_16", header="test", collected_after_tm="2014-11-01-10", collected_before_tm="2014-11-01-20")
    print a.stat_ip_match_features("feature_2014_11_01_16",simhash="79228162514264337593543950335")
    print a.list_simhash("feature_2014_11_01_16")




