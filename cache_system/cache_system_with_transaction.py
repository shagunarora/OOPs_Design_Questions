"""
Follow up 2: If there is a scenario when users want to update 
cache in batches, and entore cache should be updated as a transaction
i.e. if anything fails then entire transaction should rollback.

Implement rollback and commit methods.
"""


import threading

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
        self.lock = threading.Lock()  # Mutex for write access
        self.backup = None

    def _move_node_to_front(self, node):
        # Store head next in temp variable.
        temp = self.dll.head.next

        # Remove node from current position
        node.prev.next = node.next
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
            return None
    
        val = node.val
        self._move_node_to_front(node)
        return val

    def put(self, key, value):
        if key in self.key_to_cache_node_map:
            node = self.key_to_cache_node_map[key]
            node.val = value
            self._move_node_to_front(node)
            return
        
        if self.size == self.capacity:
            # Remove the least recently used node (at the end of the DLL)
            to_remove_node = self.dll.tail.prev
            to_remove_node.prev.next = to_remove_node.next
            to_remove_node.next.prev = to_remove_node.prev

            # Remove from map and adjust size
            key_to_remove = to_remove_node.key
            del self.key_to_cache_node_map[key_to_remove]
            self.size -= 1

        node = Node(key, value)
        self._move_node_to_front(node)
        self.key_to_cache_node_map[key] = node
        self.size += 1

    def put_transaction(self, updates_batch):
        """
        Updates the cache in a transactional manner. If any update fails, the entire
        batch is rolled back.
        :param updates_batch: List of (key, value) tuples to update in the cache.
        """
        with self.lock:
            # Step 2: Store a backup of current state
            self.backup = self._create_backup()

            try:
                # Step 3: Perform updates synchronously
                for key, value in updates_batch:
                    self.put(key, value)
                
                # Step 5: Commit changes if no exceptions occur
                self.commit()
                print("Transaction committed successfully.")

            except Exception as e:
                # Step 4: Rollback in case of any failure
                print(f"Transaction failed with error: {e}. Rolling back...")
                self.rollback()

    def _create_backup(self):
        """Create a backup of the current state of the cache."""
        backup = {
            'key_to_cache_node_map': self.key_to_cache_node_map.copy(),
            'dll': DLL(),
            'size': self.size
        }

        # Deep copy the DLL structure
        current = self.dll.head.next
        while current != self.dll.tail:
            node_copy = Node(current.key, current.val)
            backup['dll'].tail.prev.next = node_copy
            node_copy.prev = backup['dll'].tail.prev
            backup['dll'].tail.prev = node_copy
            node_copy.next = backup['dll'].tail
            current = current.next

        return backup

    def rollback(self):
        """Restore the cache state from the backup."""
        if self.backup:
            self.key_to_cache_node_map = self.backup['key_to_cache_node_map']
            self.dll = self.backup['dll']
            self.size = self.backup['size']
            self.backup = None  # Clear backup after rollback
            print("Cache state has been rolled back.")

    def commit(self):
        """Clear the backup since the transaction succeeded."""
        self.backup = None
        print("Backup cleared. Transaction committed.")

class CacheFactory:
    @staticmethod
    def create_cache(cache_type, capacity=5):
        if cache_type == "LRU":
            return LRUCache(capacity)

# Example of using the cache with transactions
cache = CacheFactory.create_cache("LRU", 5)

# Example interactive mode for testing
exit_flag = False
while not exit_flag:
    qtype = int(input("Enter 1 for get, 2 for put, 3 for transaction, 4 for exit: "))
    if qtype == 1:
        key = input("Enter key: ")
        print(cache.get(key))
    elif qtype == 2:
        key, value = input("Enter key value pair: ").split(" ")
        cache.put(key, value)
    elif qtype == 3:
        updates = []
        num_updates = int(input("Enter number of updates in the transaction: "))
        for _ in range(num_updates):
            key, value = input("Enter key value pair: ").split(" ")
            updates.append((key, value))
        cache.put_transaction(updates)
    elif qtype == 4:
        exit_flag = True
    else:
        print("Invalid input. Try again.")
