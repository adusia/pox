for j in range(1,11):
  for i in range(0,10):
    with open("Topologies/Node"+str(j)+"0/out"+str(j)+"0-"+str(i)+".brite",'r') as fR:  
      for line in fR:
        if "Edges:" in line:
          with open("Topologies/Node"+str(j)+"0/out"+str(j)+"0-"+str(i)+".txt",'w') as fW:    
            while True:  
              try:
                row = fR.next().split("\t")
                fW.write(row[1] + '\t' + row[2] + '\n')
              except: 
                break
    
