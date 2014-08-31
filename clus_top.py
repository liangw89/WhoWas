from datetime import datetime
from config import *
from common import *


conn=sqldb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PWD,db=DB_NAME)

def get_top_cluster_tb_tm(tb,tm):
	"""
	We assume the feature records may be stored in multiple tables, this function 
	generate the top-level clusters at a given time.
	:param tb: the table where the feature records from time "tm" are being stored. 
	:param tm: the time where the target feature records were collected.   
	Returns: A dict stores the top-level clusters, the dict looks like:
		<GID,CTITLE,CTMPLE,CKWS,HSERVER>: [<IP_1,TIME,CHASH_1>,... ,<IP_N,TIME,CHASH_N>] 
	"""
	res={}
	#ip_reg is where stores the target IP address.
	sql="select ip,chash,gid,ctitle,ctmpl,ckws,hserver from %s where time='%s' and ip in (select ip from ip_reg) "%(tb,tm)
	buff=run_sql_with_return(sql,conn)
	for k in buff:
		k1=(k[0],tm,k[1])
		k2=k[2:]
		if k2 in res:
			res[k2].append(k1)
		else:
			res[k2]=[k1]
	return res

def merge_top_clusters(target_clus,res_clus):
	"""
	Merge target_clus into res_clus.
	Returns: res_clus. After merging all top-level clusters the dict would looks like:
		<GID,CTITLE,CTMPLE,CKWS,HSERVER>: [<IP_1,TIME_1,CHASH_1>,... ,<IP_N,TIME_N,CHASH_N>] 
	"""
	for k in target_clus:
		res[k]=res[k]+target_clus[k] if k in res else target_clus[k]
	return res_clus

if __name__ == '__main__':
	pass

	"""
	usage example:
	res_clus={}
	for tb,tm in [("test0","2012-12-21"),("test1","2012-12-22")]
		clus=get_top_cluster_tb_tm(tb,tm)
		res_clus=merge_top_clusters(clus,res_clus)
	export_res(res_clus)
	"""




