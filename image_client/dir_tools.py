import os
import botany_importer
import logging
import sys
from time import sleep

class DirTools:
    def __init__(self,callback, limit=None):
        self.logger = logging.getLogger('Client.DirTools')
        self.callback = callback
        self.processed_num = 0
        self.processed_limit = limit

    def get_full_path(self, filepath, filename):
        if filepath is None:
            full_path = filename
        else:
            dirnames = filepath.split(os.path.sep)
            for dirname in dirnames:
                if dirname.startswith('.') and len(dirname) > 1:
                    return
            if filepath.endswith(os.path.sep):
                full_path = f"{filepath}{filename}"
            else:
                full_path = f"{filepath}{os.path.sep}{filename}"
        return full_path


    def process_files_or_directories_recursive(self, path_names):
        if isinstance(path_names,str):
            path_names = [path_names]
        for path in path_names:
            for root, d_names, f_names in os.walk(path):
                for cur_file in f_names:
                    if self.processed_limit is not None and self.processed_num > self.processed_limit:
                        return
                    self.process_file(root,cur_file)


    def process_directory(self, dirpath):
        for file in os.listdir(dirpath):
            full_path = os.path.join(dirpath, file)
            if not os.path.isdir(full_path):
                if self.processed_limit is not None and self.processed_num > self.processed_limit:
                    return
                self.process_file(dirpath, file)


    def process_file_or_directory(self,file_list):
        for curfile in file_list:
            if self.processed_limit is not None and self.processed_num > self.processed_limit:
                return
            try:

                if os.path.isdir(curfile):
                    self.process_directory(curfile)
                else:

                    self.process_file(None,curfile)
            except botany_importer.DatabaseInconsistentError:
                print(f"Fatal, skipping: {curfile}")


    def process_file(self, filepath, filename):
        if self.processed_limit is not None and self.processed_num > self.processed_limit:
            return
        self.processed_num += 1

        self.logger.debug(f"Processing {filepath}{os.path.sep}{filename}")

        full_path = self.get_full_path(filepath, filename)
        if full_path is None:
            return
        try:
            self.callback(full_path)
        except (BlockingIOError, IOError, OSError) as e:
            print(f"Blocking I/O error: {e}\n\t on {full_path}, sleeping 10 minutes and retrying", file=sys.stderr, flush=True)
            sleep(60*10)
            self.process_file(filepath, filename)