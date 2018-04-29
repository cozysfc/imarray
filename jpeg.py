# coding:utf-8


import os
import sys

from imarray import imarray
from numpy import (
    array,
    ones,
    zeros,
    empty,
    arange,
    meshgrid,
    cos,
    pi,
    sum,
    multiply,
    sqrt,
    int16,
    float16,
)

from huffman_encoder import HuffmanEncoder
from zero_length_encoder import ZeroLengthEncoder


# Luminance quantization matrix.
QUANTIZATION_MATRIX = array(
    [
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68,109,103, 77],
        [24, 35, 55, 64, 81,104,113, 92],
        [49, 64, 78, 87,103,121,120,101],
        [72, 92, 95, 98,112,100,103, 99]
    ],
    dtype=int16
)

# Scanning order of quantized DCT cofficient.
ZIGZAG_ORDER = [
     0,  1,  8, 16,  9,  2,  3, 10,
    17, 24, 32, 25, 18, 11,  4,  5,
    12, 19, 26, 33, 40, 48, 41, 34,
    27, 20, 13,  6,  7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36,
    29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46,
    53, 60, 61, 54, 47, 55, 62, 63
]


class JPEG:
    """
    Experimental implementation of JPEG Compression.

    usage
    -----
    # Load target file.
    imArray = imarray.load("images/Lenna.jpg")

    # In constructor, dct components will be generated.
    jpeg  = JPEG(8)

    # Encode imArray.
    encoded_dc_units, encoded_ac_units, shape = jpeg.encode(imArray)

    # Decode imArray.
    imArray = jpeg.decode(encoded_dc_units, encoded_ac_units, shape)

    # JPEG.decode will return compressed imarray.
    # Try imarray.show to preview image.
    imArray.show()
    """
    def __init__(self, N=8, quantization_matrix=QUANTIZATION_MATRIX):
        self.N = N
        self.dct = DCT(N)
        self.quantization_matrix = quantization_matrix

    def encode(self, imArray):
        # AC components.
        diff_dc_components = []

        # Units of DC components.
        encoded_ac_units = []

        # Slice imArray into (N, N) shaped Minimum Coded Unit.
        for (w1,w2),(h1,h2),im in imArray.slice(width=self.N, height=self.N):
            # Compute frequency domain.
            toFreq_result  = self.dct.toFreq(im)

            # Quantize frequency components.
            try:
                quantized = toFreq_result/self.quantization_matrix
                quantized = quantized.reshape(8*8).astype(int16)
            except:
                sx, sy = toFreq_result.shape
                quantized = toFreq_result/self.quantization_matrix[:sx, :sy]
                quantized = quantized.reshape(sx*sy).astype(int16)

            # Scan DCT cofficients by zigzag order.
            try:
                zigzag_sequence = [quantized[i] for i in ZIGZAG_ORDER]
            except:
                zigzag_sequence = [quantized[i] for i in ZIGZAG_ORDER if i < len(quantized)]

            # Dump diff values of each DC components.
            if len(diff_dc_components) == 0:
                diff_dc_components.append(quantized[0])
            else:
                diff_dc_components.append(quantized[0] - prev_dc_value)
            prev_dc_value = quantized[0]

            # Compress AC components by Zero Length Encoder.
            ac_components = zigzag_sequence[1:]
            print ac_components
            zero_length_encoded_components = ZeroLengthEncoder.encode(ac_components)

            # Additionaly compress AC components by Huffman Encoder.
            huffman_encoder = HuffmanEncoder(zero_length_encoded_components)
            compressed_ac_components = huffman_encoder.encode(zero_length_encoded_components)

            # Dump compressed AC components with Huffman Table.
            encoded_ac_units.append(
                [
                    compressed_ac_components,
                    huffman_encoder.code2value
                ]
            )

        # Compress diff values of each DC components by Huffman Encoder.
        huffman_encoder = HuffmanEncoder(diff_dc_components)
        compressed_dc_components = huffman_encoder.encode(diff_dc_components)

        # Show Huffman Table for DC components.
        print huffman_encoder

        # Dump compressed DC components with Huffman Table.
        encoded_dc_units = [
            compressed_dc_components,
            huffman_encoder.code2value
        ]

        return encoded_dc_units, encoded_ac_units, imArray.shape

    @staticmethod
    def decode(encoded_dc_units, encoded_ac_units, shape, N=8):
        # Construct DCT and empty imarray.
        dct = DCT(N)
        imArray = imarray(empty(shape))

        # Decode Huffman Coded DC components.
        dc_components = []
        compressed_dc_components, code2value = encoded_dc_units
        diff_dc_components = [int(code2value[s]) for s in compressed_dc_components]
        prev_dc_value = 0
        for diff in diff_dc_components:
            dc_components.append(diff+prev_dc_value)
            prev_dc_value = diff + prev_dc_value

        # Restore each Minimum Coded Unit and transform into Space domain matrix.
        for idx, ((w1,w2),(h1,h2),im) in enumerate(imArray.slice(width=N, height=N)):
            # Decode Huffman Coded AC components.
            compressed_ac_components, code2value = encoded_ac_units[idx]

            # Decode Zero Length Coded AC components.
            ac_components = ZeroLengthEncoder.decode(
                [map(int, code2value[s][1:-1].split(", ")) for s in compressed_ac_components]
            )

            # Re-construct Minimum Coded Unit from sequence of AC/DC comopnents.
            # by reading in zigzag sequence.
            zigzag_sequence = [dc_components[idx]] + ac_components
            minimum_coded_unit = [0]*64

            for i, value in zip(ZIGZAG_ORDER, zigzag_sequence):
                minimum_coded_unit[i] += value
            minimum_coded_unit = imarray(minimum_coded_unit).reshape(8, 8)

            # By Multiplying Quantization Matrix Minimum Coded Matrix transform into Frequency Cofficients.
            f_domain = minimum_coded_unit * QUANTIZATION_MATRIX

            # Transform frequency domain into Space domain.
            s_domain = dct.toSpace(f_domain)

            try:
                imArray[w1:w2, h1:h2] += s_domain
            except:
                pass

        return imArray


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
