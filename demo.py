# coding:utf-8


import os
import sys
import numpy as np

from jpeg import JPEG
from imarray import imarray


TARGET_IMAGE = "images/Lenna.jpg"
OUTPUT_PATH  = "images/Lenna-8x8.jpg"


if __name__ == "__main__":
    # load target file
    imArray = imarray.load(TARGET_IMAGE)

    # construct jpeg
    jpeg  = JPEG()

    # compress target file
    # for each level_i,j (i=0~8, j=0~8)
    result = [(i, j, jpeg.compress(imArray, level_i=i, level_j=j))
            for i in range(8)
            for j in range(8)]

    # concatenate into 8x8
    w, h = imArray.shape
    concatenate = np.zeros((8*w, 8*h))

    for i, j, x in result:
        concatenate[i*w:(i+1)*w, j*h:(j+1)*h] += x

    # save image
    imarray(concatenate).save(OUTPUT_PATH)
