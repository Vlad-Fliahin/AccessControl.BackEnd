import base64
import os
from PIL import Image
import io


def convert(path):
    with open(f"{path}1__M_Left_index_finger.BMP", "rb") as image:
        b64string = base64.b64encode(image.read())
    print(b64string)

    f = io.BytesIO(base64.b64decode(b64string))
    pilimage = Image.open(f)

    print("d")


if __name__ == '__main__':
    path = os.getcwd()[:-4] + 'media/pics/'
    convert(path)
