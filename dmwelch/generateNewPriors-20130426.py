#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import os
import sys

sys.path.insert(0, '/Shared/sinapse/sharedopt/ipython_notebooks/common/')

import SimpleITK as sitk

import pinc

def main(region, side=None, prefix='total'):
    POSTERIOR_DIR = '/paulsen/Experiments/20130202_PREDICTHD_Results/SubjectToAtlasWarped/'
    atlas = sitk.ReadImage('/paulsen/Experiments/20130426-generateNewPriors/ReferenceAtlas/template_t1.nii.gz')
    zero = atlas * 0
    sumImg = sitk.Cast(zero, sitk.sitkFloat32)
    # sessionList = ['10021', '10026', '10058', '10130', '10159', '10201', '10221', '10371', '10483', '10498']
    count = 0
    with open('/paulsen/Experiments/20130426-generateNewPriors/validSessionsWithWeighting.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            session = row['session']
            weight = row['Weighting']
            if side is None:
                filename = '_'.join([region, 'trans'])
            else:
                filename = '_'.join(['cleaned', side, region, 'seg', 'trans'])
            filepath = os.path.join(POSTERIOR_DIR, session, filename + '.nii.gz')
            if os.path.exists(filepath):
                test = sitk.ReadImage(filepath)
                # test = normalizeImage(test)
                # sitk.WriteImage(test, prefix + '_%s.nii.gz' % session)
                sumImg += (test * weight)
                del test
                # sitk.WriteImage(sumImg, prefix + '_%d.nii.gz' % count)
                count +=1
            else:
                fid = open('%s_%s.err' % (session, filename), 'a')
                fid.write("Cannot find a valid file at %s" % filepath)
                fid.close()
            # if count > 5:
            #     break
    if count > 0:
        stats = sitk.Statistics(sumImg)
        _max = stats.GetBasicMeasurementMap()['Maximum']
        _min = stats.GetBasicMeasurementMap()['Minimum']
        print "prefix: "
        print "MIN =", _min
        print "MAX =", _max
        print "------------"
        sitk.WriteImage(sumImg, 'summed_%d_' % (count) + prefix + '.nii.gz')

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print sys.argv
    elif len(sys.argv) == 4:
        region = sys.argv[2]
        side = sys.argv[3]
        prefix = sys.argv[1]
        assert region in ['accumben', 'caudate', 'globus', 'hippocampus', 'thalamus', 'putamen']
        assert side in ['l', 'r']
        main(region=region, side=side, prefix=prefix)
    elif len(sys.argv) == 3:
        region = sys.argv[2]
        prefix = sys.argv[1]
        main(region=region, prefix=prefix)
    else:
        print "ERROR: not the right number of inputs"
