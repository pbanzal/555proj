import random
import copy
import os
import sys
import argparse
import numpy as np

##########################################################
#  Graph Functions:

# creation of empty graph
def createGraph(graphSize):
  G = []
  for i in xrange(graphSize):
    G.append([])
    for j in xrange(graphSize):
      G[i].append(0)
  return G

# randomly creating edges
def createRandomEdges(G, graphSize):
  for i in xrange(graphSize):
    for j in xrange(i+1, graphSize):
      G[i][j] = random.randint(0,1)
      G[j][i] = G[i][j]
  return G

# copy part of a graph
def copyGraph(G1, G2, g2Size):
  for i in xrange(g2Size):
    for j in xrange(g2Size):
      G1[i][j] = G2[i][j]
  return G1

# create subgraph from given mapping
def createSubGraph(G, mapping):
  g2Size = len(mapping)
  G2 = createGraph(g2Size)
  for i in xrange(g2Size):
    for j in xrange(g2Size):
      G2[i][j] = G[mapping[i]][mapping[j]]
  return G2

# permuate a given graph using the mapping
# index in G maps to mapping[index] in new graph
def permuteGraph(G, mapping):
  newG = createGraph(len(G[0]))
  itr = xrange(len(mapping))
  for i in itr:
    for j in itr:
      newG[mapping[i]][mapping[j]] = G[i][j]
  return newG

# Create a rev mapping from any given mapping
def createRevMapping(mapping, size) :
  revMapping = range(size)
  for i in xrange(size):
    revMapping[mapping[i]] = i
  return revMapping

# test if one graph is an isomorphic
# subgraph of the other via the given
# mapping
def graphIso(G1, G2, mapping):
  for i in xrange(len(G1)):
    x = mapping[i]
    for j in xrange(len(G1)):
      y = mapping[j]
      if (G1[i][j] != G2[x][y]):
        return False
  return True

# print the matrix neatly
def printGraph(G):
  print len(G), len(G)
  for i in xrange(len(G)):
    print G[i]
    
# read in the graph from standard input
def readGraph(fhandle):
    matrix = np.loadtxt(fhandle,dtype=int)
    G = matrix.tolist()
    return G

# Save graph into a file  
def writeGraph(G,fhandle):
    np.savetxt(fhandle,G,fmt="%d")


##########################################################
# Bit Commitment code

# bitcommit a given graph completely
# return seed Matrix, commit Matrix
def bitCommit(H):
  hSize = len(H)
  seedMat = []
  for i in xrange(hSize):
    seedMat.append([])
    for j in xrange(hSize):
      seedMat[i].append(os.urandom(50))

  commitH = []
  for i in xrange(hSize):
    commitH.append([])
    for j in xrange(hSize):
      random.seed(seedMat[i][j])
      commitH[i].append(random.getrandbits(32) ^ H[i][j])
  return (seedMat, commitH)

# uncommit the graph.
# commitH gets modified
# mapping is used to only uncomit specific part of given graph.
# if mapping maps to all the nodes in given graph then whole graph gets
# uncommited
def uncommit(commitH, seedMat, mapping):
  mLen = 0
  if mapping != None:
    mLen = len(mapping)
  else:
    mLen = len(commitH)
    mapping = xrange(mLen)

  for x in xrange(mLen):
    i = mapping[x]
    for y in xrange(mLen):
      j = mapping[y]
      random.seed(seedMat[i][j])
      commitH[i][j] = commitH[i][j] ^ random.getrandbits(32)



##########################################################
# Arguement parsing
def parse_args():
  parser = argparse.ArgumentParser(description="Zero-Knowledge Graph Isomorphism Prover")
  subparsers = parser.add_subparsers(title='commands', dest='command', 
    description='For help on each command run: "%(prog)s <command> -h"')
  mkgraph_help = 'Generate a new random graph.'
  mkgraph_parser = subparsers.add_parser('MakeGraph', help=mkgraph_help, description=mkgraph_help)
  mkgraph_parser.add_argument('size', type=int, help='Number of nodes in the new graph.')
  mkgraph_parser.add_argument('out_file',  type=argparse.FileType('w'), help='Output file to save resulting graph.')
  isosub_help = 'Generate a new graph (with mapping) that is isomorphic to a random subgraph of the input graph.'
  isosub_parser = subparsers.add_parser('MapIsoSubgraph', help=isosub_help, description=isosub_help)
  isosub_parser.add_argument('in_file',   type=argparse.FileType('r'), help='Input graph file (must be larger than <size> nodes).')
  isosub_parser.add_argument('size', type=int, help='Number of nodes in the new isomorphic subgraph.')
  isosub_parser.add_argument('out_file',  type=argparse.FileType('w'), help='Output file to save resulting isomorphic subgraph.')
  isosub_parser.add_argument('map_file',  type=argparse.FileType('w'), help='Output file to save resulting mapping between input graph and isomorphic subgraph.')
  prover_help='Perform the Zero Knowledge Graph Isomorphism protocol.'
  prove_parser = subparsers.add_parser('Prove', help=prover_help, description=prover_help)
  prove_parser.add_argument('graph_file',      type=argparse.FileType('r'), help='Input whole graph file.')
  prove_parser.add_argument('subgraph_file',   type=argparse.FileType('r'), help='Input subgraph file.')
  prove_parser.add_argument('challenges_file', type=argparse.FileType('r'), help='Input challanges file.')
  prove_parser.add_argument('-map_file',       type=argparse.FileType('r'), help='Input whole graph to subgraph mapping file (if this \
                                    is not supplied then we assume you do not know the mapping!).')
  return parser.parse_args()

##########################################################
# Commands
def MakeGraph(size, out_file):
  print 'Generating new random graph of size ' + str(size) + '.'
  G1 = createGraph(size)
  G1 = createRandomEdges(G1, size)
  writeGraph(G1, out_file)
  print 'Output written to: ' + out_file.name

def MapIsoSubgraph(in_file, size, out_file, map_file):
  print 'Input source graph file: ' + in_file.name
  G1 = readGraph(in_file)
  print 'Input source graph size: ' + str(len(G1)) + ' nodes'
  if size > len(G1):
    print 'Error: subgraph size > source graph size!'
    exit()
  print 'Generating isomorphic subgraph of size ' + str(size) + '.'
  mapping = range(len(G1))
  random.shuffle(mapping)
  print 'Randomizing subgraph mapping.'
  g2g1Mapping = mapping[:size]
  G2 = createSubGraph(G1, g2g1Mapping)
  writeGraph(G2, out_file)
  print 'Output isomorphic subgraph written to: ' + out_file.name
  writeGraph(g2g1Mapping, map_file)
  print 'Output mapping written to: ' + map_file.name

def Prove(G1_file, G2_file, challenges_file, g2g1Mapping_file):
  
  # Make fake G2 -> G1 mapping
  # for when Peggy is cheating!
  def guess_mapping(G1, G2):
    g2g1Mapping = []
    for i in xrange(len(G2)):
      while True:
        guess = random.randint(0,len(G1)-1)
        if guess not in g2g1Mapping:
          break
      g2g1Mapping.append(guess)
    return g2g1Mapping

  print 'Input whole graph file: ' + G1_file.name
  G1 = readGraph(G1_file)
  print 'Input whole graph size: ' + str(len(G1)) + ' nodes'
  print 'Input subgraph file: ' + G2_file.name
  G2 = readGraph(G2_file)
  print 'Input subgraph graph size: ' + str(len(G2)) + ' nodes'
  if len(G2) > len(G1):
    print 'Error: subgraph size > whole graph size!'
    exit()

  if g2g1Mapping_file is not None:
    print 'Input graph mapping file: ' + g2g1Mapping_file.name
    g2g1Mapping = readGraph(g2g1Mapping_file)
  else:
    print '!!! Peggy: Guessing mapping between whole graph and the subgraph.'
    g2g1Mapping = guess_mapping(G1, G2)

  print 'Input challenges file: ' + challenges_file.name
  challenges = [x for row in readGraph(challenges_file) for x in row]
  print 'Number of rounds to perform: ' + str(len(challenges))

  print '\n=== Begining Protocol ==='
  
  for i, challenge in enumerate(challenges):
    print "\n== Round " + str(i+1)
    print 'Peggy: Generating random H graph (isomorphic to the whole graph).'
    g1hMapping = range(len(G1))
    random.shuffle(g1hMapping)
    H = permuteGraph(G1, g1hMapping)

    print 'Peggy: Generating mapping between H and the subgraph.'
    g2hMapping = []
    for i in xrange(len(G2)):
      g2hMapping.append(g1hMapping[g2g1Mapping[i]])

    print 'Peggy: Generating bit-commitments for entire H graph.'
    (seedMat, commitH) = bitCommit(H)
    
    if challenge == 1:
      print "Victor: Challenge is G2 is isomorphic to a subgraph of H."
      print 'Peggy: Uncommiting corresponding nodes of G2 in H.'
      uncommit(commitH, seedMat, g2hMapping)
      if not graphIso(G2, H, g2hMapping):
        print "!!! Victor: Unable to prove subgraph isomorphism between G2 and H!"
      else: 
        print "Victor: Correctly verified G2 is isomorphic to a subgraph of H."
    else:
      print "Victor: Challenge is G1 is isomorphic to H."
      print 'Peggy: Uncommiting all nodes of H.'
      uncommit(commitH, seedMat, g1hMapping)
      if not graphIso(G1, H, g1hMapping):
        print "!!! Victor: Unable to prove isomorphism between G1 and H!"
      else: 
        print "Victor: Correctly verified G1 is isomorphic to H."
     

##########################################################
# Main. Run the program :)
def main():
    args = parse_args()
    random.seed(os.urandom(20))

    if args.command == 'MakeGraph': # Make a random graph and save it
      MakeGraph(args.size, args.out_file)
    elif args.command == 'MapIsoSubgraph':
      MapIsoSubgraph(args.in_file, args.size, args.out_file, args.map_file)
    else:
      Prove(args.graph_file, args.subgraph_file, args.challenges_file, args.map_file)
    
# Start program :)
main()
