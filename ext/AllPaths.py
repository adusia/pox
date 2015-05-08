import math

class AllPaths:

  Topology = []
  
  num_of_nodes = 0

  NodesVisited = []

  EdgesVisited  = []

  DependencyMatrix = []

  AllProbes = []
  
  ProbeSet = []
  
  DecompositionSet = []
  
  probeno = 0
  
  def __init__(self, Topology):
    self.Topology = Topology
    self.num_of_nodes = len(self.Topology)
    self.DecompositionSet.append([])  

    for x in range(0,self.num_of_nodes):
      self.NodesVisited.append(False) 
      self.EdgesVisited.append([False]*self.num_of_nodes)
      self.DecompositionSet[0].append(x)
      
    self.DecompositionSet[0].append(self.num_of_nodes)
    
    #print "DecompositionSet=" + str(self.DecompositionSet)


    #self.EdgesVisited = deepcopy(self.Topology)   
    #print self.EdgesVisited
    
  def compute_dependency_Matrix(self,currnode):
    for endnode in range(0,self.num_of_nodes):
      self.dfs(currnode,[currnode],endnode)

    return self.DependencyMatrix
    
  def dfs(self, currnode, listofnodes, endnode):
    self.NodesVisited[currnode] = True
    #print "currnode=" + str(currnode)
    #print "endnode=" + str(endnode)
    #print "listofnodes= " + str(listofnodes)
    #print "NodesVisited= " + str(self.NodesVisited)
    #print "EdgesVisited= " + str(self.EdgesVisited)

    tempedges = []
    
    for i in range(0,self.num_of_nodes):
      if (self.Topology[currnode][i] == 1 and self.EdgesVisited[currnode][i] == False ): #and self.NodesVisited[i] == False):
        self.EdgesVisited[currnode][i] = True
        self.EdgesVisited[i][currnode] = True
        tempedges.append(str(currnode) + "-" + str(i))
        #listofnodes.append(i)
        if i == endnode:
          #print "result=" + str(listofnodes + [i])
          DependencyMatrixRow = [0]*(self.num_of_nodes + 1)
          for node in listofnodes + [i]:
            DependencyMatrixRow[node]=1
          self.DependencyMatrix.append(DependencyMatrixRow)
          self.AllProbes.append(listofnodes + [i] + [self.probeno])
          self.probeno += 1
        else:
          #listofnodes.append(i)
          self.dfs(i,listofnodes + [i],endnode)
          
        for edge in tempedges:
          i, j = edge.split("-")
          self.EdgesVisited[int(i)][int(j)]=False
          self.EdgesVisited[int(j)][int(i)]=False
          tempedges.remove(edge)

    self.NodesVisited[currnode]=False      
    '''      
    self.NodesVisited[currnode]=False
    for edge in tempedges:
      i, j = edge.split("-")
      self.EdgesVisited[int(i)][int(j)]=False
      self.EdgesVisited[int(j)][int(i)]=False
    '''  
    #print "return from execution of node " + str(currnode) 
    
  def select_probes_path_cost(self):
    #self.DependencyMatrix.sort(key = lambda x: x.count(1)) 
    self.AllProbes.sort(key = lambda x: (len(x) -2) if x[0] == x[len(x)-2] else (len(x)-2)*2) 
    
    #for probe in range(0,10):
    #  print self.DependencyMatrix[probe]
    
    f = lambda x: (len(x) -2) if x[0] == x[len(x)-2] else (len(x)-2)*2
    for probe in self.AllProbes:
      print probe[:-1] + [f(probe)]
    
    #for probe in range(0,20):    
    #  print self.AllProbes[probe]
    #for probeno in range(0,len(self.AllProbes)):
    
    for probe in self.AllProbes:      
      probeno = probe.pop()#[len(probe)-1]
      #print probeno
      print "DecompositionSet=" + str(self.DecompositionSet)
      if len(self.DecompositionSet) == (self.num_of_nodes + 1):
        return self.ProbeSet
      else:
        
        for nodeset in self.DecompositionSet:
          if len(nodeset) > 1:
            #print "nodeset=" + str(nodeset)
            set1 = []
            set0 = []
            for node in nodeset:
              #print "node=" + str(node)
              if self.DependencyMatrix[probeno][int(node)] == 1:
                set1.append(node)
              else:
                set0.append(node)
            if len(set1) > 0 and len(set0) > 0:
              #self.DecompositionSet.remove(nodeset)
              RemovedSet.append(nodeset)
              DecomposedSet.append(set1)
              DecomposedSet.append(set0)
              #self.ProbeSet.append(self.AllProbes[probeno])              
              if probe not in self.ProbeSet:
                self.ProbeSet.append(probe)
        
        for s in RemovedSet:      
          self.DecompositionSet.remove(s)        
        for s in DecomposedSet:      
          self.DecompositionSet.append(s)      

  def get_probe_entropy (self, probeno, DecompositionSet, get_DecompositionSet = False):
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
          if self.DependencyMatrix[probeno][int(node)] == 1:
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
      return self.get_entropy_ds(ds)

    
  def get_entropy_ds (self, DecompositionSet):
    ds = list(DecompositionSet)
    entropy = 0
    for nodeset in ds:
      length = len(nodeset)
      entropy = entropy + (float(length)/(self.num_of_nodes+1)) * math.log(length,2)
      
    return entropy
    
    
  def select_probes_entropy (self):
    candidate_set = list(self.AllProbes)
    while True:
      minentropy = 9999
      entropy = 0
      probe_selected = -1
      if len(self.DecompositionSet) == (self.num_of_nodes + 1):
        return self.ProbeSet    
      for probeno in range(0,len(candidate_set)):
        entropy = self.get_probe_entropy(probeno,self.DecompositionSet,False)
        #print entropy
        if entropy < minentropy:
          minentropy = entropy
          probe_selected = self.AllProbes[probeno]
      
      print "minentropy="+str(minentropy)
      print "ProbeSelected="+str(probe_selected[:-1])
      self.ProbeSet.append(probe_selected)
      candidate_set.remove(probe_selected)
      self.DecompositionSet = self.get_probe_entropy(probe_selected.pop(),self.DecompositionSet,True)
      print "DecompositionSet=" + str(self.DecompositionSet)
      print "----------------------------------------"
    
    #return self.ProbeSet
        
  
  
  def select_probes_bitwise_and(self):
   result = int(''.join(map(str,self.DependencyMatrix[0])))
   for i in range(0,len(self.DependencyMatrix)):
      MaxNumOfOne = -1;
      NumOfOne = 0
      for j in range(i,len(self.DependencyMatrix)):
        NumOfOne = str(result & int(''.join(map(str,self.DependencyMatrix[j])))).count('1')
        if NumOfOne > MaxNumOfOne:
          MaxNumOfOne = NumOfOne
        return
    
  
  
Topo = []
'''
for x in range(0,10):
  Topo.append([])

Topo[0].extend([0,1,1,1])
Topo[1].extend([1,0,0,1])
Topo[2].extend([1,0,0,1])
Topo[3].extend([1,1,1,0])


#Topo[].extend([0,1,2,3,4,5,6,7,8,9])
Topo[0].extend([0,1,0,1,0,0,1,0,0,0])
Topo[1].extend([1,0,1,1,0,0,0,0,0,0])
Topo[2].extend([0,1,0,0,1,0,0,1,0,0])
Topo[3].extend([1,1,0,0,1,0,0,0,1,0])
Topo[4].extend([0,0,1,1,0,1,1,0,1,0])
Topo[5].extend([0,0,0,0,1,0,0,1,0,1])
Topo[6].extend([1,0,0,0,1,0,0,1,0,0])
Topo[7].extend([0,0,1,0,0,1,1,0,0,1])
Topo[8].extend([0,0,0,1,1,0,0,0,0,1])
Topo[9].extend([0,0,0,0,0,1,0,1,1,0])
'''


for x in range(0,6):
  Topo.append([])

Topo[0].extend([0,1,0,1,0,1])
Topo[1].extend([1,0,1,0,0,0])
Topo[2].extend([0,1,0,1,0,0])
Topo[3].extend([1,0,1,0,1,1])
Topo[4].extend([0,0,0,1,0,1])
Topo[5].extend([1,0,0,1,1,0])

obj = AllPaths(Topo)
startnode = 0

obj.compute_dependency_Matrix(startnode)
#for row in obj.compute_dependency_Matrix(startnode):
#  print row + [row.count(1)]

#for probe in obj.AllProbes:
#  print probe

#print "All Probes=" + str(obj.AllProbes)
#print "Total Probes= %s" % len(obj.AllProbes)

#for probe in obj.select_probes():
#  print probe
#print "Probes Selected= " + str(obj.select_probes_path_cost())
#print "Probes Selected= " + str(obj.select_probes_bitwise_and())
#str(obj.select_probes_entropy())
print "Probes Selected= " + str(obj.select_probes_entropy())

