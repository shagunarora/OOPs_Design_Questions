"""
Question: Implement a cache system with below:

- set, get and delete method. (Input will be string)
    - ["SET key1 value1"]
    - ["GET key1"]
    - ["DELETE key1"]

    
Follow up question:
 - Handle transactions: the transaction is ended by either a COMMIT that commits 
                        everything permanently in the data store or ROLLBACK that 
                        reverts everything that was performed during the transaction 
                        window.
    - Implement commit method.
    - Implement rollback method.

Solution: 
    - Decide size of cache. (N=5)
    - Eviction Algo. (LRU)
    - Data structure: DLL + Hashmap

"""

class Node:
    def __init__(self, key=0, val=0, prev=None, next=None):
        self.key = key
        self.val = val
        self.prev = prev
        self.next = next

class DLL:
    def __init__(self):
        self.head = Node() 
        self.tail = Node()

        self.head.next = self.tail
        self.tail.prev = self.head

class LRUCache:
    def __init__(self, capacity):
        self.key_to_cache_node_map = {}
        self.dll = DLL()
        self.capacity = capacity
        self.size = 0

    def _move_node_to_front(self, node):
        # Store head next in temp variable.
        temp = self.dll.head.next

        # Remove node from current position
        if node.prev: 
            node.prev.next = node.next
        
        if node.next:
            node.next.prev = node.prev

        # Connect node with head.
        node.prev = self.dll.head
        self.dll.head.next = node

        # Connect node with head next.
        node.next = temp
        temp.prev = node
    
    def get(self, key):
        node = self.key_to_cache_node_map.get(key, None)

        if not node:
            print(f"Key {key} doesn't exist in cache.")
            return 
    
        val = node.val

        # Restructure DLL to maintain Least recently used key at the end of DLL.
        # Move current node to the beginning of the list and its the most recent used 
        # node.
        self._move_node_to_front(node)

        return val

    def put(self, key, value):
        if key in self.key_to_cache_node_map:
            # Update value of node and move the node in beginnning of DLL.
            node = self.key_to_cache_node_map[key]
            node.val = value

            # Move node in beginning
            self._move_node_to_front(node)

            return
        

        if self.size == self.capacity:
            # Remove last node of DLL as that signifies least recently used node.
            to_remove_node = self.dll.tail.prev
            to_remove_node.prev.next = to_remove_node.next
            to_remove_node.next.prev = to_remove_node.prev

            to_remove_node.prev = to_remove_node.next = None
            key_to_remove = to_remove_node.key

            del self.key_to_cache_node_map[key_to_remove]
            del to_remove_node

            self.size -= 1

        node = Node(key, value)

        # Insert the node at the start of DLL.
        self._move_node_to_front(node)

        # Store node in key_to_cache map
        self.key_to_cache_node_map[key] = node

        self.size += 1

class CacheFactory:
    @staticmethod
    def create_cache(cache_type, capacity=5):
        if cache_type == "LRU":
            return LRUCache(capacity)
        

cache = CacheFactory.create_cache("LRU")

# Create interactive mode for testing (You can improve interactive 
# test based on how you want to test.)
exit = 0
while(~exit):
    qtype = int(input())

    if qtype == 1:
        key = input()
        print(cache.get(key))
    elif qtype == 2:
        key, value = input().split(" ")
        print(cache.put(key, value))
    else:
        continue

    print(cache.cache.key_to_cache_node_map, "\n")
