

class ImageProcessor(object):
    """

    """
    def __init__(self, config):
        self.__config = config
        self.__base_path = config['Images']['ImagesPath']
    
    def process_image(self, url):
        pass