import os
import glob
import json
import datetime
from wapo_indexer import __version__ as package_version

class Indexer(object):
    """

    """
    def __init__(self, config, image_processor):
        self.__config = config
        self.__image_processor = image_processor

        self.__docid_list = self.__get_docid_list()
        self.__source_file_list = self.__get_source_file_list()
    

    def __get_docid_list(self):
        """

        """
        docid_list = []

        if 'IncludeDocIDListPath' in self.__config['Source']:
            f = open(self.__config['Source']['IncludeDocIDListPath'])

            for line in f:
                docid_list.append(line.strip())
                
        
        return docid_list
    
    def __get_source_file_list(self):
        """

        """
        file_list = []
        listing = os.listdir(self.__config['Source']['SourcePath'])
        
        for entry in listing:
            if entry.startswith('.') or entry.lower() == 'thumbs.db':  # Ignore hidden files (e.g. .DS_Store, Windows directory layout)
                continue

            full_path = os.path.join(self.__config['Source']['SourcePath'], entry)

            if os.path.isfile(full_path):
                file_list.append(full_path)
        
        return file_list

    
    def print_config(self):
        """

        """
        os.system('cls')
        os.system('clear')
        print(f"WAPO Indexer version {package_version}")

        # Source configuration
        print(f"    Source base directory is {self.__config['Source']['SourcePath']}")

        if len(self.__docid_list) == 0:
            print(f"    All documents within source files to be indexed.")
        else:
            print(f"    {len(self.__docid_list)} document(s) to be indexed.")
            print(f"    Document list from file {self.__config['Source']['IncludeDocIDListPath']}")

        # Index configuration


        # Image configuration
    

    def index(self):
        """
        Each line corresponds to a document.
        """
        indexed_document_count = 0
        
        for source_file in self.__source_file_list:
            f = open(source_file, 'r')

            for line in f:  # Each line corresponds to a unique document.
                line = line.strip()
                document_dict = json.loads(line)

                # If we are using a list of documents to index, ensure that it this document is to be indexed.
                if len(self.__docid_list) > 0:
                    if document_dict['id'] not in self.__docid_list:
                        continue
                
                print(document_dict['id']) # Doc ID

                print(document_dict['article_url']) # Original URL

                print(document_dict['title']) # Doc Title

                print(document_dict['author']) # Doc Author

                print(str(document_dict['published_date'])[:-3]) # Date (UNIX timestamp, wit three trailing zeroes, removed)
                print(datetime.datetime.fromtimestamp(int(str(document_dict['published_date'])[:-3])))  # Conversion to DateTime

                for entry in document_dict['contents']:
                    print(entry)

                # TESTING
                break


            f.close()