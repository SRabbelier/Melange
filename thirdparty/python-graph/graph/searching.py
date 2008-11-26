# Copyright (c) 2007-2008 Pedro Matiello <pmatiello@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


"""
Search algorithms for python-graph.

@sort: breadth_first_search, depth_first_search, _bfs, _dfs
"""


# Depth-first search

def depth_first_search(graph, root=None):
	"""
	Depth-first search.

	@type  graph: graph
	@param graph: Graph.
	
	@type  root: node
	@param root: Optional root node (will explore only root's connected component)

	@rtype:  tuple
	@return: A tupple containing a dictionary and two lists:
		1. Generated spanning tree
		2. Graph's preordering
		3. Graph's postordering
	"""
	visited = {}			# List for marking visited and non-visited nodes
	spanning_tree = {}		# Spanning tree
	pre = []				# Graph's preordering
	post = []				# Graph's postordering

	# DFS from one node only
	if (root is not None):
		spanning_tree[root] = None
		_dfs(graph, visited, spanning_tree, pre, post, root)
		return spanning_tree, pre, post
	
	# Algorithm loop
	for each in graph:
		# Select a non-visited node
		if (each not in visited):
			spanning_tree[each] = None
			# Explore node's connected component
			_dfs(graph, visited, spanning_tree, pre, post, each)

	return spanning_tree, pre, post


def _dfs(graph, visited, spanning_tree, pre, post, node):
	"""
	Depht-first search subfunction.
	
	@type  graph: graph
	@param graph: Graph.

	@type  visited: dictionary
	@param visited: List of nodes (visited nodes are marked non-zero).

	@type  spanning_tree: dictionary
	@param spanning_tree: Spanning tree being built for the graph by DFS.

	@type  pre: list
	@param pre: Graph's preordering.

	@type  post: list
	@param post: Graph's postordering.

	@type  node: node
	@param node: Node to be explored by DFS.
	"""
	visited[node] = 1
	pre.append(node)
	# Explore recursively the connected component
	for each in graph[node]:
		if (each not in visited):
			spanning_tree[each] = node
			_dfs(graph, visited, spanning_tree, pre, post, each)
	post.append(node)


# Breadth-first search

def breadth_first_search(graph, root=None):
	"""
	Breadth-first search.

	@type  graph: graph
	@param graph: Graph.

	@type  root: node
	@param root: Optional root node (will explore only root's connected component)

	@rtype:  tuple
	@return: A tuple containing a dictionary and a list.
		1. Generated spanning tree
		2. Graph's level-based ordering
	"""
	queue = []			# Visiting queue
	spanning_tree = {}	# Spanning tree
	ordering = []

	# BFS from one node only
	if (root is not None):
		queue.append(root)
		ordering.append(root)
		spanning_tree[root] = None
		_bfs(graph, queue, spanning_tree, ordering)
		return spanning_tree, ordering

	# Algorithm
	for each in graph:
		if (each not in spanning_tree):
			queue.append(each)
			ordering.append(root)
			spanning_tree[each] = None
			_bfs(graph, queue, spanning_tree, ordering)

	return spanning_tree, ordering[1:]


def _bfs(graph, queue, spanning_tree, ordering):
	"""
	Breadth-first search subfunction.
	
	@type  graph: graph
	@param graph: Graph.

	@type  spanning_tree: dictionary
	@param spanning_tree: Spanning tree being built for the graph by DFS.
	
	@type  ordering: list
	@param ordering: Graph's level-based ordering.

	@type  queue: list
	@param queue: Nodes to be visited (ordered).
	"""
	while (queue != []):
		node = queue.pop(0)

		for other in graph[node]:
			if (other not in spanning_tree):
				queue.append(other)
				ordering.append(other)
				spanning_tree[other] = node
