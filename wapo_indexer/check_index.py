#
# WAPO Check Index
# Author: Leif
# Date: 2021-12-12
#
import sys
import configparser

from whoosh.fields import *
from whoosh import index


def load_config_dict(path):
    """
    Loads the configuration file using a ConfigParser, and returns the object.
    """
    config = configparser.ConfigParser()
    config.read('wapo_indexer/defaults.config')
    config.read(path)

    return config

def main(config):
    ip = config['Index']['IndexPath']
    if index.exists_in(ip):
        print(f'Opening {ip}:')
        ix = index.open_dir(ip)
        searcher = ix.searcher()
        numdocs = searcher.doc_count_all()
        print(f'The number of documents in the index is: {numdocs}')
        print(ix.schema.names())
    else:
        print(f'Index {fp} does not exist!')



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python check_index.py <config_path>", file=sys.stderr)
        print("Where:", file=sys.stderr)
        print("    <config_path>: Path to configuration file (see sample.config)")
        sys.exit(1)

    config_path = sys.argv[1]
    config = load_config_dict(config_path)
    main(config)