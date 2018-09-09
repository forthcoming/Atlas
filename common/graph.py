from collections import deque

class Edge:
    def __init__(self,vertex,weight,right=None):
        self.vertex=vertex
        self.weight=weight
        self.right=right

class Graph:  # adjacency list
    def __init__(self,kind='DG'):
        self.__kind=kind  # DG & UDG
        self.__vertices={}
        self.__edge_num=0

    def add(self,come,to,weight=0):
        self.__edge_num+=1
        if come in self.__vertices:
            self.__vertices[come]=Edge(to,weight,self.__vertices[come])
        else:
            self.__vertices[come]=Edge(to,weight)

        if self.__kind=='UDG': # undirected graph
            if to in self.__vertices:
                self.__vertices[to]=Edge(come,weight,self.__vertices[to])
            else:
                self.__vertices[to]=Edge(come,weight)

    def delete(self,come,to):
        if (come in self.__vertices) and (to in self.__vertices):

            edge=self.__vertices[come]
            if edge:
                self.__edge_num-=1
                if edge.vertex==to:
                    self.__vertices[come]=edge.right
                else:
                    pre=edge
                    edge=edge.right
                    while edge:
                        if edge.vertex==to:
                            pre.right=edge.right
                            break
                        pre=edge
                        edge=edge.right
        
            if self.__kind=='UDG': # undirected graph
                edge=self.__vertices[to]
                if edge:
                    if edge.vertex==come:
                        self.__vertices[to]=edge.right
                    else:
                        pre=edge
                        edge=edge.right
                        while edge:
                            if edge.vertex==come:
                                pre.right=edge.right
                                break
                            pre=edge
                            edge=edge.right

    def BFS(self,start=None):
        result=[]
        vertices=set()
        queue=deque()
        if start:
            start=[start]
        else:
            start=self.__vertices
        for vertex in start:
            if vertex not in vertices:
                vertices.add(vertex)
                result.append(vertex)               
                queue.append(self.__vertices[vertex])
            while queue:
                edge=queue.popleft()
                while edge:
                    vertex=edge.vertex
                    if vertex not in vertices:
                        vertices.add(vertex)
                        result.append(vertex)
                        queue.append(self.__vertices[vertex])
                    edge=edge.right
        return result
    
    def find_path(self,start,end):
        vertices=set()
        path=[]
        result=[]
        def _find_path(start,end):
            vertices.add(start)
            path.append(start)
            if start==end:
                result.append(path[:])
            else:
                edge=self.__vertices[start]
                while edge:
                    vertex=edge.vertex
                    if vertex not in vertices:
                        _find_path(vertex,end)
                    edge=edge.right
            vertices.remove(start)
            path.pop()
        _find_path(start,end)
        return result

    def _is_reach(self,start,end,extra=None):
        if start==end:
            return True
        vertices={extra,start}
        queue=deque()
        queue.append(self.__vertices[start])
        while queue:
            edge=queue.popleft()
            while edge:
                vertex=edge.vertex
                if vertex==end:
                    return True
                elif vertex not in vertices:
                    vertices.add(vertex)
                    queue.append(self.__vertices[vertex])
                edge=edge.right
        return False

    def get_vertices(self,start,extra):
        if start!=extra:
            edge=self.__vertices[extra]
            while edge:
                vertex=edge.vertex
                if self._is_reach(start,vertex,extra):
                    yield vertex
                edge=edge.right
        
if __name__=='__main__':
    '''
              A
             / \
            B---C---D
            | \ |
            E---F
    '''

    graph=Graph(kind='UDG')
    for edge in [('A','C',2),('A','B',1),('B','C',5),('C','D',4),('B','F',7),('B','E',2),('E','F',3),('F','C',6)]:
        graph.add(*edge)
    path=graph.find_path('A','F')
    print(path)
    graph.delete('B','F')
    path=graph.find_path('A','D')
    print(path)