'''
*This approach finds the cyclic path probes from source node to source node with a constraint*
#Constraint: For a graph with max depth X, include probes with length <= 2*X
#Constraint: Edges and Nodes cannot be repeated
#Constraint: Symmetric probes are not added
*This probes may not be able to uniquely identify all possible faults
*So using the undecomposed set, extra probes (non-cyclic) are added to the probe set
until all faults can be uniquely identified
*Iterative BFS method is used
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

class AllPaths:

  Topology = []
  
  num_of_nodes = 0
 
  DependencyMatrix = []

  AllProbes = []
  
  ProbeSet = []
  
  DecompositionSet = []
  
  probeno = 0
  
  NumberOfProbesSelected = 0
  
  Node = collections.namedtuple('Node', 'NodeNum, parents')
  
  G = nx.Graph()
  
  ProbeCount = {}
  
  def __init__(self, Topology, Graph):
    self.Topology = Topology
    self.num_of_nodes = len(self.Topology)    
    self.G = Graph    
    self.DependencyMatrix = []
    self.AllProbes = []   
    #print nx.shortest_path_length(self.G,0,4)
    self.probeno = 0
    self.initialization()
      
  def initialization(self):
  
    self.ProbeSet = []    
    self.NumberOfProbesSelected = 0
    self.DecompositionSet = []
    self.DecompositionSet.append([])
    for x in range(0,self.num_of_nodes):      
      self.DecompositionSet[0].append(x)
      self.ProbeCount[x] = 0
      
    self.DecompositionSet[0].append(self.num_of_nodes)    
    
   
  def compute_dependency_Matrix(self,currnode):
    self.iterDFS(currnode,currnode)
    '''
    for endnode in range(0,self.num_of_nodes):    
      self.iterDFS(currnode,endnode)'''
    
    return self.DependencyMatrix
    
  def iterDFS(self, currnode, endnode): 
    #print "endnode=%s" % endnode
    startnode = self.Node(currnode, str(currnode))
    #stack = []
    stack = deque()
    stack.append(startnode)
    #d = 0

    distToEndnode = {}
    nodeDegree = {}      
    for n in range(0,self.num_of_nodes):
      distToEndnode[n] = nx.shortest_path_length(self.G,n,endnode)      
      nodeDegree[n] = self.G.degree(n)
    MaxDepth = max(distToEndnode.itervalues())
    #print distToEndnode
    print "MaxDepth = %d" % MaxDepth
    
    while (stack):     
      #d += 1
      top = stack.popleft()      
      #top = stack.pop()      
      nbrs = [i for i,x in enumerate(self.Topology[top.NodeNum]) if x == 1]
      for nbr in nbrs:        
        #if str(top.NodeNum)+"-"+str(nbr) not in top.parents and str(nbr)+"-"+str(top.NodeNum) not in top.parents:
        if str(nbr) not in top.parents or (nbr == currnode and str(top.NodeNum)+"-"+str(nbr) not in top.parents and str(nbr)+"-"+str(top.NodeNum) not in top.parents):
          if nbr == endnode:
            probe = top.parents.split("-") + [str(nbr)]# + [str(self.probeno)]   
            DependencyMatrixRow = [0]*(self.num_of_nodes + 1)
            for node in probe:
              DependencyMatrixRow[int(node)] += 1
            if DependencyMatrixRow not in self.DependencyMatrix:
              self.DependencyMatrix.append(DependencyMatrixRow)
              self.AllProbes.append(map(int, probe + [str(self.probeno)]))
              self.probeno += 1
              self.ProbeCount[endnode] += 1
              for n in top.parents.split("-"):
                if int(n) in nodeDegree:
                  nodeDegree[int(n)] -= 1
                  if nodeDegree[int(n)] == 0:
                    del nodeDegree[int(n)]
                    
              #print "Probe=%s" % str(probe)
            '''
            self.DependencyMatrix.append(DependencyMatrixRow)
            self.AllProbes.append(map(int, probe + [str(self.probeno)]))
            self.probeno += 1    '''
          else:           
            if len((top.parents+"-"+str(nbr)).split("-")) <= MaxDepth*2:
            #if int(nbr) in nodeDegree:
            #if len(nodeDegree) > 0:           
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
      
      if len(self.DecompositionSet) == (self.num_of_nodes + 1):        
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
          #if self.DependencyMatrix[probeno][int(node)] == 1:
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
      
      if len(self.DecompositionSet) == (self.num_of_nodes + 1):
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
        


for j in range(10,101,10):

  Topo = []
  G = nx.Graph()
  #labels = {}

  nodes=j
  for x in range(0,nodes):
    Topo.append([])
    Topo[x].extend([0]*nodes)
    G.add_node(x)
    #labels[x]='$'+str(x)+'$'
  
  print colored("Number of nodes = %d" % nodes,'red')
  mat = np.loadtxt("Topologies/"+str(nodes)+"-2.txt",delimiter="\t")
  
  for i in mat:
    Topo[int(i[0])][int(i[1])] = 1
    Topo[int(i[1])][int(i[0])] = 1
    G.add_edges_from([(int(i[0]),int(i[1])), (int(i[1]),int(i[0]))])  

  mat = None  

  
  '''
  for x in range(0,6):
    Topo.append([])
    G.add_node(x)
  Topo[0].extend([0,1,0,1,0,1])
  Topo[1].extend([1,0,1,0,0,0])
  Topo[2].extend([0,1,0,1,0,0])
  Topo[3].extend([1,0,1,0,1,1])
  Topo[4].extend([0,0,0,1,0,1])
  Topo[5].extend([1,0,0,1,1,0])
  for row in range(0,6):
    for col in range(0,6):
      if Topo[row][col] == 1:
        G.add_edge(row,col)
  #print G.edges()
  '''

  obj = AllPaths(Topo, G)
  startnode = 0

  obj.compute_dependency_Matrix(startnode)
  #for row in obj.compute_dependency_Matrix(startnode):
  #  print row #+ [row.count(1)]

  #for probe in obj.AllProbes:
  #  print probe

  #print "All Probes=" + str(obj.AllProbes)
  print colored("Total Probes = %s" % len(obj.AllProbes),'red')
  print "----------------------------------------------------------------------------------"

  print colored("Probe selection using PathCost/ProbeLength", 'white')
  obj.select_probes_path_cost()
  #obj.select_probes_entropy()

  #for probe in obj.ProbeSet:
  #  print probe

  #print "Probes Selected=%s" % obj.ProbeSet
  print colored("Total number of probes = %d" % obj.NumberOfProbesSelected, 'red')
  f = lambda x: (len(x) - 2) if x[0] == x[len(x)-2] else (len(x)-2)*2 
  print colored("Total length of all probes = %d" % sum(f(lst) for lst in obj.ProbeSet), 'red')
  #print obj.ProbeCount
  print "----------------------------------------------------------------------------------"
  
  obj.initialization()
  
  print colored("Probe selection using entropy", 'white')  
  obj.select_probes_entropy()
  #for probe in obj.ProbeSet:
  #  print probe


  print colored("Total number of probes = %d" % obj.NumberOfProbesSelected, 'red')
  #f = lambda x: (len(x) -1) if x[0] == x[len(x)-1] else (len(x)-1)*2 
  print colored("Total length of all probes = %d" % sum(f(lst) for lst in obj.ProbeSet), 'red')
  #print obj.ProbeCount
  print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  
  
  '''
  plt.figure(figsize=(24,24))
  pox=nx.spring_layout(G)
  nx.draw_networkx(G,pox,labels)
  plt.show()
  '''
