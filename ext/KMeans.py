import math
import numpy as np
import collections
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import random
from operator import itemgetter

def KMeans(Graph,K):
  #Graph = G.copy()
  #Graph.remove_node(0)
  oldknodes = random.sample(Graph.nodes(),K)
  newknodes = random.sample(Graph.nodes(),K)
  clusters = {}
  FirstTimeOldNewSame = True #Incase when oldknodes and newknodes are same
  result = 0
  
  while result != 1 or FirstTimeOldNewSame:  
    oldknodes = newknodes
    #print "oldknodes = %s"%newknodes
    clusters = ClusterNodes(Graph,newknodes)
    #print clusters
    newknodes = ReevaluateClusters(Graph, clusters)
    #print "newknodes=%s"%newknodes
    FirstTimeOldNewSame = False
    result = HasConverged(oldknodes,newknodes,clusters,Graph)       
    if result == 2:
      newknodes = random.sample(Graph.nodes(),K) 
  return clusters  

def HasConverged(oldknodes,newknodes,clusters, Graph):  
  if set(oldknodes) != set(newknodes):
    return 0 #False
  if clusters:
    for nodes in clusters.itervalues():      
      if not nx.is_connected(Graph.subgraph(nodes)):
        #print 'Disconnected Graph'      
        return 2 #False, select random nodes again      
  return 1 #True
  
  
def ReevaluateClusters(Graph, clusters):
  newknodes = []
  for cluster, nodes in clusters.items():
    mindist = 999999
    minnode = -1
    for node in nodes:
      dist = sum(nx.shortest_path_length(Graph,node,n) for n in nodes)
      #print "node=%d"%node, " dist=%d"%dist
      if mindist > dist:
        mindist = dist
        minnode = node
    newknodes.append(minnode)
  return newknodes

#This method will select the cluster with min distance and min node value  
def ClusterNodes1(Graph,clusternodes):
  clusters = {}
  clusternodes.sort()
  for n in clusternodes:
    clusters[n] = []  
  for node in Graph.nodes():
    dist = []
    for cluster in clusternodes:
      dist.append([cluster,nx.shortest_path_length(Graph,node,cluster)])   
    MinClus = min(dist,key=itemgetter(1))[0]
    clusters[MinClus].append(node)    
  return clusters
  
  
def ClusterNodes(Graph,clusternodes):
  clusters = {}
  clusternodes.sort()
  for n in clusternodes:
    clusters[n] = []
  
  for node in Graph.nodes():
    dist = []
    for cluster in clusternodes:
      dist.append([cluster,nx.shortest_path_length(Graph,node,cluster)])
    #print "node = %d"%node, " dist = %s"%dist    
    MinDistance = min(dist,key=itemgetter(1))[1]
    MinDistClusters = [item[0] for item in dist if item[1] == MinDistance]
    #print "MinDistClusters=%s"%MinDistClusters
    if len(MinDistClusters) > 1:      
      #This will sort the dict on length of value(list) and then on value of key.
      #So clusters with min nodes is selected, then cluster with min number is selected
      MinCountClus = sorted([[clus, len(nodes)] for clus, nodes in clusters.iteritems() if clus in MinDistClusters],key=itemgetter(1,0))[0][0]
    else:
      MinCountClus = MinDistClusters[0]
    clusters[MinCountClus].append(node)
    #print "cluster=%s"%clusters
    
  return clusters
 
def main():   
  G = nx.Graph()
  labels = {}
  nodes = 10
    
  for x in range(0,nodes):
    G.add_node(x)
    labels[x]='$'+str(x)+'$'

  mat = np.loadtxt("Topologies/"+str(nodes)+"-2.txt",delimiter="\t")  
  for i in mat:
    G.add_edges_from([(int(i[0]),int(i[1])), (int(i[1]),int(i[0]))])  

  mat = None
  clusters = {}
  clusters =  KMeans(G,2)
  print clusters

  '''
  plt.figure(figsize=(24,24))
  pox=nx.spring_layout(G)
  nx.draw_networkx(G,pox,labels)
  plt.show()
  

  for clus, nodes in clusters.items():
    #print clus, nodes
    #plt.figure(figsize=(24,24))
    H = G.subgraph(nodes)
    #pox=nx.spring_layout(H)
    #nx.draw_networkx(H,pox,labels)
    #plt.show()'''

if __name__ == '__main__':  
  main()
