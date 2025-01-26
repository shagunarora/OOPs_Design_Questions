"""
Design a library to read a directory and perform operations 
such as filtering by file type and size constraints.

Requirements:
    - Filter based on file type (hashmap)
        - file type e.g. txt, xlsx can be extracted from the filename itself.
            - hashmap

    - Provide option to filter by size directly by provding one size and also range of size.
         - hashmap
         - sortedSet (To maintain sizes)

    TODO: Ordered dict (Read about this how it is different from normal dict)

"""
from sortedcontainers import SortedSet
from bisect           import bisect_left

class Directory:
    def __init__(self, files: dict):
        self.files = files
        self.filetype_to_filenames_map : dict = self.buildFileTypeToFileMap()
        self.filesize_to_filenames_map : dict = self.buildFileSizeToFileMap()
        self.filesizes_available_in_sorted_order : SortedSet = self.initializeFileSizesSortedList()

    def buildFileTypeToFileMap(self):
        filetype_to_filename_map = {}

        for filename in self.files.keys():
            # Extract extension/filetype of the file
            filetype = filename.split('.')[-1]
            filetype_to_filename_map[filetype] = filetype_to_filename_map.get(filetype, []) + [filename]
        
        return filetype_to_filename_map
    
    def buildFileSizeToFileMap(self):
        filesize_to_filename_map = {}
        for filename, filesize in self.files.items():
            filesize_to_filename_map[filesize] = filesize_to_filename_map.get(filesize, []) + [filename]
        
        return filesize_to_filename_map

    def initializeFileSizesSortedList(self):
        filesize_sorted_list = SortedSet()
        for filesize in self.files.values():
            filesize_sorted_list.add(filesize)
        
        return filesize_sorted_list

    def filterByType(self, filetype):
        return self.filetype_to_filenames_map.get(filetype, [])

    def filterBySize(self, filesize):
        return self.filesize_to_filenames_map.get(filesize, [])

    def filterBySizeRange(self, min_file_size, max_file_size):
        # Get index from sortedList from where we have to start fetching files
        files = []
        index = bisect_left(self.filesizes_available_in_sorted_order, min_file_size)
        while index < len(self.filesizes_available_in_sorted_order) and \
                self.filesizes_available_in_sorted_order[index] <= max_file_size:
            files.extend(self.filesize_to_filenames_map.get(self.filesizes_available_in_sorted_order[index], []))
            index += 1
        
        return files


# Example cases

files = {
    "apple.txt": 10,
    "mango.txt": 10,
    "car.csv": 100,
    "truck.csv": 20
}

directory = Directory(files)
print(directory.filterBySize(10))
print(directory.filterBySizeRange(20, 100))
print(directory.filterBySize(20))

# Sample Test Case 2:

# Empty directory
empty_files = {}
empty_directory = Directory(empty_files)
print(empty_directory.filterByType("txt"))  # []
print(empty_directory.filterBySize(10))     # []
print(empty_directory.filterBySizeRange(1, 50))  # []

# Files with duplicate extensions but different sizes
files = {
    "doc1.txt": 10,
    "doc2.txt": 20,
    "sheet.csv": 100,
    "data.csv": 20,
    "readme.md": 5,
}
directory = Directory(files)
print(directory.filterByType("txt"))  # ['doc1.txt', 'doc2.txt']
print(directory.filterBySize(20))     # ['doc2.txt', 'data.csv']
print(directory.filterBySizeRange(10, 20))  # ['doc1.txt', 'doc2.txt', 'data.csv']
