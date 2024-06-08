# auxillary program used for gathering saves for further analysis

import argparse
import os
import shutil
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileUpdateHandler(FileSystemEventHandler):
    def __init__(self, file_to_watch, destination_directory):
        self.file_to_watch = file_to_watch
        self.destination_directory = destination_directory
        self.copy_count = 0

    def on_modified(self, event):
        if event.src_path == self.file_to_watch:
            print(f"{self.file_to_watch} has been updated")
            self.copy_file()

    def on_any_event(self, event):
        print(event)

    def copy_file(self):
        self.copy_count += 1
        new_filename = f"autosave_{self.copy_count}"
        destination_path = os.path.join(self.destination_directory, new_filename)
        shutil.copy(self.file_to_watch, destination_path)
        print(f"Copied {self.file_to_watch} to {self.destination_directory}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor changes in save games for a singular campaign')
    parser.add_argument('file_to_watch', type=str, help='The path of the autosave file')
    parser.add_argument('destination_directory', type=str,
                        help='The destination to which watched files should be added')

    args = parser.parse_args()
    if args[0] == 'auto':
        file_to_watch = "C:\\Users\\Wajha\\Documents\\Paradox Interactive\\Victoria 3\\save games\\autosave.v3"
    else:
        file_to_watch = args[0]
    destination_directory = args[1]
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    shutil.copy(file_to_watch,destination_directory)

    event_handler = FileUpdateHandler(file_to_watch, destination_directory)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(file_to_watch), recursive=False)
    observer.start()

    print(f"Monitoring {file_to_watch} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping watcher")
        observer.stop()
    observer.join()
