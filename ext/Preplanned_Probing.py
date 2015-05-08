

class Preplanned_Probing:

  Topology = []

  Nodes = set()

  Links = set()

  Links_Covered = set()

  #Node_Degree = set()

  Node_Degree = []

  Nodes_Selected = set()

  num_of_nodes = 0

  def __init__(self, Topology):
    self.Topology = Topology
    self.num_of_nodes = len(self.Topology)
    
    self.Node_Degree = [0]*self.num_of_nodes
    #for node in range(0, self.num_of_nodes):     
    #  self.Node_Degree.append([])
    #  self.Node_Degree[node].append(node)
    #  self.Node_Degree[node].append(0)
    
    self.comp_links_degree() 
    #self.select_nodes()


  def comp_links_degree(self):    
    for i in range(0, self.num_of_nodes):
      self.Nodes.add(i)
      for j in range(i, self.num_of_nodes):
        if self.Topology[i][j] == 1:
          self.Links.add(str(i) + "-" + str(j))
          #self.Node_Degree[i][1] += 1
          #self.Node_Degree[j][1] += 1
          self.Node_Degree[i] += 1
          self.Node_Degree[j] += 1
    #print (self.Node_Degree)
   
    
  #Function to compute the node set to send pings to
  def select_nodes(self):
    
    while len(self.Links) != 0:
    
      max_degree_node_links = set()
      max_degree_node = self.comp_max_degree_node()
      #print max_degree_node
      
      self.Nodes_Selected.add(int(max_degree_node)+1)

      max_degree_node_links = self.comp_links_covered(max_degree_node)
      #print max_degree_node_links
    
      #Add links to links covered set
      self.Links_Covered.update(max_degree_node_links)
    
      #print max_degree_node_links
      #print self.Links
      #Remove covered links from the available links set
      self.Links.difference_update(max_degree_node_links)
      #print self.Links

      #update the degree of nodes from remaining available links    
      self.update_node_degree()
      #print self.Node_Degree
      
    return self.Nodes_Selected
  
  #Function to update the degree of the nodes with remaining links
  def update_node_degree(self):
    if len(self.Links) != 0:
      self.Node_Degree = [0]*self.num_of_nodes

      for link in self.Links:
        n1, n2 = link.split('-')
        self.Node_Degree[int(n1)] += 1
        self.Node_Degree[int(n2)] += 1
  

  #Function to compute the node with maximum degree of links
  #In case of multiple nodes with max degree
  #Select the node with minimum links already covered in Links_Covered set
  def comp_max_degree_node(self):
    min_links_covered = 99999
    min_links_covered_node = -1
    
    max_degree = max(self.Node_Degree)
    #print max_degree

    if self.Node_Degree.count(max_degree) == 1:
      return self.Node_Degree.index(max_degree)
    else:            
      for n in self.Nodes:
        if self.Node_Degree[n] == max_degree:
          links_covered = self.comp_links_already_covered(n)
          #print "links_covered " + str(links_covered)
          if links_covered < min_links_covered:
            min_links_covered = links_covered
            min_links_covered_node = n
             
      return min_links_covered_node

 #Function to compute the links covered by a node, and also the set of count
  def comp_links_covered(self, node):

    #Variable to track the links already covered by a node 
    links = set()
 
    for link in self.Links:
      n1, n2 = link.split('-')
      if int(n1) == node or int(n2) == node:
        links.add(link)

    return links


  #Function to compute the links already covered by a node and return the count
  def comp_links_already_covered(self, node):
    
    #Variable to count the number of links already covered by a node 
    count = 0
 
    for link in self.Links_Covered:
      n1, n2 = link.split('-')
      if int(n1) == node or int(n2) == node:
        count += 1

    return count
    

'''
Topo = []

for x in range(0,6):
  Topo.append([])

Topo[0].extend([0,1,0,1,0,1])
Topo[1].extend([1,0,1,0,0,1])
Topo[2].extend([0,1,0,1,0,0])
Topo[3].extend([1,0,1,0,1,1])
Topo[4].extend([0,0,0,1,0,1])
Topo[5].extend([1,0,0,1,1,0])

top1 = Preplanned_Probing(Topo)
print top1.select_nodes()
#top1.comp_edges()
#lst = [1, 5, 5]
#print (lst.count(max(lst)))

dst = {}
dst1 = {}
dst[1] = []
dst[1].append(1)
dst[1].append(2)
dst1[1] = []
dst1[1] = dst[1][:]
dst1[1].remove(1)
print dst1
print dst


#dst1 = dst.copy()
'''
