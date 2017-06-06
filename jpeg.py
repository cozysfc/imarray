# coding:utf-8


import os
import sys

from imarray import imarray
from numpy import array, ones, zeros, empty, arange, meshgrid, cos, pi, sum, multiply, sqrt


class JPEG:
    """
    Transform array into jpeg formatted imarray.

    usage
    -----
    # In constructor, dct components will be generated.
    jpeg = JPEG(8)

    # JPEG.compress will return compressed imarray.
    # The erasing range of high frequency components
    # will be setted by arguments (level_i, level_j).
    imArray = imarray.load('Lenna.jpg')
    compressed = jpeg.compress(imArray, level_i=2, level_j=2)

    # Show compressed imarray.
    imarray(compressed).show()

    # Save compressed imarray.
    imarray(compressed).save('compressed.jpg')
    """

    def __init__(self, N=8):
        self.N = N
        self.dct = DCT(N)

    def compress(self, imArray, level_i=0, level_j=0):
        # Prepare space domain empty matrix.
        s_domain = imarray(empty(imArray.shape))

        # Slice imArray into (N, N) shaped imarray.
        for (w1,w2),(h1,h2),im in imArray.slice(width=self.N, height=self.N):
            # Compute frequency domain.
            toFreq_result  = self.dct.toFreq(im)

            # Erase high frequency components in 0:level_i to 0:level_j.
            toFreq_result[level_i:,level_j:] = 0

            # Compute space domain.
            toSpace_result = self.dct.toSpace(toFreq_result)
            s_domain[w1:w2, h1:h2] = toSpace_result

        return s_domain


class DCT:
    """
    Two dimentional discrete cosine transformation.

    Usage
    -----
    # Precompute base components matrix of dct.
    dct = DCT(N=8)

    # Transform into frequency domain matrix.
    # X should be 2d array (list or numpy.ndarray)
    # with smaller shape than (N, N).
    F = dct.toFreq(X)

    # Transform into space domain matrix.
    S = dct.toSpace(F)
    """

    def __init__(self, N=8):
        # range of frequency domain
        self.N = N

        # precompute 1d dct base components
        self.base = lambda k: ones(N)/sqrt(N) if k==0 else sqrt(2.0/N)*cos((k*pi/(2*N))*(arange(N)*2+1))
        self.base = [self.base(k) for k in xrange(N)]

        # precompute 2d dct base components
        self.components = [multiply(*meshgrid(self.base[i],self.base[j])) for i in xrange(N) for j in xrange(N)]
        self.components = array(self.components).reshape(N, N, N, N)

    def toFreq(self, X):
        N = self.N

        # if X is smaller than (N, N),
        # X will be padded zero to reshape (N, N)
        X_i, X_j = X.shape
        if X.shape != (N, N):
            _X = zeros((N, N))
            _X[:X_i,:X_j] = X[:X_i,:X_j]
            X = _X

        ret =  sum(self.components.reshape(N**2,N**2)*X.reshape(N**2),axis=1)
        return ret.reshape(N,N)[:X_i,:X_j]

    def toSpace(self, F):
        N = self.N

        # if F is smaller than (N, N),
        # F will be padded zero to reshape (N, N)
        F_i, F_j = F.shape
        if F.shape != (N,N):
            _F = zeros((N,N))
            _F[:F_i,:F_j] = F[:F_i,:F_j]
            F = _F

        ret = sum((F.reshape(N,N,1)*self.components.reshape(N,N,N**2)).reshape(N**2,N**2),axis=0)
        return ret.reshape(N,N)[:F_i,:F_j]
