import os
import io
import time
import datetime
#import urllib.request
from PIL import Image
import requests

class ImageProcessor(object):
    """

    """
    def __init__(self, config):
        self.__config = config
        self.__verbose = config.getboolean('Index', 'Verbose')
        self.__enable_processing = config.getboolean('Images', 'SaveImages')

        self.__base_path = os.path.join(config['Index']['IndexPath'], config['Images']['ImagesPath'])
        self.__original_path = 'original'
        self.__thumbnail_path = 'thumbails'
        self.__thumbnail_dimensions = self.__config.getint('Images', 'ThumbnailDimension'), self.__config.getint('Images', 'ThumbnailDimension')

        self.__generate_thumbnails = self.__config.getboolean('Images', 'GenerateThumbnails')
        self.__last_access_time = datetime.datetime.now()  # When was an image last retrieved?
        self.__access_delay = self.__config.getint('Images', 'DownloadDelay')

        self.__create_directories()

    
    def __create_directories(self):
        """

        """
        if not os.path.exists(os.path.join(self.__base_path, self.__original_path)):
            os.makedirs(os.path.join(self.__base_path, self.__original_path))
        
        if self.__generate_thumbnails and not os.path.exists(os.path.join(self.__base_path, self.__thumbnail_path)):
            os.makedirs(os.path.join(self.__base_path, self.__thumbnail_path))
    
    def process_image(self, doc_id, url, image_number=0):
        """

        """
        return_paths = {}

        if not self.__enable_processing:
            return False

        if self.__verbose:
            print( f'  * Downloading image for document {doc_id} ...' )

        tmp_path = os.path.join(self.__base_path, self.__original_path, f'{doc_id}_i{image_number}.tmp')
        tmp_download_path = tmp_path + '.download'
        original_path = os.path.join(self.__base_path, self.__original_path, f'{doc_id}_i{image_number}.jpg')
        thumbnail_path = os.path.join(self.__base_path, self.__thumbnail_path, f'{doc_id}_i{image_number}_t.jpg')

        # Sleep/block if a sufficient gap has not yet been reached between the last access and the one to make here.
        if self.__last_access_time is not None and self.__access_delay > 0:
            delta = (datetime.datetime.now() - self.__last_access_time).seconds
            if delta < self.__access_delay:
                time.sleep(delta)


        if os.path.exists(tmp_download_path):
            print("Previously tried to download, convert and save, but failed.", tmp_download_path)
            return False

        if not os.path.exists(tmp_path):
            # Attempt to read the image from the server. If this fails, return False.
            try:
                totalbits = 0
                response = requests.get(url)
                if response.status_code == 200:
                    with open(tmp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                totalbits += 1024
                                f.write(chunk)
                        print("Downloaded", totalbits / 1024 / 1024, "MB...")
                else:
                    print("Response code not 200")
                #response = urllib.request.urlopen(url)
                #image_file = io.BytesIO(response.read())
                # Create a PIL object from the downloaded image.
                #image = Image.open(image_file)
                #image_file.close()
            except:  # 404, server not available, etc. -- fallback to failure.
                print("Download Failed: ", tmp_path)
                with open(tmp_download_path, 'w') as fp:
                    fp.close()
                return False

        if not os.path.exists(tmp_path):
            print("Image not downloaded: ", tmp_path)
            with open(tmp_download_path, 'w') as fp:
                fp.close()
            return False

        try:

            image = Image.open(tmp_path)

            w,h = image.size
            print(w, h)

            if w*h > 7000000:
                image.close()
                return False
            image = image.resize((400, int(h/w*400)), Image.NEAREST)

            image.convert('RGB')
        except:
            print("Image Conversion Failed")

        try:
            image.save(original_path, 'JPEG')  # Save the original image as-is.

            if self.__generate_thumbnails:
                image.thumbnail(self.__thumbnail_dimensions)  # Resize to the dimensions provided for a thumbnail, and save.
                image.save(thumbnail_path, 'JPEG')


            image.close()

            self.__last_access_time = datetime.datetime.now()  # Update the last access time.


            return_paths['original'] = os.path.join(self.__original_path, f'{doc_id}_i{image_number}.jpg')

            if self.__generate_thumbnails:
                return_paths['thumbnail'] = os.path.join(self.__thumbnail_path, f'{doc_id}_i{image_number}_t.jpg')
        except:
            print("Image save failed")
            with open(tmp_download_path, 'w') as fp:
                fp.close()
            return False
        return return_paths
