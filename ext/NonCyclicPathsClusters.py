'''
*KMeans clustering algorithm is used to compute subgraphs
*This approach finds the non-cyclic probes from cluster center node to all nodes in the subgraph with a constraint*
#Constraint: Probe length <= Depth of Subgraph from cluster center
#Constraint: Edges and Nodes cannot be repeated
#Constraint: Symmetric probes are not added
*The path from source node of the complete graph to the cluster center is added to each probe of that cluster.
*IterativeBFS is used to search the graph for paths
'''

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
import timeit
import os
from KMeans import KMeans

class AllPaths:

  def __init__(self, Graph):   
    self.num_of_nodes = Graph.number_of_nodes()    
    self.G = Graph    
    self.DependencyMatrix = []
    self.AllProbes = []   
    self.probeno = 0
    self.MaxdepthSubGraph = -1
    self.Node = collections.namedtuple('Node', 'NodeNum, parents')
    self.ProbeToClus = []

    distToNode = {}
    for n in range(0,self.num_of_nodes):
      distToNode[n] = nx.shortest_path_length(self.G,0,n)
    self.Maxdepth = max(distToNode.itervalues())

    self.initialization()
      
  def initialization(self):
  
    self.ProbeSet = []    
    self.NumberOfProbesSelected = 0
    self.DecompositionSet = []
    self.DecompositionSet.append([])
    self.ProbeCount = {}
    for x in range(1,self.num_of_nodes):      
      self.DecompositionSet[0].append(x)
      self.ProbeCount[x] = 0
      
    self.DecompositionSet[0].append(self.num_of_nodes) 
    #print self.DecompositionSet
   
  def compute_dependency_Matrix(self,currnode,clusters):
    for clus, nodes in clusters.items():
      if currnode in nodes:
        nodes.remove(currnode)
      #print clus, nodes
      SubGraph = self.G.subgraph(nodes)
      #self.PrintGraph(SubGraph)
      if clus != currnode: #source node is not one of the clusters
        self.ProbeToClus = nx.shortest_path(self.G,source=currnode,target=clus)
        #AllProbesToClus = nx.all_simple_paths(self.G,source=currnode,target=clus,cutoff=self.Maxdepth) #cutoff = self.Maxdepth
        AllProbesToClus = []
        AllProbesToClus.append(self.ProbeToClus)
        for probe in list(AllProbesToClus):
          DependencyMatrixRow = [0]*(self.num_of_nodes + 1)
          for node in probe:
            DependencyMatrixRow[int(node)] += 1
          if DependencyMatrixRow not in self.DependencyMatrix:
            self.DependencyMatrix.append(DependencyMatrixRow)
            self.AllProbes.append(probe + [self.probeno])
            self.probeno += 1
          
        self.ProbeToClus.pop()    
        
      #print "ProbeToClus = %s"%self.ProbeToClus
      
      
      distToNode = {}   
      for n in SubGraph.nodes():
        try:
          distToNode[n] = nx.shortest_path_length(SubGraph,n,clus)
        except:
          print "EXCEPTION!!!! Disconnected Graph"
          #print SubGraph.nodes()
          #print SubGraph.edges()
          #print distToNode
          #print n
          #print self.G.edges(n) 
      self.MaxdepthSubGraph = max(distToNode.itervalues())  
      
      for node in nodes:
        if node != clus and node != currnode:
          self.iterBFS(clus, node, SubGraph)
       
    return self.DependencyMatrix
    
  def iterBFS(self, currnode, endnode, SubGraph): 
    #print "endnode=%s" % endnode
    startnode = self.Node(currnode, str(currnode))
    #stack = []
    stack = deque()
    stack.append(startnode)
    #d = 0
    
    while (stack):     
      #d += 1
      top = stack.popleft()      
      nbrs = SubGraph.neighbors(top.NodeNum)
      for nbr in nbrs:        
        #if str(top.NodeNum)+"-"+str(nbr) not in top.parents and str(nbr)+"-"+str(top.NodeNum) not in top.parents:
        if str(nbr) not in top.parents.split("-") or (nbr == currnode and str(top.NodeNum)+"-"+str(nbr) not in top.parents and str(nbr)+"-"+str(top.NodeNum) not in top.parents):
          if nbr == endnode:
            probe = self.ProbeToClus + top.parents.split("-") + [str(nbr)]
            DependencyMatrixRow = [0]*(self.num_of_nodes + 1)
            for node in probe:
              DependencyMatrixRow[int(node)] += 1
            if DependencyMatrixRow not in self.DependencyMatrix:
              self.DependencyMatrix.append(DependencyMatrixRow)
              self.AllProbes.append(map(int, probe + [str(self.probeno)]))
              self.probeno += 1
              #self.ProbeCount[endnode] += 1              
              #print "top.NodeNum=%d" % top.NodeNum
              #print "Probe=%s" % str(probe)            
          else:
            #if len((top.parents+"-"+str(nbr)).split("-")) <= distToEndnode[currnode]: #shortest length probe
            if len((top.parents+"-"+str(nbr)).split("-")) <= self.MaxdepthSubGraph: #maxdepth of the sub graph 
            #if len((top.parents+"-"+str(nbr)).split("-")) <= MaxDepth: #maxDepth of the node
            #if len((top.parents+"-"+str(nbr)).split("-")) <= self.num_of_nodes:
              stack.append(self.Node(nbr, top.parents+"-"+str(nbr)))
      #print stack
      #print nodeDegree
           
      #if d <= 10:
      #  print stack 
 
    
  def select_probes_path_cost(self):
    candidate_set = list(self.AllProbes)    
    candidate_set.sort(key = lambda x: (len(x) -2) if x[0] == x[len(x)-2] else (len(x)-2)*2)         
    DM = list(self.DependencyMatrix)
    while True:    
      for probe in candidate_set:      
        probeno = int(probe[-1]) #int(probe.pop())
        #print probeno
        #print "DecompositionSet=" + str(self.DecompositionSet)   
        DecomposedSet = []
        RemovedSet = []
        for nodeset in self.DecompositionSet:
          if len(nodeset) > 1:
            #print "nodeset=" + str(nodeset)
            set1 = []
            set0 = []
            for node in nodeset:
              #print "node=" + str(node)
              if DM[probeno][int(node)] > 0:
                set1.append(node)
              else:
                set0.append(node)
            if len(set1) > 0 and len(set0) > 0:
              #self.DecompositionSet.remove(nodeset)
              RemovedSet.append(nodeset)
              DecomposedSet.append(set1)
              DecomposedSet.append(set0)                          
              if probe not in self.ProbeSet:
                #print "DecompositionSet=" + str(self.DecompositionSet)
                #print probe
                self.ProbeSet.append(probe)
        
        for s in RemovedSet:      
          self.DecompositionSet.remove(s)        
        for s in DecomposedSet:      
          self.DecompositionSet.append(s)  
      
      if len(self.DecompositionSet) == (self.num_of_nodes):        
        self.NumberOfProbesSelected = len(self.ProbeSet)
        candidate_set = None
        DM = None        
        return        

      #self.NumberOfProbesSelected = len(self.ProbeSet)
      print colored("Undecomposed Set=" + str(self.DecompositionSet),'green')      
      print colored("Total number of probes with undecomposed set = %d" % len(self.ProbeSet), 'blue')
      f = lambda x: (len(x) -2) if x[0] == x[len(x)-2] else (len(x)-2)*2 
      print colored("Total length of all probes with undecomposed set = %d" % sum(f(lst) for lst in self.ProbeSet), 'blue')        
      #print "Candidat Set=%s" % str(candidate_set)
     
      candidate_set = []
      for ds in self.DecompositionSet:
        if len(ds) > 1:
          for node in ds:
            if self.G.__contains__(int(node)):
              newprobe = nx.shortest_path(self.G,0,int(node))+[self.probeno]
              candidate_set.append(newprobe)
              self.probeno += 1
              DependencyMatrixRow = [0]*(self.num_of_nodes + 1)
              for node in newprobe[:-1]:
                DependencyMatrixRow[int(node)] += 1              
              DM.append(DependencyMatrixRow)
              #self.AllProbes.append(newprobe)
      print "New Candidate Set=%s" % str(candidate_set)      
   
    
  def get_probe_entropy (self, probe, DecompositionSet, get_DecompositionSet = False):
    if get_DecompositionSet: 
      ds = DecompositionSet
    else:
      ds = list(DecompositionSet)  
    DecomposedSet = []
    RemovedSet = []
    for nodeset in ds:
      if len(nodeset) > 1:      
        set1 = []
        set0 = []
        for node in nodeset:
          if node in probe:
            set1.append(node)
          else:
            set0.append(node)
        if len(set1) > 0 and len(set0) > 0:      
          RemovedSet.append(nodeset)
          DecomposedSet.append(set1)
          DecomposedSet.append(set0)
        
    for s in RemovedSet:      
      ds.remove(s)        
    for s in DecomposedSet:      
      ds.append(s)
    
    if get_DecompositionSet:
      return ds
    else:
      if len(ds) > len(DecompositionSet):  
        return self.get_entropy_ds(ds)
      else:
        return 10000

    
  def get_entropy_ds (self, DecompositionSet):
    ds = list(DecompositionSet)
    entropy = 0    
    for nodeset in ds:
      length = len(nodeset)
      entropy = entropy + (float(length)/(self.num_of_nodes+1)) * math.log(length,2)
            
    return entropy
        
  def select_probes_entropy (self):
    candidate_set = list(self.AllProbes)    
    f = lambda x: (len(x) -2) if x[0] == x[len(x)-2] else (len(x)-2)*2
    #print "DecompositionSet=" + str(self.DecompositionSet)    
    while True:
      minentropy = 9999
      entropy = 0
      probe_selected = -1      
      minProbeLen = 9999
      ProbeLen = -1      
      
      if len(self.DecompositionSet) == (self.num_of_nodes):
        self.NumberOfProbesSelected = len(self.ProbeSet)
        return 
      for probe in candidate_set:
        #print "Probe= %s"%probe
        #print "DecompositionSet=%s"%self.DecompositionSet
        entropy = self.get_probe_entropy(probe[:-1],self.DecompositionSet,False)
        #ProbeLen = len(probe[:-1])-1
        ProbeLen = f(probe)
        
        if entropy == minentropy and ProbeLen < minProbeLen:
          #print "minentropy=%s"%str(minentropy)
          #print "ProbeLen= %d"%ProbeLen
          #print "minProbeLen= %d"%minProbeLen
          minentropy = entropy
          minProbeLen = ProbeLen
          probe_selected = probe 
        
        if entropy < minentropy:
          #print "entropy=%s"%str(entropy)
          #print "ProbeLen= %d"%ProbeLen
          #print "minProbeLen= %d"%minProbeLen
          minentropy = entropy
          minProbeLen = ProbeLen
          probe_selected = probe
                           
      if probe_selected != -1: 
        #print "minentropy="+str(minentropy)      
        #print "ProbeSelected=%s " % str(probe_selected[:-1])
        self.ProbeSet.append(probe_selected)
        candidate_set.remove(probe_selected)
        self.DecompositionSet = self.get_probe_entropy(probe_selected[:-1],self.DecompositionSet,True)
        #print "DecompositionSet=" + str(self.DecompositionSet)
      else:
        #self.NumberOfProbesSelected = len(self.ProbeSet)
        print colored("Undecomposed Set=" + str(self.DecompositionSet),'green')
        print colored("Total number of probes with undecomposed set = %d" % len(self.ProbeSet), 'blue')
        #f = lambda x: (len(x) -1) if x[0] == x[len(x)-1] else (len(x)-1)*2 
        print colored("Total length of all probes with undecomposed set = %d" % sum(f(lst) for lst in self.ProbeSet), 'blue')        
        #print "Candidat Set=%s" % str(candidate_set)
        candidate_set = []
        for ds in self.DecompositionSet:
          if len(ds) > 1:
            for node in ds:
              if self.G.__contains__(int(node)):
                newprobe = nx.shortest_path(self.G,0,int(node))+[self.probeno]
                candidate_set.append(newprobe)
                self.probeno += 1  
                DependencyMatrixRow = [0]*(self.num_of_nodes + 1)
                for node in newprobe[:-1]:
                  DependencyMatrixRow[int(node)] += 1              
                self.DependencyMatrix.append(DependencyMatrixRow)
                self.AllProbes.append(newprobe)              
       
        print "New Candidate Set=%s" % str(candidate_set)

  def PrintGraph(self,Graph):
    labels = {}
    plt.figure(figsize=(12,12))
    pox=nx.spring_layout(Graph)
    for node in Graph.nodes():
      labels[node]='$'+str(node)+'$'
    nx.draw_networkx(Graph,pox,labels)
    plt.show()


def main():  
        
  #filename = "Topologies/Node"+str(nodes)+"/result-GraphDepth"+str(nodes)+".txt"
  filename = "Topologies/ClusterResults/GraphDepth.txt"
  if os.path.exists(filename):
    os.remove(filename)
  with open(filename,'a') as fR:
    fR.write("Nodes\t"+"AvgDeg\t"+"TotPrbs\t"+"MaxDepth\t"+"PCExecTime\t"+"No.ofPrbs\t"+"TotLenOfPrbs\t"+"PEExecTime\t"+"No.ofPrbs\t"+"TotLenOfPrbs\n")
        
  for nodes in range(10,11,10):
    for j in range(0,1):
      print "nodes = %d" % nodes, " j=%d" % j
      G = nx.Graph()
      #labels = {}
      ResultRow = []
      ResultRow.append(nodes)
    
      for x in range(0,nodes):
        G.add_node(x)
        #labels[x]='$'+str(x)+'$'
  
      #print colored("Number of nodes = %d" % nodes,'red')
      mat = np.loadtxt("Topologies/Node"+str(nodes)+"/out"+str(nodes)+"-"+str(j)+".txt",delimiter="\t")
  
      for i in mat:
        G.add_edges_from([(int(i[0]),int(i[1])), (int(i[1]),int(i[0]))])  

      mat = None    

      obj = AllPaths(G)
      startnode = 0
  
      clusters = KMeans(G,5)
      #print "K = 2"
      print "clusters = %s"%clusters
        
      obj.compute_dependency_Matrix(startnode,clusters)
 
    
      #for row in obj.compute_dependency_Matrix(startnode):
      #  print row #+ [row.count(1)]
    
      #for probe in obj.AllProbes:
        #print probe[:-1]
      ResultRow.append(float(sum(nx.degree(G).values()))/nodes)     
      ResultRow.append(obj.Maxdepth)
      #print colored("Total Probes = %s" % len(obj.AllProbes),'red')
      #print "----------------------------------------------------------------------------------"

      #print colored("Probe selection using PathCost/ProbeLength", 'white')
      start = timeit.default_timer()  
      obj.select_probes_path_cost()
      stop = timeit.default_timer()      
      ResultRow.append(str(stop - start))

      #for probe in obj.ProbeSet:
        #print probe[:-1]
  
      ResultRow.append(obj.NumberOfProbesSelected)
      #print colored("Total number of probes = %d" % obj.NumberOfProbesSelected, 'red')
      f = lambda x: (len(x) - 2) if x[0] == x[len(x)-2] else (len(x)-2)*2 
      #print colored("Total length of all probes = %d" % sum(f(lst) for lst in obj.ProbeSet), 'red')
      #print obj.ProbeCount
      #print "----------------------------------------------------------------------------------"
      ResultRow.append(sum(f(lst) for lst in obj.ProbeSet))
    
      obj.initialization()  
      #print colored("Probe selection using entropy", 'white')
      start = timeit.default_timer()  
      obj.select_probes_entropy()
      stop = timeit.default_timer()
      ResultRow.insert(2,len(obj.AllProbes))
      ResultRow.append(str(stop - start))

      #for probe in obj.ProbeSet:
      #  print probe[:-1]

      ResultRow.append(obj.NumberOfProbesSelected)
      #print colored("Total number of probes = %d" % obj.NumberOfProbesSelected, 'red')  
      #print colored("Total length of all probes = %d" % sum(f(lst) for lst in obj.ProbeSet), 'red')
      #print obj.ProbeCount
      print colored("Total Probes after adding new probes= %s" % len(obj.AllProbes),'red')
      #print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
      ResultRow.append(sum(f(lst) for lst in obj.ProbeSet))

      with open(filename,'a') as fR:
        for res in ResultRow:
          fR.write(str(res)+"\t")
        fR.write("\n")
        
      #obj.PrintGraph(G)

if __name__ == '__main__':
  main()
  
