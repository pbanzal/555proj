import random;
import copy;
import os;
import numpy as np;

G1File = "/Users/Suvidha/Desktop/G1.txt"
G2File = "/Users/Suvidha/Desktop/G2.txt"
G2G1Map = "/Users/Suvidha/Desktop/G2G1Map.txt"

# creation of empty graph
def createGraph(graphSize):
  G = [];
  for i in xrange(graphSize):
    G.append([]);
    for j in xrange(graphSize):
      G[i].append(0);
  return G;

# randomly creating edges
def createEdges(G, graphSize):
  for i in xrange(graphSize):
    for j in xrange(i+1, graphSize):
      G[i][j] = random.randint(0,1);
      G[j][i] = G[i][j];
  return G;

# copy part of a graph
def copyGraph(G1, G2, g2Size):
  for i in xrange(g2Size):
    for j in xrange(g2Size):
      G1[i][j] = G2[i][j];
  return G1;

# create subgraph from given mapping
def createSubGraph(G, mapping):
  g2Size = len(mapping);
  G2 = createGraph(g2Size);
  for i in xrange(g2Size):
    for j in xrange(g2Size):
      G2[i][j] = G[mapping[i]][mapping[j]];
  return G2;

# permuate a given graph using the mapping
# index in G maps to mapping[index] in new graph
def permuteGraph(G, mapping):
  newG = createGraph(len(G[0]));
  itr = xrange(len(mapping));
  for i in itr:
    for j in itr:
      newG[mapping[i]][mapping[j]] = G[i][j];
  return newG;

# Create a rev mapping from any given mapping
def createRevMapping(mapping, size) :
  revMapping = range(size);
  for i in xrange(size):
    revMapping[mapping[i]] = i;
  return revMapping;

# print the matrix neatly
def printGraph(G):
  print len(G), len(G);
  for i in xrange(len(G)):
    print G[i];
    
# read in the graph from standard input
def readGraph(fileName):
    matrix = np.loadtxt(fileName,dtype=int)
    G = matrix.tolist()
    return(G)

# Save graph into a file  
def writeGraph(G,fileName):
    np.savetxt(fileName,G,fmt="%d")

# create own graph for testing the code
# graphs are randomly created
def createGraphForTesting():
  g1Size = random.randint(50, 100);
  g2Size = random.randint(25, g1Size/2);
  G1 = createGraph(g1Size);
  G1 = createEdges(G1, g1Size);

  mapping = range(g1Size)
  random.shuffle(mapping);
  g2g1Mapping = mapping[:g2Size];

  g1g2Mapping = range(g1Size);
  for i in xrange(g1Size):
    g1g2Mapping[i] = "";
  for i in xrange(g2Size):
    g1g2Mapping[g2g1Mapping[i]] = i;

  G2 = createSubGraph(G1, g2g1Mapping);
  print "Created graph G1 of size", g1Size, "and G2 of size", g2Size;
  
  writeGraph(G1,G1File)
  writeGraph(G2,G2File)
  writeGraph(g2g1Mapping,G2G1Map)
 

# bitcommit a given graph completely
# return seed Matrix, commit Matrix
def bitCommit(H):
  hSize = len(H);
  seedMat = [];
  for i in xrange(hSize):
    seedMat.append([]);
    for j in xrange(hSize):
      seedMat[i].append(os.urandom(50));

  commitH = [];
  for i in xrange(hSize):
    commitH.append([]);
    for j in xrange(hSize):
      random.seed(seedMat[i][j]);
      commitH[i].append(random.getrandbits(32) ^ H[i][j]);
  return (seedMat, commitH);

# uncommit the graph.
# commitH gets modified
# mapping is used to only uncomit specific part of given graph.
# if mapping maps to all the nodes in given graph then whole graph gets
# uncommited
def uncommit(commitH, seedMat, mapping):
  mLen = 0;
  if mapping != None:
    mLen = len(mapping);
  else:
    mLen = len(commitH);
    mapping = xrange(mLen);

  for x in xrange(mLen):
    i = mapping[x];
    for y in xrange(mLen):
      j = mapping[y];
      random.seed(seedMat[i][j]);
      commitH[i][j] = commitH[i][j] ^ random.getrandbits(32);

# Prove that the code is right and is working
def prove(G1,G2,g2g1Mapping,isInteractive=True):
  #(G1, G2, g2g1Mapping) = createGraphForTesting();

  g1Size = len(G1);
  g2Size = len(G2);
  g1hMapping = range(g1Size);
  random.shuffle(g1hMapping);

  H = permuteGraph(G1, g1hMapping);
  (seedMat, commitH) = bitCommit(H);
  count=0
  #printGraph(seedMat);
  #printGraph(commitH);
  #printGraph(H);

  g2hMapping = [];
  for i in xrange(g2Size):
    g2hMapping.append(g1hMapping[g2g1Mapping[i]]);

  oldCommitH = copy.deepcopy(commitH);  
  for run in xrange(100):
    random.seed(os.urandom(10));
    if(isInteractive == True):
        while(1):
        
            input = int(raw_input("Please enter 0/1: "))
            if(input == 0 or input == 1):
                break;
        
    else:
        input = random.randint(0,1)
    
    if(input == 1):
      count = count+1
      uncommit(commitH, seedMat, g2hMapping);
      for i in xrange(g2Size):
        x = g2hMapping[i];
        for j in xrange(g2Size):
          y = g2hMapping[j];
          if (G2[i][j] != commitH[x][y]):
            print "Problem in proving subgraph isomorphism between G2 and H"
            print "G2[{0}][{1}]= {2} != commit[{3}][{4}]= {5} where vertices {0},{1} in G2 maps to {6},{7} in G1 which maps to {3},{4} in H".format(i,j,G2[i][j],x,y,commitH[x][y],g2g1Mapping[i],g2g1Mapping[j])
            return(0);
      print "Verified H matches with subGraph G2";
    
    else:
      uncommit(commitH, seedMat, g1hMapping);
      for i in xrange(g1Size):
        x = g1hMapping[i];
        for j in xrange(g1Size):
          y = g1hMapping[j];
          if (G1[i][j] != commitH[x][y]):
            print "Problem in proving isomorphism between G1 and H", G1[i][j], commitH[x][y];
            return(0);
      print "Verified H matches with Graph G1";
    commitH = copy.deepcopy(oldCommitH);
  
  print "Challenge G2,H is choosen {0} times".format(count)
  print "Challenge G1,H is chosen {0} times".format(100-count)
  return(1)

def main():
    createGraphForTesting();
    G1 = readGraph(G1File)
    G2 = readGraph(G2File)
    
    #Honest
    g2g1Mapping = readGraph(G2G1Map) 
    
    #Cheat : No Knowlege of mapping
    #mapping = range(len(G1))
    #random.shuffle(mapping)
    #g2g1Mapping =mapping[:len(G2)]
    
    if(prove(G1,G2,g2g1Mapping,False) == 0):
        print("Conclusion : Peggy COULD NOT convince Victor of her Subgraph Isomorphic Knowledge between G1 and G2")
    else:
        print("In all runs, Peggy convinced Victor of her Subgraph Isomorphic Knowledge between G1 and G2 ")
    
    
# To test if permute function works properly
# Can be used for other testing purpose
def test1():
    # randomly generating random size of the graph
    g1Size = random.randint(100, 100);

    G1 = createGraph(g1Size);

    G1 = createEdges(G1, g1Size);

    # Creating a mapping
    mapping = range(g1Size)
    random.shuffle(mapping);

    revMapping = createRevMapping(mapping, g1Size);

    #print mapping;
    #print revMapping;

    permG1 = permuteGraph(G1, mapping);
    permpermG1 = permuteGraph(permG1, revMapping);

    for i in xrange(g1Size):
      for j in xrange(g1Size):
        if (G1[i][j] != permpermG1[i][j]):
          print "ProblemA",i,j;

# Start program :)
main()