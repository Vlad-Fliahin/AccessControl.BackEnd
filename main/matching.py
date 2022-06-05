import base64
import os
from PIL import Image
import io

PATH = path = os.getcwd().rsplit('/', 1)[0] + '/media/pics/'


def convert():
    with open('/Users/fliahin/Desktop/test2.bmp', 'rb') as image:
        b64string = base64.b64encode(image.read())

    # decodeit.write(base64.b64decode((byte)))

    print(b64string)
    print(b64string.decode('ascii'))


if __name__ == '__main__':
    convert()
    # convert('test.BMP')
    # convert('test2.bmp')
