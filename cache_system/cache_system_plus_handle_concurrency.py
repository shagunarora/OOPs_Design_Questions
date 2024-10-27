"""
Create a custom ReaderWriter lock to handle concurrency.
    - Multiple read threads are allowed to access shared data. 
      (cache in this case).
    - Write should be performed exclusively as it can generate 
      wrong results for other threads.

Below code is improvement of v1 which contains implementation of cache
without handling concurrency.

"""

import threading

class ReaderWriterLock:
    def __init__(self):
        self.readers = 0
        self.writer = False
        self.condition = threading.Condition()

    def acquire_read(self):
        with self.condition:
            while self.writer:
                self.condition.wait()
            self.readers += 1

    def release_read(self):
        with self.condition:
            self.readers -= 1
            if self.readers == 0:
                self.condition.notify_all()

    def acquire_write(self):
        with self.condition:
            while self.writer or self.readers > 0:
                self.condition.wait()
            self.writer = True

    def release_write(self):
        with self.condition:
            self.writer = False
            self.condition.notify_all()

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
        self.lock = ReaderWriterLock()  # Use the custom reader-writer lock.

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
        # Acquire read lock to allow multiple reads simultaneously.
        self.lock.acquire_read()
        try:
            node = self.key_to_cache_node_map.get(key, None)
            if not node:
                print(f"Key {key} doesn't exist in cache.")
                return None

            val = node.val

            # Since it's accessed, move the node to the front.
            # Acquire a write lock since this operation modifies the cache.
            self.lock.release_read()
            self.lock.acquire_write()
            try:
                self._move_node_to_front(node)
            finally:
                self.lock.release_write()

            return val
        finally:
            # Ensure the read lock is released if not already.
            if self.lock.readers > 0:
                self.lock.release_read()

    def put(self, key, value):
        # Acquire write lock as this will modify the cache.
        self.lock.acquire_write()
        try:
            if key in self.key_to_cache_node_map:
                # Update value of node and move the node to the beginning of DLL.
                node = self.key_to_cache_node_map[key]
                node.val = value
                self._move_node_to_front(node)
                return
            
            if self.size == self.capacity:
                # Remove last node of DLL as it signifies the least recently used node.
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

            # Store node in the key_to_cache map.
            self.key_to_cache_node_map[key] = node

            self.size += 1
        finally:
            # Ensure the write lock is released.
            self.lock.release_write()
