import logging
import logging.config
import sys
import time
from watchdog.observers import Observer
from image_handler import ImageHandler

if __name__ == "__main__":
    logging.config.dictConfig(dict(
        version = 1,
        formatters = {
            'f': {
                'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
            }
        },
        handlers = {
            'h': {
                'class': 'logging.StreamHandler',
                'formatter': 'f',
                'level': logging.DEBUG
            }
        },
        root = {
            'handlers': ['h'],
            'level': logging.DEBUG,
        },
    ))

    observer:Observer = Observer()
    event_handler:ImageHandler = ImageHandler(size_ratio=0.75, dest_path='/Users/hernanyamakawa/Desktop/screenshots-min')
    observer.schedule(event_handler, '/Users/hernanyamakawa/Desktop/screenshots')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join
