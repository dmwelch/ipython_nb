# -*- coding: utf-8 -*-
import os
from os.path import join as osjoin
import sys

import SimpleITK as sitk

from generatePriors import *

# Constant values
debug = True
experimentDir = os.path.join('/paulsen', 'Experiments', '20130426-generateNewPriors')
testDir = '/paulsen/Experiments/20130202_PREDICTHD_Results/SubjectToAtlasWarped'

def main(subject):
    if not os.path.exists(osjoin(testDir, subject, 't2_average_BRAINSABC_trans.nii.gz')):
        print "Subject has no T2 image"
        return 0
    inputDict = createImageMap(air=osjoin(testDir, subject, 'POSTERIOR_AIR_trans.nii.gz'),
                               notcsf=osjoin(testDir, subject, 'POSTERIOR_NOTCSF_trans.nii.gz'),
                               caudate=osjoin(testDir, subject, 'POSTERIOR_CAUDATE_trans.nii.gz'),
                               wm=osjoin(testDir, subject, 'POSTERIOR_WM_trans.nii.gz'),
                               hippo=osjoin(testDir, subject, 'POSTERIOR_HIPPOCAMPUS_trans.nii.gz'),
                               notgm=osjoin(testDir, subject, 'POSTERIOR_NOTGM_trans.nii.gz'),
                               crblgm=osjoin(testDir, subject, 'POSTERIOR_CRBLGM_trans.nii.gz'),
                               notvb=osjoin(testDir, subject, 'POSTERIOR_NOTVB_trans.nii.gz'),
                               putamen=osjoin(testDir, subject, 'POSTERIOR_PUTAMEN_trans.nii.gz'),
                               thalamus=osjoin(testDir, subject, 'POSTERIOR_THALAMUS_trans.nii.gz'),
                               csf=osjoin(testDir, subject, 'POSTERIOR_CSF_trans.nii.gz'),
                               surfgm=osjoin(testDir, subject, 'POSTERIOR_SURFGM_trans.nii.gz'),
                               globus=osjoin(testDir, subject, 'POSTERIOR_GLOBUS_trans.nii.gz'),
                               accumben=osjoin(testDir, subject, 'POSTERIOR_ACCUMBEN_trans.nii.gz'),
                               notwm=osjoin(testDir, subject, 'POSTERIOR_NOTWM_trans.nii.gz'),
                               crblwm=osjoin(testDir, subject, 'POSTERIOR_CRBLWM_trans.nii.gz'),
                               vb=osjoin(testDir, subject, 'POSTERIOR_VB_trans.nii.gz'),
                               l_accumben=osjoin(testDir, subject, 'cleaned_l_accumben_seg_trans.nii.gz'),
                               r_accumben=osjoin(testDir, subject, 'cleaned_r_accumben_seg_trans.nii.gz'),
                               l_caudate=osjoin(testDir, subject, 'cleaned_l_caudate_seg_trans.nii.gz'),
                               r_caudate=osjoin(testDir, subject, 'cleaned_r_caudate_seg_trans.nii.gz'),
                               l_globus=osjoin(testDir, subject, 'cleaned_l_globus_seg_trans.nii.gz'),
                               r_globus=osjoin(testDir, subject, 'cleaned_r_globus_seg_trans.nii.gz'),
                               l_hippo=osjoin(testDir, subject, 'cleaned_l_hippocampus_seg_trans.nii.gz'),
                               r_hippo=osjoin(testDir, subject, 'cleaned_r_hippocampus_seg_trans.nii.gz'),
                               l_putamen=osjoin(testDir, subject, 'cleaned_l_putamen_seg_trans.nii.gz'),
                               r_putamen=osjoin(testDir, subject, 'cleaned_r_putamen_seg_trans.nii.gz'),
                               l_thalamus=osjoin(testDir, subject, 'cleaned_l_thalamus_seg_trans.nii.gz'),
                               r_thalamus=osjoin(testDir, subject, 'cleaned_r_thalamus_seg_trans.nii.gz'))
    if debug:
        checkStats(inputDict)

    testing = False
    if testing:
        down = {}
        for key, img in inputDict.items():
            down[key] = sitk.Resample(img*255, transform=sitk.Transform(3, sitk.sitkIdentity),
                                      interpolator=sitk.sitkLinear,
                                      size=[64] * 3,
                                      outputOrigin=img.GetOrigin(),
                                      outputDirection=img.GetDirection(),
                                      outputSpacing=[x * 4 for x in img.GetSpacing()])
    airsum = sumPosteriors(inputDict)
    out1 = {}
    out1['air'] = correctAir(inputDict['air'], airsum, False)
    _, out1 = copyDict(inputDict, out1)
    if debug:
        checkStats(out1, checks=["min"])
    inputDict = None

    bgKeys = ['l_accumben', 'r_accumben', 'l_caudate', 'r_caudate', 'l_putamen', 'r_putamen']
    out2 = {}
    out2['mask_basal'] = sumOverKeys(out1, bgKeys) > 0
    out2['mask_globus'] = sumOverKeys(out1, ['l_globus', 'r_globus']) > 0
    out2['mask_hippo'] = sumOverKeys(out1, ['l_hippo', 'r_hippo']) > 0
    out2['mask_thalamus'] = sumOverKeys(out1, ['l_thalamus', 'r_thalamus']) > 0
    for key in out1.keys():
        if key in out2.keys() + ['l_globus', 'r_globus', 'l_hippo', 'r_hippo', 'l_thalamus', 'r_thalamus'] + bgKeys:
            continue
        else:
            out2[key] = out1[key]
    if debug:
        checkStats(out2, checks=['min'])
    assert set(out2.keys()) == set(['hippo', 'vb', 'crblgm', 'caudate',
                                    'mask_thalamus', 'globus', 'air', 'surfgm',
                                    'csf', 'notvb', 'mask_hippo', 'thalamus',
                                    'mask_basal', 'crblwm', 'wm', 'notgm',
                                    'mask_globus', 'notcsf', 'accumben',
                                    'notwm', 'putamen']), out2.keys()
    out1 = None

    gmImageKeys = ['surfgm', 'crblgm', 'notgm',   # posterior gm
                 'accumben', 'caudate', 'globus', 'hippo', 'putamen', 'thalamus']  # posterior

    maskKeys = ['mask_basal', 'mask_globus', 'mask_hippo', 'mask_thalamus']
    out2['surfgm'] = createResidualImage(out2, gmImageKeys, maskKeys)
    if debug:
        checkStats(out2, checks=['min'])

    imageKeys = ['vb', 'notvb',  # posterior vb
                 'csf', 'notcsf',  # posterior csf
                 'surfgm', 'crblgm', 'notgm',   # posterior gm
                 'wm', 'crblwm', 'notwm',  # posterior wm
                 'accumben', 'caudate', 'globus', 'hippo', 'putamen', 'thalamus',  # posterior
                 'air']  # corrected air
    mask = createMask(out2, maskKeys, True)
    out3 = {}
    out3 = maskImages(out2, mask, maskKeys)
    # Remove the unnecessary POSTERIOR images
    for key in ['accumben', 'caudate', 'globus', 'hippo', 'putamen', 'thalamus']:
        out3.pop(key)
    assert set(out3.keys()) == set(['vb', 'crblgm', 'mask_thalamus',
     'air',
     'surfgm',
     'csf',
     'notvb',
     'mask_hippo',
     'mask_basal',
     'crblwm',
     'wm',
     'notgm',
     'mask_globus',
     'notcsf',
     'notwm']), set(out3.keys())
    if debug:
        checkStats(out3, checks=['min'])
    out2 = None
    maskDict = createImageMap(brainstem=osjoin(experimentDir, 'newAtlas', 'brainstem.nii.gz'),
                              cerebrum=osjoin(experimentDir, 'newAtlas', 'cerebrum.nii.gz'),
                              cerebellum=osjoin(experimentDir, 'newAtlas', 'cerebellum.nii.gz'))
    # resample masks to prior space
    mask1 = {}
    for key, value in maskDict.items():
        mask1[key] = sitk.Resample(maskDict[key],
                                   interpolator=sitk.sitkNearestNeighbor,
                                   size=maskDict[key].GetSize(),
                                   outputOrigin=out3['air'].GetOrigin(),
                                   outputDirection=out3['air'].GetDirection())
    assert mask1.keys() == maskDict.keys()
    # Create hard and soft masks
    # combine the cerebrum and brainstem mask
    mask1['cerebrum'] = (mask1['cerebrum'] + mask1['brainstem']) > 0
    mask1.pop('brainstem')
    if debug:
        checkStats(mask1)
    maskDict = None
    mask2 = {}
    for key in mask1.keys():
        # Create hard mask
        mask2[key] = sitk.BinaryMorphologicalClosing(mask1[key], 3) # close hard masks
        mask2["soft_" + key] = SoftMask(mask2[key], 4.0) # create soft masks
    # Create a third label for watersheds from T1 image
    t1 = sitk.ReadImage(osjoin(experimentDir, 'newAtlas', 'template_t1.nii.gz'))
    t1 = sitk.Resample(t1, interpolator=sitk.sitkLinear,
                       size=t1.GetSize(),
                       outputOrigin=out3['air'].GetOrigin(),
                       outputDirection=out3['air'].GetDirection())
    distFile = osjoin(experimentDir, 'Results', 'distanceMap.nii.gz')
    skullFile = osjoin(experimentDir, 'Results', 'masks_skull.nii.gz')
    if os.path.exists(distFile) and os.path.exists(skullFile):
        dist_img = sitk.ReadImage(distFile)
        mask2['skull'] = sitk.ReadImage(skullFile)
        labels =  mask2['cerebellum'] + (mask2['cerebrum']*2) + mask2['skull']*3
    else:
        combined = (mask2['cerebellum'] + mask2['cerebrum']) > 0
        safety_margin = 3
        mask2['skull'] = (t1>50) * (1 - sitk.BinaryDilate(combined, safety_margin))
        labels =  mask2['cerebellum'] + (mask2['cerebrum']*2) + mask2['skull']*3
        # Move over the cerebellum and cerebrum values for gm
        dist_img = sitk.SignedMaurerDistanceMap(labels!=0, insideIsPositive=False, squaredDistance=False, useImageSpacing=False)
        sitk.WriteImage(dist_img, distFile)
        dumpImageMap(mask2, osjoin(experimentDir, 'Results'), prefix="masks", sep="_")
    if debug:
        checkStats(mask2)
    mask1 = None
    gm_combined = (out3['surfgm'] + out3['crblgm'])
    wsd_img = sitk.MorphologicalWatershedFromMarkers(gm_combined * dist_img, labels, markWatershedLine=False)
    mask3 = {} # Subject-specific masks included
    mask3['soft_cerebellum'] = SoftMask(wsd_img==1, 2.0) # smaller smoothing due to label proximity
    mask3['soft_cerebrum'] = SoftMask(wsd_img==2, 2.0)
    _, mask3 = copyDict(mask2, mask3)
    if debug:
        checkStats(mask3)
    mask2 = None

    out4 = {}
    out4['surfgm'] = gm_combined * mask3['soft_cerebrum']
    out4['crblgm'] = gm_combined * mask3['soft_cerebellum']

    wm_combined = out3['wm'] + out3['crblwm']
    out4['wm'] = wm_combined * mask3['soft_cerebrum']
    out4['crblwm'] = wm_combined * mask3['soft_cerebellum']
    _, out4 = copyDict(out3, out4)
    if debug:
        checkStats(out4, checks=["min"])
    out3 = None

    level=10
    cerebellum_combined = out4['crblgm'] + out4['crblwm']
    crblgm, crblwm = gammaScale(out4['crblgm'], out4['crblwm'], level)

    out5 = {}
    out5['crblgm'] = sitk.Mask(crblgm, wsd_img==1)
    out5['crblwm'] = sitk.Mask(crblwm, wsd_img==1)
    _, out5 = copyDict(out4, out5)
    if debug:
        checkStats(out5, checks=["min"])
    out4 = None

    skull_array = sitk.GetArrayFromImage(mask3['skull'])
    skull_array[:,138:,:] = 1.0
    skull_array[94:,:,:] = 1.0
    sinus = sitk.GetImageFromArray(skull_array)
    sinus.CopyInformation(mask3['skull'])
    closed_air = sitk.ConnectedComponent(sitk.BinaryMorphologicalOpening(out5['air'] > 0.01, 5))  # Opening b/c air is an 'INVERSE' mask
    head = sitk.RelabelComponent(closed_air, True)

    valid_air = sitk.Cast(head, sitk.sitkUInt8) * sitk.Cast(1 - sinus, sitk.sitkUInt8)
    va = sitk.GetArrayFromImage(valid_air)
    keep_labels = numpy.unique(va)
    assert len(keep_labels) >= 3, "Sinuses were not located"
    labels = (head == keep_labels[0])
    for ii in + keep_labels[1:]:
        labels += (head == ii)
    labels = labels>0

    out6 = {}
    out6['air'] = sitk.Mask(out5['air'], labels)
    out6['csf'] = sitk.Mask(out5['air'], labels==0) + out5['csf']
    _, out6 = copyDict(out5, out6)
    if debug:
        checkStats(out6, checks=['min'])
    out5 = None

    out7 = normalizeImages(out6, verify=True)
    if debug:
        checkStats(out7)
    out6 = None
    resultDir = os.path.join(experimentDir, 'Results', subject)
    if not os.path.exists(resultDir):
        os.mkdir(resultDir)
    dumpImageMap(out7, resultDir, prefix='final', sep="_")

if __name__ == '__main__':
    with open(argv[1], 'r') as csvFile:
        lines = csvFile.readlines()
    for line in lines:
        output = line.split(',')
        subject = output[0]
        print "Processing subject {0}".format(subject)
        main(subject=subject)
