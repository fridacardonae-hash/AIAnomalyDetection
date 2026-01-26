from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from datetime import datetime
import threading


class AOIWatchdogHandler(FileSystemEventHandler):
    def __init__(self, inspector):
        self.inspector = inspector

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        print("file_path", file_path)
        file_name = os.path.basename(file_path)


        corr1 = self.inspector.file_config["Image_correlation1"]
        corr2 = self.inspector.file_config["Image_correlation2"]
        corr3 = self.inspector.file_config["Image_correlation3"]
        

        if file_name not in (corr1, corr2, corr3):
            corr4 = self.inspector.file_config["Image_correlation4"]
            corr5 = self.inspector.file_config["Image_correlation5"]
            corr6 = self.inspector.file_config["Image_correlation6"]
            if file_name not in (corr4, corr5, corr6):
                return

        cam_folder = os.path.dirname(file_path)
        if os.path.basename(cam_folder) != "Cam1":
            return

        isn_path = os.path.dirname(cam_folder)
        create_time = datetime.fromtimestamp(os.path.getctime(isn_path))
        if create_time <= self.inspector.start_time:
            return
        isn = os.path.basename(isn_path)

        if isn in self.inspector.processed_folders:
            return

        print(f"Imagen detectada: {file_name} para ISN {isn}")

        self.inspector._try_process_isn(isn, cam_folder)