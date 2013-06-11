# -*- coding: utf-8 -*-
import csv
import os
import sys

sys.path.insert(0, '/ipldev/sharedopt/ipython_notebooks/common/')

import SimpleITK as sitk

import pinc

def main(fname, notfname):
    tissueImage = sitk.ReadImage(fname)
    notImage = sitk.ReadImage(notfname)
    # Blur the probabilities by 0.5 mm
    width = 0.5
    blurredTissue = sitk.DiscreteGaussian(tissueImage, width)
    blurredNot = sitk.DiscreteGaussian(notImage, width)
    # Get the brain mask
    brainMask = sitk.ReadImage('/ipldev/scratch/welchdm/bld/BTools-20130312/ReferenceAtlas-build/Atlas/Atlas_20130106/')

if __name__ == '__main__':
    import sys

