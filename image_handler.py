import logging
import os
import subprocess
import shutil
from watchdog.events import PatternMatchingEventHandler, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent
from PIL import Image
from typing import Tuple, List

class ImageHandler(PatternMatchingEventHandler):
    
    def __init__(self, size_ratio:float=1.0, dest_path:str=None):
        super().__init__(patterns=['*.png'], ignore_directories=True)
        self._size_ratio:float = size_ratio
        self._dest_path:str = dest_path
        self._logger:logging.Logger = logging.getLogger('com.ImageHandler')

    def on_created(self, event:FileCreatedEvent):
        self._logger.debug('New file detected {path}'.format(path = event.src_path))
        self._reduce_image_size(self._resize(event.src_path))

    def on_deleted(self, event:FileDeletedEvent):
        self._logger.debug('File deletion detected {path}'.format(path = event.src_path))
        self._remove_file(event.src_path)

    def on_modified(self, event:FileModifiedEvent):
        self._logger.debug('File modification detected {path}'.format(path = event.src_path))
        self._reduce_image_size(self._resize(event.src_path))

    def on_moved(self, event:FileMovedEvent):
        self._logger.debug('File move detected from {src_path} to {dest_path}'.format(src_path = event.src_path, dest_path = event.dest_path))
        self._reduce_image_size(self._resize(event.dest_path))

    def _compute_dest_path(self, input_path:str) -> str:
        '''
        Computes dest path for given input path
        '''

        path_components:Tuple[str, str] = os.path.split(input_path)
        return os.path.join(self._dest_path, path_components[1])

    def _resize(self, image_path:str) -> str:
        '''
        Resizes source image path if necessary, returns the new image path
        '''

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

        path_components:Tuple[str, str] = os.path.split(image_path)
        dest_image_path:str = os.path.join(self._dest_path, path_components[1])

        if os.path.exists(dest_image_path):
            os.remove(dest_image_path)

    def _reduce_image_size(self, src_path:str) -> None:
        '''
        Uses pngquant to reduce image size
        '''

        command_args:List[str] = ['pngquant', src_path]
        command_result:subprocess.CompletedProcess = subprocess.run(command_args)
        self._logger.debug('pngquant executed {data}'.format(data = command_result))
        os.remove(src_path)

