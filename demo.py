# coding:utf-8


import time
import click

from jpeg import JPEG
from numpy import empty
from imarray import imarray


FPATH = "images/Lenna.jpg"


# cmd group
@click.group()
def cmd():
    pass


# run demo
@cmd.command(help="")
@click.argument('fpath', type=click.Path(), default=FPATH)
def run(fpath):

    # load target file
    print "loading image: {}".format(fpath)
    imArray = imarray.load(fpath)

    # construct jpeg
    jpeg  = JPEG()

    # encode image
    encoded_dc_components, encoded_ac_components, shape = jpeg.encode(imArray)
    print u"↑ Huffman Table of DC Components"

    # decode image
    decoded_imArray = jpeg.decode(encoded_dc_components, encoded_ac_components, shape)

    # concatenate and show images
    shape_x, shape_y = imArray.shape
    result = imarray(empty((shape_x*2, shape_y)))

    # upper image is original, lower image is compressed
    result[0:shape_x, 0:shape_y] += imArray
    result[shape_x:shape_x*2, 0:shape_y] += decoded_imArray
    result.show()


def main():
    cmd(obj={})


if __name__ == "__main__":
    main()
