class AllPaths:

  Topology = []
  
  num_of_nodes = 0

  NodesVisited = []

  EdgesVisited  = []

  DependencyMatrix = []

  AllProbes = []

  def __init__(self, Topology):
    self.Topology = Topology
    self.num_of_nodes = len(self.Topology)  

    for x in range(0,self.num_of_nodes):
      self.NodesVisited.append(False) 
      self.EdgesVisited.append([False]*self.num_of_nodes)

    #self.EdgesVisited = deepcopy(self.Topology)   
    #print self.EdgesVisited

  def compute_dependency_Matrix(self,currnode):
    for endnode in range(0,self.num_of_nodes):
      self.dfs(currnode,[currnode],endnode)
    return self.DependencyMatrix

  def dfs(self, currnode, listofnodes, endnode):
    self.NodesVisited[currnode] = True
    #print "currnode=" + str(currnode)
    #print "listofnodes= " + str(listofnodes)
    #print "NodesVisited= " + str(self.NodesVisited)
    #print "EdgesVisited= " + str(self.EdgesVisited)

    tempedges = []

    for i in range(0,self.num_of_nodes):
      if (self.Topology[currnode][i] == 1 and self.EdgesVisited[currnode][i] == False and self.NodesVisited[i] == False):
        self.EdgesVisited[currnode][i] = True
        self.EdgesVisited[i][currnode] = True
        tempedges.append(str(currnode) + "-" + str(i))
        #listofnodes.append(i)
        if i == endnode:
			    #print "result=" + str(listofnodes + [i])	    
	  		  #print str(listofnodes + [i])
	  	    DependencyMatrixRow = [0]*self.num_of_nodes
	  	    for node in listofnodes + [i]:
						DependencyMatrixRow[node]=1
						self.DependencyMatrix.append(DependencyMatrixRow)
						self.AllProbes.append(str(listofnodes + [i]))
        else:
				  #listofnodes.append(i)
	 				self.dfs(i,listofnodes + [i],endnode)    
					self.NodesVisited[currnode]=False
			for edge in tempedges:
        i, j = edge.split("-")
        self.EdgesVisited[int(i)][int(j)]=False
        self.EdgesVisited[int(j)][int(i)]=False
        #print "return from execution of node " + str(currnode)  

Topo = []

for x in range(0,4):
  Topo.append([])

Topo[0].extend([0,1,1,1])
Topo[1].extend([1,0,0,1])
Topo[2].extend([1,0,0,1])
Topo[3].extend([1,1,1,0])

'''
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

'''
for x in range(0,6):
  Topo.append([])

Topo[0].extend([0,1,0,1,0,1])
Topo[1].extend([1,0,1,0,0,1])
Topo[2].extend([0,1,0,1,0,0])
Topo[3].extend([1,0,1,0,1,1])
Topo[4].extend([0,0,0,1,0,1])
Topo[5].extend([1,0,0,1,1,0])
'''
obj = AllPaths(Topo)
startnode = 0
#endnode = 2
#AllProbes = []

for row in obj.compute_dependency_Matrix(startnode):
  print row
print obj.AllProbes




