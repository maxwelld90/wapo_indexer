import re
import os
import glob
import json
import datetime
from whoosh.fields import *
from whoosh import index
from wapo_indexer import __version__ as package_version
from bs4 import BeautifulSoup

class Indexer(object):
    """
    """
    def __init__(self, config, image_processor):
        self.__config = config
        self.__verbose = config['Index']['Verbose']
        self.__image_processor = image_processor
        self.__docid_list = self.__get_docid_list()
        self.__source_file_list = self.__get_source_file_list()
        self.__markup_pattern = re.compile('<.*?>')
        self.__schema = Schema(docid=TEXT(stored=True),
                               article_url=TEXT(stored=True),
                               title=TEXT(stored=True),
                               author=TEXT(stored=True),
                               published_date=DATETIME(stored=True),
                               kicker=TEXT(stored=True),
                               byline=TEXT(stored=True),
                               source=TEXT(stored=True),
                               body=TEXT(stored=True, vector=True),
                               body_front=TEXT(stored=True, vector=True),
                               body_back=TEXT(stored=True, vector=True),
                               author_bio=TEXT(stored=True),
                               images=TEXT(stored=True),
                               alltext=TEXT(stored=True),
                               lead_sentence=TEXT(stored=True))

        self.print_config()
        if index.exists_in(config['Index']['IndexPath']):
            self.__index = index.open_dir(config['Index']['IndexPath'])
        else:
            self.__index = index.create_in(config['Index']['IndexPath'], self.__schema)
        self.__writer = self.__index.writer(limitmb=config.getint('Index', 'CommitMB'))
    

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

        print()
    

    def __process_document(self, document_dict):
        """

        """
        keep_markup = self.__config.getboolean('Index', 'KeepMarkup')
        paragraph_break = self.__config['Index']['ParagraphBreak']
        image_counter = 0

        # If we are using a list of documents to index, ensure that it this document is to be indexed.
        if len(self.__docid_list) > 0:
            if document_dict['id'] not in self.__docid_list:
                return False

        try:
            dt = datetime.datetime.fromtimestamp(int(str(document_dict['published_date'])[:-3])) # Conversion to DateTime from UNIX timestamp
        except:
            dt = None
        
        indexing_dict = {
            'docid': document_dict['id'],
            'article_url': document_dict['article_url'],
            'title': document_dict['title'],
            'author': document_dict['author'],
            'published_date': dt,
            'kicker': '',
            'byline': '',
            'body': '',
            'body_front':'',
            'body_back':'',
            'author_bio': '',
            'images': [],
            'lead_sentence':'',
        }
        
        # Parse the contents data structure to extract the necessary details.
        for entry in document_dict['contents']:

            if entry is not None:

                if entry['type'] == 'kicker':
                    indexing_dict['kicker'] = entry['content']

                if entry['type'] == 'byline':
                    indexing_dict['byline'] = entry['content']

                if entry['type'] == 'sanitized_html':
                    processed_paragraph = entry['content']

                    if keep_markup:
                        indexing_dict['body'] = f"{indexing_dict['body']}<p>{processed_paragraph}</p>{paragraph_break}"
                    else:
                        indexing_dict['body'] = f"{indexing_dict['body']}{processed_paragraph}{paragraph_break}"

                    clean1 = re.compile('<a.*?>')
                    clean2 = re.compile('</a>')
                    clean_body = re.sub(clean1, '', indexing_dict['body'])
                    clean_body = re.sub(clean2, '', clean_body)
                    clean_body = clean_body.replace('\\n', '')
                    indexing_dict['body'] = clean_body

                    soup = BeautifulSoup(clean_body)
                    tags = soup.findAll('p')
                    ptags = [tag.prettify() for tag in tags]
                    if len(ptags) > 3:
                        indexing_dict['body_front'] = ' '.join(ptags[:3])
                        indexing_dict['body_back'] = ' '.join(ptags[3:])
                    else:
                        indexing_dict['body_front'] = ' '.join(ptags)

                    clean3 = re.compile('<.*?>')
                    clean_body = re.sub(clean3, '', clean_body)
                    sentences = clean_body.split('.')

                    #num_sentences = len(sentences)
                    lead_sentence = ''
                    #if num_sentences >= 1:
                    #    lead_sentence = f'{sentences[0]}.'
                    #if len(lead_sentence) < 200 and num_sentences > 1:
                    #    lead_sentence = f'{sentences[0]}. {sentences[1]}.'
                    if len(ptags) > 0:
                        lead_sentence =  ptags[0]
                        lead_sentence = re.sub(clean3, '', lead_sentence)
                        lead_sentence = lead_sentence.replace('\\','')

                    indexing_dict['lead_sentence'] = lead_sentence

                if entry['type'] == 'author_info':
                    indexing_dict['author_bio'] = entry['bio']

                # Process the image(s). Use the image processor to resize, save and make thumbnails if required.
                if self.__image_processor and entry['type'] == 'image':
                    processing_response = self.__image_processor.process_image(doc_id=indexing_dict['docid'],
                                                                               url=entry['imageURL'],
                                                                               image_number=image_counter)

                    if processing_response:
                        if 'fullcaption' in entry:
                            processing_response['fullcaption'] = entry['fullcaption']
                        indexing_dict['images'].append(processing_response)

                        image_counter += 1
        
        if not keep_markup:  # Removes all HTML markup if the appropriate setting has been made.
            body = re.sub(self.__markup_pattern, '', body)



        
        indexing_dict['body'] = indexing_dict['body'].strip(paragraph_break)
        return indexing_dict


    def index_document(self, indexing_dict):
        """

        """
        if self.__verbose:
            print(f" * Saving document {indexing_dict['docid']}...")

        try:
            self.__writer.add_document(docid=indexing_dict['docid'],
                                   article_url=indexing_dict['article_url'],
                                   title=indexing_dict['title'],
                                   author=indexing_dict['author'],
                                   published_date=indexing_dict['published_date'],
                                   kicker=indexing_dict['kicker'],
                                   byline=indexing_dict['byline'],
                                   body=indexing_dict['body'],
                                   body_front=indexing_dict['body_front'],
                                   body_back=indexing_dict['body_back'],
                                   source='Washington Post',
                                   author_bio=indexing_dict['author_bio'],
                                   images=json.dumps(indexing_dict['images']),
                                   alltext=f"{indexing_dict['title']} {indexing_dict['author']} {indexing_dict['body']}",
                                   lead_sentence=indexing_dict['lead_sentence'] )

        except struct.error as e:
            d_id = indexing_dict['doc_id']
            print(f'Error {e} was encountered with document {d_id}')

        except Exception as ef:
            d_id = indexing_dict['doc_id']
            print(f'Exception {ef} occurred, check error.txt\n')


    def __process_file(self, f):
        """

        """
        for line in f:  # Each line corresponds to a unique document.
            line = line.strip()
            document_dict = json.loads(line)
            indexing_dict = self.__process_document(document_dict)

            if indexing_dict:
                self.index_document(indexing_dict)
    

    def index(self):
        """
        Each line corresponds to a document.
        """
        for source_file in self.__source_file_list:
            if self.__verbose:
                print(f' * Opening source file \'{source_file}\'...')
            f = open(source_file, 'r')
            self.__process_file(f)

            f.close()
        
        if self.__verbose:
            print(" * Completed.")
        
        self.__writer.commit(optimize=True)
        self.__index.close()
