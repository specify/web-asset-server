import os, pickle
from anytree import Node, RenderTree
import iz_importer_config


class DirectoryTree():

    def __init__(self, directories):
        self.pickle_file = 'directory_tree.pickle'
        if os.path.exists(self.pickle_file):
            print("RESTORING FROM PICKLE")
            # load the directory tree from the pickle file
            with open(self.pickle_file, 'rb') as f:
                self.root_node = pickle.load(f)
        else:
            # build the directory tree by scanning the directory
            print("GENERATING PICKLE")

            self.root_node = None
            for directory in directories:
                if self.root_node is None:
                    self.root_node = self._build_tree(directory)
                    self.root_node.name = directory
                else:
                    self.add_directory(directory)

            # save the directory tree to a pickle file
            with open(self.pickle_file, 'wb') as f:
                pickle.dump(self.root_node, f)

    def _build_tree(self, root_path):
        # create a node for the root directory
        root_node = Node(os.path.basename(root_path))

        # traverse the directory structure recursively
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path):
                # recursively traverse subdirectories
                subdirectory_node = self._build_tree(item_path)
                subdirectory_node.parent = root_node
            else:
                # create a leaf node for each file
                Node(item, parent=root_node)

        return root_node

    def add_directory(self, root_path):
        # build a subtree rooted at the new root path
        new_root_node = self._build_tree(root_path)
        new_root_node.name = root_path
        new_root_node.parent = self.root_node

    def get_node_path(self,node):
        if node.is_root:
            return str(node.name)
        else:
            parent_path = self.get_node_path(node.parent)
            return f"{parent_path}/{node.name}"



    def print_tree(self):
        for pre, _, node in RenderTree(self.root_node):
            print(f'{pre}{node.name}')

    def process_files(self, func):
        for node in self.root_node.descendants:
            if not node.is_leaf:
                continue
            func(self.get_node_path(node))

    def get_node_from_path(self, full_path):
        path_parts = os.path.normpath(full_path).split(os.sep)

        node = self.root_node
        for part in path_parts:
            node = next((child for child in node.children if child.name == part), None)
            if node is None:
                return None

        return node

    def find_closest_decoder_ring(self, full_path):
        node = self.get_node_from_path(full_path)

        while node.parent is not None:
            for child in node.parent.children:
                if child.name == 'decoder_ring.tsv':
                    return child.path
            node = node.parent

        return node


if __name__ == '__main__':
    DIR = "/Volumes/images/izg/IZ/"
    print(f"Joe test: {DIR}")
    ring = DirectoryTree(iz_importer_config.IZ_CORE_SCAN_FOLDERS)
    ring.print_tree()
    #
    # def search_file(self, filename):
    #     # Traverse the tree from the given filename to the root node, checking for the target file along the way
    #     path = os.path.dirname(filename)
    #     while path != '/':
    #         full_path = os.path.join(path, filename)
    #         if os.path.exists(full_path):
    #             return full_path
    #         else:
    #             node = next(node for node in self.root.descendants if node.path == path)
    #             path = os.path.dirname(node.path)
    #
    #     # If the target file was not found, return None
    #     return None
