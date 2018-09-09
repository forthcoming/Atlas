from collections import deque

class Node: 
    def __init__(self,data,left=None,right=None):   
        self.data=data
        self.left=left
        self.right=right

    def __str__(self):
        return '_id:{}'.format(self.data)

class Hamming:
    def __init__(self,depth=64): 
        self.__root=Node('#')
        self.__depth=depth  # signature's binary digits and binary_tree's depth(not including root node)

    def insert(self,signature,_id): 
        root=self.__root
        for index in range(self.__depth):  # the nodes generateed from low to high
            if signature&1:    # left-child:1,right-child:0
                if not root.left:  
                    root.left=Node(True)
                root=root.left
            else:
                if not root.right:
                    root.right=Node(True)
                root=root.right
            signature>>=1
        root.data=_id

    def BFS(self):
        count=0  # node numbers
        if self.__root:
            queue=deque((self.__root,))
            while queue:
                node=queue.popleft()
                count+=1
                print(node)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        return count

    def find(self,signature,dis):
        root=self.__root
        result=[]
        def _find(root,signature,dis,depth):
            if dis>=0:  
                if depth==self.__depth:
                    print(root)
                    result.append(root)
                    return
                bit=signature&1
                signature>>=1
                if bit:
                    if root.left:
                        _find(root.left,signature,dis,depth+1)
                    if root.right:
                        _find(root.right,signature,dis-1,depth+1)
                else:
                    if root.left:
                        _find(root.left,signature,dis-1,depth+1)
                    if root.right:
                        _find(root.right,signature,dis,depth+1)

        _find(root,signature,dis,0)   
        return result     

    def delete(self):
        pass


if __name__=='__main__':
    lsh=Hamming(4)
    signatures=[0b0011,0b1001,0b1100,0b0111]
    for index,each in enumerate(signatures):
        lsh.insert(each,index)
    matched=lsh.find(0b1001,2)