from pymongo.mongo_client import MongoClient
from PIL import Image
import io
from yolo import Yolo

yl = Yolo()

class Database:
    def __init__(self):
        uri = "mongodb+srv://shiladityasarkar:Dy4hELTzhwWiQyuH@cluster.48ap8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"
        client = MongoClient(uri)
        db = client.segmentator
        self.key = None
        self.images = db.test
        self.users = db.users
        try:
            client.admin.command('ping')
            print("Ping! Successfully connected to MongoDB...")
        except Exception as e:
            print(e)

    def put_user(self, uname: str = None, pasw: str = None) -> None:
        self.users.insert_one({"uname": uname, "pasw": pasw})
        self.key = uname + pasw

    def get_user(self, uname: str = None, pasw: str = None):
        user = self.users.find_one({"uname": uname, "pasw": pasw})
        if user:
            self.key = uname + pasw
        return user

    def write(self, path:str = None):
        if self.key is None:
            return -1
        try:
            img = Image.open(path).convert('RGB')
        except (Exception,):
            return 'No file chosen!!!'
        print('THE PATH ISSS --- ', path)
        yl.run(path)
        yimg = Image.open('./temp/'+path).convert('RGB')
        img_bytes = io.BytesIO()
        yimg_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        yimg.save(yimg_bytes, format='JPEG')
        flter = {"key": self.key}
        update = {"$set":{"image": img_bytes.getvalue(), "yimg": yimg_bytes.getvalue()}}
        res = self.images.update_one(flter, update, upsert=True)
        if res.upserted_id is not None:
            return 'Uploaded Successfully!'
        return 'Updated Successfully!'


    def read(self):
        if self.key is None:
            return -1
        image = self.images.find_one({"key": self.key})
        if image is None:
            return None
        img_bytes = io.BytesIO(image['image'])
        yimg_bytes = io.BytesIO(image['yimg'])
        try:
            img = Image.open(img_bytes).convert('RGB')
            yimg = Image.open(yimg_bytes).convert('RGB')
        except Exception as e:
            return f'Error processing images: {e}'
        width = img.width + yimg.width
        height = max(img.height, yimg.height)
        combined_image = Image.new(mode='RGB', size=(width, height))
        combined_image.paste(img, (0, 0))
        combined_image.paste(yimg, (yimg.width, 0))
        img_combined_bytes = io.BytesIO()
        combined_image.save(img_combined_bytes, format='JPEG')
        return img_combined_bytes.getvalue()
