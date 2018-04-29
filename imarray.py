# coding:utf-8


import cPickle as pickle

from PIL import Image, ImageOps
from numpy import ndarray, asarray, meshgrid, empty, uint8, max, min


class imarray(ndarray):
    """
    Image object based on numpy.ndarray.

    Usage
    ------
    # Initialize from array
    imArray = imarray(np.range(100))
    imArray = imarray(range(100))
    imArray = imArray.reshape(10,10)

    # Initialize from image
    imArray = imarray.load("Lenna.png")

    # Convert to PIL.Image
    print imArray.toimage()

    # Slice image
    imarray.split(imArray, width=100, height=100)

    # Preview image
    imArray.show()

    # Save imarray
    imArray.save('Lenna.imarray')

    # Load imarray
    imArray = imarray.load('Lenna.imarray')
    """

    def __new__(cls, array=[], scale=False):
        if isinstance(array, ndarray) or isinstance(array, list):
            self = asarray(array).view(cls)

            if scale:
                self = imarray.uint8scale(self)
                self = self.astype(uint8)

            self.ishape = self.shape
        else:
            raise ValueError, "input must be list or ndarray"

        self.flags.writeable = True
        self.fpath = None

        return self

    @classmethod
    def fromimage(cls, fpath, grayscale=True):
        with Image.open(fpath) as img:
            if grayscale:
                img = img.convert("L")

            self = asarray(img).view(cls)
            self.ishape = img.size

        self.flags.writeable = True
        self.fpath = fpath

        return self

    def save(self, fpath):
        if fpath[::-1][:8][::-1] == ".imarray":
            with open(fpath, "wb") as wfp:
                pickle.dump(self, wfp)
        else:
            self.toimage().convert("RGB").save(fpath)

    @staticmethod
    def load(fpath, grayscale=True):
        if fpath[::-1][:8][::-1] == ".imarray":
            with open(fpath, "rb") as rfp:
                ret = pickle.load(rfp)
        else:
            ret = imarray.fromimage(fpath, grayscale)

        return ret

    def toimage(self):
        return Image.fromarray(self)

    def slice(self, width=8, height=8, _enumerate=False):
        w, h = self.shape
        if _enumerate:
            for idx_i, i in enumerate(xrange(0, w, width)):
                for idx_j, j in enumerate(xrange(0, h, height)):
                    yield (idx_i,idx_j), (i,i+width), (j,j+height), self[i:i+width,j:j+height]
        else:
            for i in xrange(0, w, width):
                for j in xrange(0, h, height):
                    yield (i,i+width), (j,j+height), self[i:i+width,j:j+height]

    def show(self, force=False, scale=False):
        if self.size > 15000000:
            if force == False:
                print "too big image size, use force option"
                return -1

        if scale:
            Image.fromarray(self.astype(uint8)).show()
        else:
            Image.fromarray(self).show()

    @staticmethod
    def uint8scale(array):
        if len(array) > 0:
            mins = min(array)
            maxs = max(array)
            rng  = mins-maxs if mins-maxs else .1
            ret  = 255-255*(maxs-array)/rng

        return ret
