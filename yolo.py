from ultralytics import YOLO

class Yolo:
    def __init__(self):
        self.model = YOLO('yolov8n-seg.pt')

    def run(self, path:str = None) -> None:
        self.model(source=path, project='.', name='temp', save=True, exist_ok = True)