#Author: Alex Peplinski
"""
EFFECTS: calculates entropy of the setup.py file or any file
this code is Adapted from FB36 a contributor on https://code.activestate.com/recipes/577476-shannon-entropy-calculation/#c3
 file_entropy.py
 Shannon Entropy of a file
 = minimum average number of bits per character
 required for encoding (compressing) the file
 So the theoretical limit (in bytes) for data compression:
 Shannon Entropy of the file * file size (in bytes) / 8
 (Assuming the file is a string of byte-size (UTF-8?) characters
 because if not then the Shannon Entropy value would be different.)
 FB - 201011291
"""
#This code is adapted from author FB36 a contributor on https://code.activestate.com/recipes/577476-shannon-entropy-calculation/#c3
import sys
import math
from os.path import abspath, dirname, join
#from __future__ import division
#from collections import Counter
#import math


def entropy_calculator(entropy_file):
    """
    Purpose: read the whole file into a byte array
    """
    f = open(entropy_file, "rb")
    byteArr = f.read()
    f.close()
    fileSize = len(list(byteArr))

    # calculate the frequency of each byte value in the file
    freqList = []
    for b in range(256):
        ctr = 0
        for byte in byteArr:
            if byte == b:
                ctr += 1
        freqList.append(float(ctr) / fileSize)
    # Shannon entropy
    ent = 0.0
    for freq in freqList:
        if freq > 0:
            ent = ent + freq * math.log(freq, 2)
    ent = -ent
    return ent


def entropy_test():
    """
    Purpose: Tests entropy calculation
    """
    entropy_file = abspath(
        join(dirname(__file__), './test_entropy.py'))
    extracted_data = entropy_calculator(entropy_file)


if __name__ == '__main__':
    entropy_test()
