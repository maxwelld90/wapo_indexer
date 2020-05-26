#
# WAPO Indexer
# Author: David Maxwell
# Date: 2020-05-26
#

import sys
import configparser
from wapo_indexer.image_processor import ImageProcessor
from wapo_indexer.indexer import Indexer

def load_config_dict(path):
    """
    Loads the configuration file using a ConfigParser, and returns the object.
    """
    config = configparser.ConfigParser()
    config.read('wapo_indexer/defaults.config')
    config.read(path)

    return config


def instantiate_image_processor(config):
    """
    Given a configuration, returns an image processor object.
    If no image processing is required, None is returned.
    """
    if 'Images' in config:
        return ImageProcessor(config)
    
    return None


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python -m wapo_indexer <config_path>", file=sys.stderr)
        print("Where:", file=sys.stderr)
        print("    <config_path>: Path to configuration file (see sample.config)")
        sys.exit(1)
    
    config_path = sys.argv[1]
    config = load_config_dict(config_path)

    image_processor = instantiate_image_processor(config)
    
    indexer = Indexer(config, image_processor)
    #indexer.print_config()
    indexer.index()