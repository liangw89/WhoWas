import time
from datetime import datetime
import MySQLdb,re
import sys,os
import cPickle,ipaddr
from cluster import *
import os,math
import numpy as np
from numpy import arange,array,ones,linalg

def mse(data):
        l=len(data)
        xi=arange(0,l)
        A=array([xi,ones(l)])
        y=data
        w = linalg.lstsq(A.T,y)[0]
        predicts= w[0]*xi+w[1]
        return  np.sqrt(((predicts - y) ** 2).mean())

def cutoff(data,c,b):
        L=data[0:c]
        R=data[c:]
        #print data,c,L,R
        return float(c)/b*mse(L)+float(b-c)/b*mse(R)

def Lmethod(data):
        b=len(data)
        tmp=cutoff(data,1,b)
        m=0
        #print "data",data
        for c in xrange(1,b):
                r=cutoff(data,c,b)
                if r<=tmp:
                        m=c
                        tmp=r
        return m

def find_best(data):
        b=len(data)
        c=b
        lk=b
        ck=b
        #print "init",ck,lk,c,data[:c]
        while 1:
                lk=ck
                ck=Lmethod(data[:c])
                c=ck*2
                #print ck,lk,c
                if ck>=lk:
                        break
        based=data[10]
        low=data[ck+1]
        high=data[ck-1]
        if ck>=10:
                if high==based:
                        return 10,based
		if (high==data[ck]+1) and (low==data[ck]-1):
                        return ck-1,high
		if ck>20:
			return ck-1,high
		else:
			return ck,data[ck]
        else:
                if based<low:
                        return 10,based
                return ck+1,low

def hamming_distance(h1,h2,b):
    x = (h1 ^ h2) & ((1 << b) - 1)
    tot = 0
    while x:
        tot += 1
        x &= x-1
    return tot

def text_sim_score(h1,h2,b=96):
    return 100*float(hamming_distance(h1,h2,b)) / b

def text_sim(h1,h2,thres):
        dis=text_sim_score(h1, h2)
        if dis<=thres:
                return True
        return False

def text_cluster(st_list,thres):
        tmp={}
        clus={}
        for k in st_list:
                tmp[k]=0

        while len(tmp)!=0:
                #print len(tmp)
                #tmp.sort()
                st=tmp.keys()[0]
                clus[st]=[st]
                tmp.pop(st)
                keys=tmp.keys()
                for v in keys:
                        if text_sim(st, v,thres):
                                tmp.pop(v)
                                clus[st].append(v)
        if 0 in clus:
                clus.pop(0)
	out=[]
	for k in clus:
		out.append(clus[k])
        return out

def clus_2(st,ed,no,clus_1):
	#f=open("clus_1.db")
	#clus_1=cPickle.load(f)
	#f.close()
	res={}
	c=0
	for k in clus_1.keys()[st:ed]:
		c=c+1
		its=clus_1[k]
		tmp={}
		for i in its:
			h=int(i[2])
			if h in tmp:
				tmp[h].append((i[0],i[1]))
			else:
				tmp[h]=[(i[0],i[1])]
		if len(tmp)==1:
			tmp_k=tmp.keys()[0]
			new_k=k+(tmp_k,)
			res[new_k]=tmp[tmp_k]
		else:
			data={}
                        index={}
			dlen=len(tmp)
			if dlen<800:
				cl = HierarchicalClustering(tmp.keys(),text_sim_score)
                        for i in range(1,50):
				if dlen>=800:
                                	d=text_cluster(tmp.keys(),i)
                                else:
					d=cl.getlevel(i)
				data[i]=len(d)
                                index[len(d)]=i
                        #print data.values()
			m,v=find_best(data.values())
			#print m,v,index[v]
			if dlen>=800:
                        	clus=text_cluster(tmp.keys(),index[v])
			else:
				clus=cl.getlevel(index[v])
			for tmp_cls in clus:
				new_k=k+(tmp_cls[0],)
				tgs=[]
				for tmp_kk in tmp_cls:
					tgs+=tmp[tmp_kk]
				res[new_k]=tgs	
	f=open("clus_2_%s.db"%(no),"w")
	cPickle.dump(res,f)
	f.close()

def cluster_no():
        res=[]
        out={}
        for i in range(0,5):
                r=cPickle.load(open("clus_2_%s.db"%(i)))
                res+=r.keys()

        for x in xrange(len(res)):
                out[res[x]]=x
        f=open("clus_no.db","w")
        cPickle.dump(out,f)
        f.close()

def reverse_db():
        cno=cPickle.load(open("clus_no.db"))
        out={}
        for i in range(0,5):
                r=cPickle.load(open("clus_2_%s.db"%(i)))
                for k in r:
                        no=cno[k]
                        for it in r[k]:
                                out[it]=no
        f=open("clus_2.db","w")
        cPickle.dump(out,f)
        f.close()
#no_all=296864
#l=no_all/5+1
f=open("clus_1.db")
clus_1=cPickle.load(f)
f.close()
no_all=len(clus_1)
print "all",no_all
l=no_all/5+1
#clus_2(0,no_all,0,clus_1)
#sys.exit()
for i in xrange(5):
	st=i*l
	ed=(i+1)*l
	if ed>no_all-1:
		ed=no_all-1
	print st,ed,i
	clus_2(st,ed,i,clus_1)
	#break
#clus_2(0:10000)
cluster_no()
reverse_db()
