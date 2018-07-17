import logging
import os
import subprocess
import shutil
import humanfriendly
import time
from watchdog.events import PatternMatchingEventHandler, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent
from PIL import Image
from typing import Tuple, List

class ProcessingContext(object):

    def __init__(self, src_img_path:str):
        self.src_img_path:str = src_img_path
        self.src_img_size:int = os.path.getsize(src_img_path)
        self._dest_img_path:str = None
        self.dest_img_size:int = None
        self.start:float = time.time()

    @property
    def dest_img_path(self) -> str:
        return self._dest_img_path

    @dest_img_path.setter
    def dest_img_path(self, img_path:str) -> None:
        self._dest_img_path = img_path
        self.dest_img_size = os.path.getsize(img_path)

    def print_statistics(self, logger:logging.Logger) -> None:
        params = {
            'src_path': self.src_img_path, 
            'initial_size': humanfriendly.format_size(self.src_img_size), 
            'final_size': humanfriendly.format_size(self.dest_img_size),
            'compression': 1 - (self.dest_img_size/self.src_img_size),
            'divider': '=' * 30,
            'total_time': time.time() - self.start
        }
        logger.info('Image stats:\nSource: {src_path}\nInitial Size: {initial_size:>15}\nFinal Size: {final_size:>17}\nCompression: {compression:>16.2%}\nTime: {total_time:>21.2} s\n{divider}'.format(**params))

class ImageHandler(PatternMatchingEventHandler):
    
    def __init__(self, size_ratio:float=1.0, dest_path:str=None):
        super().__init__(patterns=['*.png'], ignore_directories=True)
        self._size_ratio:float = size_ratio
        self._dest_path:str = dest_path
        self._logger:logging.Logger = logging.getLogger('com.ImageHandler')
        self._ext:str = '-new.png'

    def on_created(self, event:FileCreatedEvent):
        self._logger.debug('New file detected {path}'.format(path = event.src_path))
        context:ProcessingContext = ProcessingContext(event.src_path)
        intermediate_file:str = self._resize(context)
        self._reduce_image_size(intermediate_file, context)
        context.print_statistics(self._logger)

    def on_deleted(self, event:FileDeletedEvent):
        self._logger.debug('File deletion detected {path}'.format(path = event.src_path))
        self._remove_file(event.src_path)

    def on_modified(self, event:FileModifiedEvent):
        self._logger.debug('File modification detected {path}'.format(path = event.src_path))
        context:ProcessingContext = ProcessingContext(event.src_path)
        intermediate_file:str = self._resize(context)
        self._reduce_image_size(intermediate_file, context)
        context.print_statistics(self._logger)

    def on_moved(self, event:FileMovedEvent):
        self._logger.debug('File move detected from {src_path} to {dest_path}'.format(src_path = event.src_path, dest_path = event.dest_path))
        context:ProcessingContext = ProcessingContext(event.dest_path)
        intermediate_file:str = self._resize(context)
        self._reduce_image_size(intermediate_file, context)
        context.print_statistics(self._logger)

    def _compute_dest_path(self, input_path:str) -> str:
        '''
        Given the input file path it computes the destination file path
        '''

        path_components:Tuple[str, str] = os.path.split(input_path)
        return os.path.join(self._dest_path, path_components[1])

    def _compute_compressed_file_path(self, input_file_path:str) -> str:
        '''
        Given the input file path it computes the compressed file path
        '''

        path_components:Tuple[str, str] = os.path.split(input_file_path)
        filename_components:Tuple[str, str, str] = path_components[1].rpartition('.png')
        dest_image_path:str = os.path.join(self._dest_path, filename_components[0] + self._ext)
        return dest_image_path

    def _resize(self, context:ProcessingContext) -> str:
        '''
        Resizes source image path if necessary, returns the new image path
        '''

        image_path:str = context.src_img_path
        dest_image_path:str = self._compute_dest_path(image_path)

        if self._size_ratio == 1.0 or self._size_ratio is None:
            return shutil.copy2(image_path, self._dest_path)

        with open(image_path, 'rb') as file:
            img:Image.Image = Image.open(file)
            new_img:Image.Image = img.resize(((int(img.width * self._size_ratio), int(img.height * self._size_ratio))), Image.LANCZOS)
            path_components:Tuple[str, str] = os.path.split(image_path)
            dest_image_path = os.path.join(self._dest_path, path_components[1])
            new_img.save(dest_image_path, None, compress_level=0)

        return dest_image_path

    def _remove_file(self, image_path:str) -> None:
        '''
        Deletes file in dest directory if present
        '''

        dest_image_path:str = self._compute_compressed_file_path(image_path)

        if os.path.exists(dest_image_path):
            os.remove(dest_image_path)

    def _reduce_image_size(self, src_path:str, context:ProcessingContext) -> None:
        '''
        Uses pngquant to reduce image size
        '''

        subprocess.run(['pngquant', '--ext', self._ext, src_path])
        final_image_path:str = self._compute_compressed_file_path(src_path)
        context.dest_img_path = final_image_path
        os.remove(src_path)