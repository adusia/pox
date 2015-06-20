import math
import numpy as np
import collections
import networkx as nx
#from networkx import Graph
import matplotlib.pyplot as plt
from dijkstras import Graph
from collections import deque
from termcolor import colored
import copy
import random

class MinCut:
  
  def __init__(self, Graph):  
    self.Graph = Graph
    self.numberofnodes = self.Graph.number_of_nodes()   
    self.G1 = []
    self.G2 = []
    self.Costs = {}
    self.T = 0
    self.clusters = {}
    #self.KL()
    #return self.clusters
    
  def Clus(self):
    H1 = self.Graph.subgraph(self.G1)
    mindist = 999999
    minnode = -1
    for node in self.G1:     
      dist = sum(nx.shortest_path_length(H1,node,n) for n in self.G1)
      if mindist > dist:
        mindist = dist
        minnode = node
    self.clusters[minnode] = self.G1     

    H2 = self.Graph.subgraph(self.G2)
    mindist = 999999
    minnode = -1
    for node in self.G2:     
      dist = sum(nx.shortest_path_length(H2,node,n) for n in self.G2)
      if mindist > dist:
        mindist = dist
        minnode = node
    self.clusters[minnode] = self.G2

    return
  
  def KL(self):
    self.RandomDivision()
    #print "G1=%s"%self.G1        
    #print "G2=%s"%self.G2    
    for node in self.G1:
      self.T += self.ExternalCost(node)
    #print "T=%d"%self.T
    
    while True:
      newT = 0
      for node in range(0,self.numberofnodes):
        self.Costs[node] = (self.ExternalCost(node) - self.InternalCost(node))
      #print "Costs=%s "%self.Costs     
      
      GainPairs = self.GainSwaps()
      
      #print "GainPairs = %s"%GainPairs
      k, MaxGain  = self.MaxGainPairs(GainPairs)
      #MaxGain, MaxPairs = self.MaxGainPairs(GainPairs)
      #for i in range(0,k):
        #MaxPairs.append(GainPairs[i])
        
      #print "Gain=%d"%MaxGain, " ,Swaps=%s"%GainPairs[0:k+1]
      if MaxGain > 0:
        for Pair in GainPairs[0:k+1]: #(5, [['4-2', 3], ['6-3', 1], ['8-0', 1]])
          x,y = Pair[0].split("-")
          self.G1.remove(int(x))
          self.G2.append(int(x))        
          self.G2.remove(int(y))
          self.G1.append(int(y))
        #print "G1=%s"%self.G1        
        #print "G2=%s"%self.G2 
       
        for node in self.G1:
          newT += self.ExternalCost(node)  
        #print "newT=%d"%newT
        self.T -= MaxGain
        #print "T=%d"%self.T      
      else:
        #print "MinCut=%d"%self.T
        #print "G1=%s"%self.G1,", G2=%s"%self.G2 
        self.Clus()
        return self.clusters
        
  def MaxGainPairs(self,GainPairs):
    Sum = []
    Sum.append(GainPairs[0][1])

    for i in range (1, self.numberofnodes/2):
      Sum.append(Sum[i-1]+GainPairs[i][1])
    
    #print Sum
    return Sum.index(max(Sum)), max(Sum)
     
  def GainSwaps(self):
    GainPairs = []
    UnMarkedNodesG1 = list(self.G1)
    UnMarkedNodesG2 = list(self.G2)
    
    while len(UnMarkedNodesG1) > 0:
      Gain = {}
      for x in UnMarkedNodesG1:
        for y in UnMarkedNodesG2:
          Gain[str(x)+"-"+str(y)] = self.Costs[x] + self.Costs[y] 
          if self.Graph.has_edge(x,y):
            Gain[str(x)+"-"+str(y)] -= 2
      #print "Gain= %s "%Gain
      MaxGain = max(val for val in Gain.itervalues())
      #print "MaxGain=%d"%MaxGain
      Pair, Gain = [[key, value] for key, value in Gain.items() if value == MaxGain][0]
      #print  "Pair=%s"%Pair, ", Gain=%d" % Gain
      GainPairs.append([Pair, Gain])
      i,j = Pair.split("-")
      i = int(i)
      j = int(j)
      UnMarkedNodesG1.remove(i)
      UnMarkedNodesG2.remove(j)
      self.Costs.pop(i,None)
      self.Costs.pop(j,None) 

      for node in UnMarkedNodesG1:
        if self.Graph.has_edge(node,i):
          self.Costs[node] += 2
        if self.Graph.has_edge(node,j):
          self.Costs[node] -= 2
          
      for node in UnMarkedNodesG2:
        if self.Graph.has_edge(node,i):
          self.Costs[node] -= 2
        if self.Graph.has_edge(node,j):
          self.Costs[node] += 2
        
      #print "Costs = %s"%self.Costs 
      
      #GainPairs.sort(key=lambda x:x[1], reverse=True)
      
    return GainPairs
  
  def RandomDivision(self):
    LstOfAllNodes = self.Graph.nodes()
    self.G1 = random.sample(LstOfAllNodes,self.numberofnodes/2)
    for n in self.G1:
      LstOfAllNodes.remove(n)
    self.G2 = LstOfAllNodes
    
  def ExternalCost(self, node):
    E = 0

    if node in self.G1:
      InG1 = True
    else:
      InG1 = False
      
    nbrs = self.Graph.neighbors(node)
    for nbr in nbrs:
      if InG1 and nbr in self.G2:
        E += 1  
      elif InG1==False and nbr in self.G1:
        E += 1        
    return E
  
  def InternalCost(self, node):
    I = 0
    
    if node in self.G1:
      InG1 = True
    else:
      InG1 = False
    
    nbrs = self.Graph.neighbors(node)
    for nbr in nbrs:
      if InG1 and nbr in self.G1:
        I += 1       
      elif InG1==False and nbr in self.G2:
        I += 1  
    return I    

def main():
  G = nx.Graph()
  nodes = 20
  for x in range(0,nodes):
    G.add_node(x)
    
  mat = np.loadtxt("Topologies/Node40/out40-1.txt",delimiter="\t")  
  for i in mat:
    G.add_edges_from([(int(i[0]),int(i[1])), (int(i[1]),int(i[0]))])  
  mat = None
  #print "Total number of edges in main graph = %d" % G.number_of_edges()      
  obj = MinCut(G)
  print obj.KL()
  
  #G1, G2 = RandomDivision(G)  

if __name__ == '__main__':  
  main() 
