# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import os
import sys

import SimpleITK as sitk

valueDict = {
    "l_caudate": 1,
    "r_caudate": 2,
    "l_putamen": 3,
    "r_putamen": 4,
    "l_hippocampus": 5,
    "r_hippocampus": 6,
    "l_thalamus": 7,
    "r_thalamus": 8,
    "l_accumbens": 9,
    "r_accumbens": 10,
    "l_globus": 11,
    "r_globus": 12
}

orderOfPriority = ["l_caudate",
                   "r_caudate",
                   "l_putamen",
                   "r_putamen",
                   "l_hippocampus",
                   "r_hippocampus",
                   "l_thalamus",
                   "r_thalamus",
                   "l_accumbens",
                   "r_accumbens",
                   "l_globus",
                   "r_globus"]

def getVolumes(outfile, labelImageDir):
    parts = labelImageDir.split(os.path.sep)
    _dummy = parts.pop()
    session = parts.pop()
    subject = parts.pop()
    site = parts.pop()
    experiment = parts.pop()
    labelImageName = os.path.join(labelImageDir, "allLabels_seg.nii.gz")
    labelImage = sitk.ReadImage(labelImageName)
    lstat = sitk.LabelStatisticsImageFilter()
    lstat.Execute(labelImage, labelImage)

    ImageSpacing = labelImage.GetSpacing()
    for name in orderOfPriority:
        value = valueDict[name]
        if lstat.HasLabel(value):
            myMeasurementMap = lstat.GetMeasurementMap(value)
            dictKeys = myMeasurementMap.GetVectorOfMeasurementNames()
            dictValues = myMeasurementMap.GetVectorOfMeasurementValues()
            measurementDict = dict(zip(dictKeys, dictValues))
            volume = ImageSpacing[0] * ImageSpacing[1] * ImageSpacing[2] * measurementDict['Count']
            try:
                fid = open(outfile, 'a')
                fid.write("{experiment},{site},{subject},{session},{name},{volume}\n".format(experiment=experiment, site=site, subject=subject,
                                                                                             session=session, name=name, volume=volume))
                fid.flush()
            finally:
                fid.close()

def getICV(outfile, sessionDir):
    parts = sessionDir.split(os.path.sep)
    _dummy = parts.pop()
    session = parts.pop()
    subject = parts.pop()
    site = parts.pop()
    experiment = parts.pop()
    labelImageName = os.path.join(sessionDir, "fixed_brainlabels_seg.nii.gz")
    labelImage = sitk.ReadImage(labelImageName)
    ImageSpacing = labelImage.GetSpacing()

    lstat = sitk.LabelStatisticsImageFilter()
    lstat.Execute(labelImage, labelImage)

    volume = 0.0
    labels = []
    name = 'ICV'
    for value in lstat.GetValidLabels():
        if value != 0:
            labels.append(value)
            myMeasurementMap = lstat.GetMeasurementMap(value)
            dictKeys = myMeasurementMap.GetVectorOfMeasurementNames()
            dictValues = myMeasurementMap.GetVectorOfMeasurementValues()
            measurementDict = dict(zip(dictKeys, dictValues))
            volume += ImageSpacing[0] * ImageSpacing[1] * ImageSpacing[2] * measurementDict['Count']
    try:
        fid = open(outfile, 'a')
        fid.write("{experiment},{site},{subject},{session},{name},{volume}\n".format(experiment=experiment, site=site, subject=subject,
                                                                                             session=session, name=name, volume=volume))
        fid.flush()
    finally:
        fid.close()

def main(args):
    baseDir = args.baseDir
    outfile = args.outfile
    for base, dirs, _ in os.walk(baseDir):
        if 'CleanedDenoisedRFSegmentations' in dirs and args.volumeFlag in ['regions', 'all']:
            labelImageDir = os.path.join(base, 'CleanedDenoisedRFSegmentations')
            getVolumes(outfile, labelImageDir)
        if 'TissueClassify' in dirs and args.volumeFlag in ['icv', 'all']:
            labelImageDir = os.path.join(base, 'TissueClassify')
            getICV(outfile, labelImageDir)

if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='BRAINSABC segmentation volume calculation script 2013-04-26')
    parser.add_argument('-v', '--volume', action='store', dest='volumeFlag',
                        choices=['icv', 'regions', 'all'], type=str, required=True,
                        help='The volume flag to determine what type of volume')
    parser.add_argument('-d', '--directory', action='store', dest='baseDir', type=str, required=True,
                        help='The base directory to search for TissueClassify/ directories')
    parser.add_argument('-f','--file', action='store', dest='outfile', type=str, required=True,
                        help='The filename for the output csv.  If it exists already, it will be appended.')
    args = parser.parse_args()
    sys.exit(main(args))

