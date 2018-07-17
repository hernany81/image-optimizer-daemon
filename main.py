import logging
import logging.config
import sys
import time
import argparse

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

    # Command line processing
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description='Command to reduce image size and lossless compression')
    parser.add_argument('inputDir', help='Input directory to be monitored')
    parser.add_argument('outputDir', help='Output directory where transformed images will be saved')
    parser.add_argument('-r', '--ratio', type=float, default=1.0, help='Reduce size ratio, from 0.0 to 1.0, default: 1.0')
    args = parser.parse_args()

    # Image handler setup
    observer:Observer = Observer()
    event_handler:ImageHandler = ImageHandler(size_ratio=args.ratio, dest_path=args.outputDir)
    observer.schedule(event_handler, args.inputDir)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join
