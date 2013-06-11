#!/usr/bin/env python
"""
# # Description #
#
# BRAINSTools does not currently create robust segmentations of brain labels, and sometimes the brain labels are __severely__ incorrect.  In the test cases, the labels are outside the brain mask (in the neck) and that affects our intercranial volume (ICV) measurements.
#
# * * *
#
# ## Purpose ##
#
# The purpose of this script is to remove these abborrent segmentations and calculate the resulting ICV volume.
#
# ## Methods ##
#
# 1.  Create a simple dilated mask of the [NAC atlas](http://nac.spl.harvard.edu/publications/item/view/1265)[1].
# 2.  Remove the dilated mask inclusion of the eyes
# 2.  BRAINSTools calculates the transforms between sessions to the atlas. We will apply the transform from atlas --> session on the mask
# 3.  Using the mask, we will remove the labeled volumes outside the mask
# 4.  Remove surviving 'islands' near valid labels by a binary mask of the result label image and masking by the largest region
#
# __This order is necessary to remove labels that might have been connected to the largest region mask initially, but are incorrect.__
#
# [1] Nota Bene: BRAINSTools atlas is slightly different than the original.  It can be found on the MIDAS site or in the `.../build/BRAINSTools/ReferenceAtlas-build/Atlas/` directory.
"""
import os

from nipype.interfaces import ants
import numpy as np
import SimpleITK as sitk

atlas = '/ipldev/scratch/welchdm/bld/BTools-20130312/ReferenceAtlas-build/Atlas/Atlas_20130106/template_nac_labels.nii.gz'
nacFile = '/ipldev/scratch/welchdm/bld/BTools-20130312/ReferenceAtlas-build/Atlas/Atlas_20130106/hncma-atlas.nii.gz'
avg_t1 = '/ipldev/scratch/welchdm/bld/BTools-20130312/ReferenceAtlas-build/Atlas/Atlas_20130106/template_t1.nii.gz'

os.environ["PATH"] += ':/ipldev/scratch/welchdm/bld/BTools-20130312/bin'

def calculateICVFromMask(image):
    """
    Calculate the intercranial volume measurement from the brain mask
    """
    nda = sitk.GetArrayFromImage(image)
    maskSum = nda.sum()
    size = image.GetSpacing()
    return maskSum * size[0] * size[1] * size[2]

def main(args):
    baseDir = args.baseDir
    outfile = args.outfile
    # Make the atlas mask
    atlasFile = '/tmp/atlasMask.nii.gz'
    if not os.path.exists(atlasFile):
         labels = sitk.ReadImage(atlas)
         mask = sitk.BinaryThreshold(labels, 1.0)
         dilate = sitk.DilateObjectMorphology(mask, 10)
         nac = sitk.ReadImage(nacFile)
         eyes_mask = sitk.BinaryThreshold(nac, 4027, 4028) # right eye = 4028, left eye = 4027
         dilated_eyes = sitk.DilateObjectMorphology(eyes_mask, 6)
         full_mask = dilate * (1 - dilated_eyes)
         sitk.WriteImage(full_mask, atlasFile)
         print "Temporary atlas mask written to %s" % atlasFile
    transformDir = 'SubjectToAtlasWarped'
    transformFile = 'AtlasToSubject_Composite.h5'
    for base, dirs, _ in os.walk(baseDir):
        if 'TissueClassify' in dirs:
            pathElements = list(base.split(os.path.sep))
            session = pathElements.pop()
            subject = pathElements.pop()
            site = pathElements.pop()
            experiment = pathElements.pop()
            original = os.path.join(baseDir, 'TissueClassify', 'fixed_brainlabels_seg.nii.gz')
            print pathElements, type(pathElements)
            home = os.path.sep.join(pathElements)
            transform = os.path.sep.join([home, experiment, transformDir, session, transformFile])
            registered = ants.ApplyTransforms()
            registered.inputs.reference_image = original
            registered.inputs.transformation_files = [transform]
            registered.inputs.interpolation = 'NearestNeighbor'
            registered.inputs.input_image = atlasFile
            registered.inputs.output_image = os.path.join(baseDir, 'TissueClassify', 'registered_atlas_mask.nii.gz')
            registered.run()
            uncorrected = sitk.ReadImage(os.path.join(baseDir, 'TissueClassify', 'fixed_brainlabels_seg.nii.gz'))
            atlas_mask = sitk.Cast(sitk.ReadImage(registered.inputs.output_image), uncorrected.GetPixelIDValue())
            # Remove the islands but keep the venous blood
            opened = sitk.DilateObjectMorphology(sitk.ErodeObjectMorphology(sitk.BinaryThreshold(uncorrected * atlas_mask, 1.0), 1), 3)
            new_labels = opened * uncorrected
            connected = sitk.ConnectedComponent(new_labels, True)
            relabeled = sitk.RelabelComponent(connected)
            final_mask = sitk.BinaryThreshold(relabeled, 1, 1)
            sitk.WriteImage(uncorrected * final_mask, os.path.join(baseDir, 'TissueClassify', 'masked_fixed_brainlabels_seg.nii.gz'))
            volume=calculateICVFromMask(final_mask)
            try:
                fid = open(outfile, 'a')
                fid.write("{experiment},{site},{subject},{session},ICV,{volume}\n".format(experiment=experiment, site=site, subject=subject, session=session, volume=volume))
                fid.flush()

            finally:
                fid.close()

if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='\
    BRAINSABC segmentation clean up script 2013-04-05\
    \
    This writes several files to the TissueClassify/ directory:\
     + registered_atlas_mask.nii.gz\
     + masked_fixed_brainlabels_seg.nii.gz\
    \
    *** Therefore, you need to verify that you have write permissions to the ***\
    ***      /TissueClassify directories before running this script          ***')
    parser.add_argument('-d', '--directory', action='store', dest='baseDir', type=str, required=True,
                        help='The base directory to search for TissueClassify/ directories')
    parser.add_argument('-f','--file', action='store', dest='outfile', type=str, required=True,
                        help='The filename for the output csv.  If it exists already, it will be appended.')
    args = parser.parse_args()
    sys.exit(main(args))
