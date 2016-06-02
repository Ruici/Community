import community as cm
import networkx as nx
import sys
import matplotlib.pyplot as plt
import heapq 
import numpy as np
import json as simplejson
from collections import deque
class Edge(object):
	def __init__(self, start, end):
		self.start = start
		self.end = end
		self.value = 0
	# def value(value):
	# 	self.value = value

class Node(object):
	def __init__(self, value):
		self.value = value
		self.bellowEdge = list()
		self.topEdge = list()
		self.credit = 1
	def add_bellow_Edge(self, edge):
		self.bellowEdge.append(edge)
	def add_topEdge(self, edge):
		self.topEdge.append(edge)
	def credit(self, c):
		self.credit += c

def call_bfs(graph, Gr):
	betweenness = dict()
	for node in Gr.nodes():
		temp_bt = bfs(node, graph)
		for key in temp_bt:
			if key not in betweenness:
				betweenness[key] = temp_bt[key]
			else:
				betweenness[key] += temp_bt[key]
	for key in betweenness:
		betweenness[key] = betweenness[key] / float(2)
	return betweenness
		
def bfs(root, graph):
	levelL = dict()
	rootNode = Node(root)
	levelL[rootNode] = 0
	queue = deque([rootNode])
	explored = set()
	visited = set()
	rem = list()
	remEdge = dict()
	while queue:
		exploreNode = queue.popleft()
		
		if exploreNode.value not in explored:
			explored.add(exploreNode.value)
			# print "eplore", exploreNode.value
			rem.append(exploreNode)
			for child in graph[exploreNode.value]:
				childNode = Node(child)
				if childNode.value not in visited and childNode.value not in explored:
					# print "child", childNode.value

					levelL[childNode] = levelL[exploreNode] + 1
					edge = Edge(exploreNode.value, child)
					if edge not in remEdge:
						remEdge[edge] = 0
					childNode.add_topEdge(edge)
					exploreNode.add_bellow_Edge(edge)

					queue.append(childNode)

					visited.add(childNode.value)
				elif childNode.value not in explored:
					for node in queue:
						if node.value == childNode.value and levelL[node] == levelL[exploreNode] + 1:
							edge = Edge(exploreNode.value, child)
							node.add_topEdge(edge)
							exploreNode.add_bellow_Edge(edge)

	#group the same level 
	same_level = dict()
	for key in levelL:
		level_no = levelL[key]
		if level_no not in same_level:
			same_level[level_no] = []
		same_level[level_no].append(key)

	# for k in same_level:
	# 	print "\n", k, 
	# 	for i in same_level[k]:
	# 		print i.value,

	for key in sorted(same_level, reverse=True):
		if key != 0:
			for node in same_level[key]:
				if len(node.bellowEdge) != 0:
					for e in node.bellowEdge:
						node.credit += remEdge[e]

				#end of nodes credit
				#then the credit of topedte
				num = len(node.topEdge)
				for e in node.topEdge:
					remEdge[e] = node.credit/ float(num)
	bet_res = dict()
	for e in remEdge:
		temp = [e.start, e.end]
		temp = sorted(temp)
		bet_res[tuple(temp)] = remEdge[e]
		#print "(", e.start, ",", e.end, ")",remEdge[e]
	return bet_res








if __name__ == '__main__':
	inputFile = open(sys.argv[1])
	outputFile = open("output.txt", "w")
	outputImg = sys.argv[2]

	G = nx.Graph()
	G_fin = nx.Graph()
	G_pic = nx.Graph()
	for line in inputFile:
		vertice = line.strip().split()
		
		G.add_edge(int(vertice[0]), int(vertice[1]))#G is used to calculate modularity
		G_fin.add_edge(int(vertice[0]), int(vertice[1]))# G_fin is used to get the result community
		G_pic.add_edge(int(vertice[0]), int(vertice[1]))# G_pic is used to print the pic

	#cut is used to record the order of cut edge
	cut = dict()
	#modularity is used to record the modularity of each step
	modularity = list()

	step = list()
	


	while(G.number_of_edges() > 0):
		#calculate the betweenness and get the max one
		heap = list()

		#res = nx.edge_betweenness_centrality(G)
		#first, find out the ajacency list
		aj_list = G.adjacency_list()
		aj_dict = dict()
		node_L = G.nodes()
		for i in range(0, len(node_L)):
			aj_dict[node_L[i]] = aj_list[i]
		#print aj_dict
		res = call_bfs(aj_dict, G)
			
		for key in res:
			heap.append((res[key], key))

		heapq._heapify_max(heap)
		#print heap
		
		#heap: (betweenneww, edge)
		pop = heapq.heappop(heap)
		heapq._heapify_max(heap)
		btw = pop[0]
		temp = pop[1]
		G.remove_edge(*temp)
		idx = len(step)
		step.append(len(step))
		cut[idx] = [temp]
		#print "cut", temp, btw
		while(len(heap)!= 0 and heap[0][0] == btw):
			pop = heapq.heappop(heap)
			heapq._heapify_max(heap)
			temp = pop[1]
			G.remove_edge(*temp)
			cut[idx].append(temp)
		# print "cut", cut[idx]
		graphs = list(nx.connected_component_subgraphs(G))

		part = dict() #{node: #_com}
		idx_com = 0
		for subgraph in graphs:
			inOneCom = subgraph.nodes()
			for ele in inOneCom:
				part[ele] = idx_com
			idx_com += 1
		
		
		st = cm.Status()

		st.init(G, part)
		#calculate the modularity
		modSum = cm.__modularity(st)

		modularity.append(modSum)
		
	#find out the maximum modularity
	idx = np.argmax(modularity)
	
	#find out the community
	for i in range (0, idx +1):
		ed = cut[i]
		for ele in ed:
			G_fin.remove_edge(*ele)
	graphs = list(nx.connected_component_subgraphs(G_fin))


	val_map = dict()
	idx_com = 0
	for subgraph in graphs:
		inOneCom = sorted(subgraph.nodes())
		#write into output.txt
		simplejson.dump(inOneCom, outputFile)
		outputFile.write("\n")
		
		for ele in inOneCom:
			val_map[ele] = idx_com
		idx_com += 1
	values = [val_map.get(node, 0.25) for node in G_pic.nodes()]

	outputFile.close()
	inputFile.close()
	nx.draw(G_pic, cmap = plt.get_cmap('jet'), node_color = values, with_labels = True)
	plt.savefig(outputImg)
#	plt.show()