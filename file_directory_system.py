"""
Design an extensible solution to implement a search filter in OOD 
for a directory, matching files by size or name.


 Search
    - name
    - prefix
    - size
        - size as number.

 Solution:
  - Trie data structure
     - TC = O(q*len(word))
     - SC = ?

  - Hashmap
    {size: filenames}

"""

class TrieNode:
    def __init__(self):
        self.children = [None] * 26  # Array for 26 alphabets
        self.files_with_prefix = []  # Files sharing this prefix
        self.word_complete_status = False


class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insertWord(self, word, filename):
        node = self.root

        for ch in word:
            index = ord(ch) - ord('a')
            if not node.children[index]:
                node.children[index] = TrieNode()
            node = node.children[index]
            node.files_with_prefix.append(filename)  # Add file to prefix list
        
        node.word_complete_status = True

    def searchPrefix(self, prefix):
        node = self.root

        for ch in prefix:
            index = ord(ch) - ord('a')
            if not node.children[index]:
                return []  # Prefix not found
            node = node.children[index]
        
        return node.files_with_prefix  # Return all files with this prefix

    def removeWord(self, word, filename):
        node = self.root

        for ch in word:
            index = ord(ch) - ord('a')
            if not node.children[index]:
                raise Exception(f"File {filename} not found in Trie.")
            node = node.children[index]
            # Remove file from the prefix list
            if filename in node.files_with_prefix:
                node.files_with_prefix.remove(filename)


class DirectorySystem:
    def __init__(self, files: dict):
        self.files = files
        self.files_trie_storage = self.buildTrie(files)
        self.file_size_storage = self.buildSizeHashMap(files)
    
    def buildTrie(self, files):
        filesTrieStorage = Trie()

        for filename in files.keys():
            filesTrieStorage.insertWord(filename, filename)
        
        return filesTrieStorage

    def buildSizeHashMap(self, files):
        file_size_to_filenames_map = {}

        for filename, size in files.items():
            file_size_to_filenames_map[size] = file_size_to_filenames_map.get(size, []) + [filename]
        
        return file_size_to_filenames_map
    
    def insertFile(self, filename, filesize):
        if filename in self.files:
            raise Exception(f"File with filename {filename} already exists.")

        self.files[filename] = filesize
        self.files_trie_storage.insertWord(filename, filename)
        self.file_size_storage[filesize] = self.file_size_storage.get(filesize, []) + [filename]

    def deleteFile(self, filename):
        if filename not in self.files:
            raise Exception(f"No file with filename {filename} exists.")
        
        filesize = self.files[filename]
        del self.files[filename]
        
        # Remove from size-based hashmap
        self.file_size_storage[filesize].remove(filename)
        if not self.file_size_storage[filesize]:
            del self.file_size_storage[filesize]

        # Remove from Trie
        self.files_trie_storage.removeWord(filename, filename)

    def searchByPrefix(self, prefix):
        return self.files_trie_storage.searchPrefix(prefix)

    def searchBySize(self, size):
        return self.file_size_storage.get(size, [])


# Example Usage
files = {
    "apple": 100,
    "application": 150,
    "banana": 200,
    "bat": 50
}

directory = DirectorySystem(files)
print(directory.searchByPrefix("app"))  # ['apple', 'application']
print(directory.searchBySize(100))     # ['apple']

directory.insertFile("appstore", 250)
print(directory.searchByPrefix("app"))  # ['apple', 'application', 'appstore']

directory.deleteFile("apple")
print(directory.searchByPrefix("app"))  # ['application', 'appstore']
