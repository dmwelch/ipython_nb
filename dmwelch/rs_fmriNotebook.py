# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# <h1>rs_fMRI pilot project</h1> 
# <h3>Development notes</h3>
# <h3>Date: December, 2012</h3>

# <markdowncell>

# <h4>Environment setup for pipeline:</h4>
# This would be better accomplished in a <b>virtualenv</b>
# <li>Portable
# <li>Avoids needed teardown at the script end
# <li>Flexible
# <li>Avoids confusion when nipype_display_crash is called in 'clean' parent enviroment 
#     <i><b>(spent a whole day trying to debug what I thought was a pipeline error that was actually due to nipype_display_crash ImportError)</b></i>

# <codecell>

import argparse
import os
import sys

### HACK: Set PYTHONPATH, DYLD_LIBRARY_PATH, FREESURFER_HOME, and SUBJECTS_DIR for Athena ###
### export PATH=$PATH:/opt/afni-OSX_10.7:/opt/freesurfer_v4.5.0-full/bin ###
os.environ['FREESURFER_HOME'] = '/opt/freesurfer_v4.5.0-full'
os.environ['SUBJECTS_DIR'] = '/paulsen/MRx'
try:
    old_dyld = os.environ['DYLD_LIBRARY_PATH']
except KeyError:
    old_dyld = ''
old_path = os.environ['PATH']
try:
    old_fallback = os.environ['DYLD_FALLBACK_LIBRARY_PATH']
except KeyError:
    old_fallback = ''

os.environ['PATH'] = '/Volumes/scratch/welchdm/bld/latest_BSA/bin:' + \
    '/opt/afni-OSX_10.7:' + '/opt/freesurfer_v4.5.0-full/bin:' + old_path

os.environ['DYLD_LIBRARY_PATH'] = '/Volumes/scratch/welchdm/bld/latest_BSA/lib:' + \
    '/Volumes/scratch/welchdm/bld/latest_BSA/bin:' + \
    '/opt/freesurfer_v4.5.0-full/lib:' + old_dyld

os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = '/opt/afni-OSX_10.7:' + old_fallback

sys.path.insert(1, '/Volumes/scratch/welchdm/src/nipype/nipype')
sys.path.insert(2, '/Volumes/scratch/welchdm/bld/latest_BSA/SimpleITK-build/lib')
sys.path.insert(3, '/Volumes/scratch/welchdm/src/BRAINSStandAlone/AutoWorkup')
# print sys.path

# <markdowncell>

# Function <b><i>select_volume()</i></b> pulls out one 3D timepoint from a 4D (3D + time) DWI array

# <codecell>

def select_volume(filename, index):
    """Return the 3D volume with timestep index from a 4D (3D + time) file
    """
    from nibabel import nifti1 as nifti
    import numpy as np
    assert isinstance(index, int)
    image = nifti.load(filename)
    fourD = image.get_data()
    print len(fourD[...,:])
    header = image.get_header()
    affine = header.get_best_affine()
    threeD = fourD[...,index]
    newVolume = nifti.Nifti1Image(data=threeD, affine=affine, header=header) 
    newVolume.update_header()
    return newVolume, header

# <codecell>

fMRI_file = '/Volumes/scratch/welchdm/src/rs-fMRI-pilot/workflow_20121203_0948/afni3Ddetrend/errts_Decon+orig_dt.nii'
threeD0, header = select_volume(fMRI_file, 0)
# print threeD0.get_header()

# <codecell>

print """Get the valid label list from the freesurfer label volume """
label_file = '/Volumes/scratch/welchdm/src/rs-fMRI-pilot/workflow_20121203_0948/antsApplyTransformsFS1/aparc+aseg_trans.nii.gz'
import SimpleITK as sitk
temp = sitk.ReadImage(label_file)
print temp.GetPixelIDTypeAsString()
labelStat_1 = sitk.LabelStatisticsImageFilter()
labelStat_1.Execute(sitk.Cast(temp, sitk.sitkUInt32), sitk.Cast(temp, sitk.sitkUInt32))
labelList = labelStat_1.GetValidLabels()
print labelList
count = 0;
for item in labelList[1:]:
    if item == 47:
        print count + 1
    else: count += 1

# <markdowncell>

# <h3><color rgb(255,0,0)>The code below does not work: cannot verify the image cosines!</color></h3>
# Instead, used nipy.nifti file reader!!!

# <codecell>

""" Roll threeD0 array so that it matches dimensions with label image """
### label = sitk.Cast(temp, sitk.sitkInt64)
### array = sitk.GetArrayFromImage(label)
### print array.shape

# Rotate (roll) volume until it matches label
# print threeD0.shape
# newArray = np.rollaxis(threeD0, 2, 0)
### Why doesn't this work: >>> newArray = np.rollaxis(newArray, 1, 2)
# newArray = np.rollaxis(newArray, 2, 1) # TODO: verify that image cosines are still correct!
# print newArray.shape
# print threeD0.shape

# labelStat.Execute(array, sitk.Cast(image, sitk.sitkUInt32))
# Copy label image data to newArray
threeD0.set_filename('threeD0.nii')
threeD0.to_files()
newVol = sitk.ReadImage(threeD0.get_filename())
newVol.GetPixelIDTypeAsString()
# print header.keys()
# pixdim = header.get('pixdim')
# print pixdim
# newVol.SetSpacing(header.get('pixdim')[1:3])
# newVol.CopyInformation(label) # Cannot use newVol image cosines!  How can we get the information from the fMRI image???
# sitk.Show(label, 'Orig label')
# sitk.Show(newVol, 'Modified fMRI')
# fmri = sitk.ReadImage(fMRI_file)
# labelStat = sitk.LabelStatistics(fmri, temp) # label image comes SECOND & ITK can't read 4D images!
# statMap1 = labelStat.GetLabelStatisticsMap()
labelStat2 = sitk.LabelStatisticsImageFilter()
labelStat2.Execute(newVol, sitk.Cast(temp, sitk.sitkUInt32))
labelStat2.GetLabelStatisticsMap()
print labelStat2.GetValidLabels()[4]

# <codecell>

import numpy as np
rows = 10
columns = len(labelList)
data = np.array(np.empty((rows, columns)), ndmin=2)
index = 0
for row in range(rows):
    numpy.put( data, index, np.array(labelList, ndmin=2))
    index += columns
frow, fcolumn =  data.shape
# print '%d, %d' %(frow, fcolumn)
# print data

# for ii in range(columns):
#     print data[:,ii].shape
covar = np.cov(data)
print covar.shape

# <markdowncell>

# <h3>Binary Thresholding testing</h3>

# <codecell>

import SimpleITK as sitk
import copy
# img1 = sitk.ReadImage(label_file)
input_file = '/Volumes/scratch/welchdm/src/rs-fMRI-pilot/rs_fmri_workflow/antsApplyTransformWHM/mapflow/_antsApplyTransformWHM0/POSTERIOR_WM_TOTAL_trans.nii'
image = sitk.ReadImage(input_file)
# sitk.Show(image, 'Posteriors')
# print image.GetPixelIDTypeAsString()
binaryMask = sitk.BinaryThreshold(image, 0.5, 1.0)
sitk.Show(binaryMask*255, 'binary')
# fileName = 'whiteMatterMask.nii'
radiusMM = 1
erodedMask = sitk.BinaryErode(binaryMask, radiusMM)
sitk.Show(erodedMask*255, 'eroded')
connected = sitk.ConnectedComponent(erodedMask)
sitk.Show(connected*15, 'connected')
sortedComp = sitk.RelabelComponent(connected, 10)
sitk.Show(sortedComp*15, 'sorted_10')
maskOnly = sitk.BinaryThreshold(sortedComp, 1, 1)
sitk.Show(maskOnly*255, 'maskOnly')
# fullName = os.path.join(os.getcwd(), fileName)
# sitk.WriteImage(maskOnly, os.path.join(os.getcwd(), 'Only' + fileName))
sitk.Show(img1, 'label_file')

# <markdowncell>

# <h3>Correlation .mat file</h3>

# <codecell>

### Test writeMat function
import os
import numpy as np
from scipy.io import savemat
in_file = '/Volumes/scratch/welchdm/src/rs-fMRI-pilot/workflow_20121206_1330/_label_file_..Volumes..scratch..welchdm..src..rs-fMRI-pilot..workflow_20121205_1330..antsApplyTransformsFS1..aparc+aseg_trans.nii.gz/afni3DroiStats/errts_Decon+orig_dtroiStat.1D'
out_file = 'my_out_file.mat'
with open(in_file, 'r') as fID:
    count = 0
    timepoint = []
    row_data = []
    for valueStr in fID.readlines():
        value_list = valueStr.split()
        if count == 0:
            column_header = value_list[2:]
            valid_labels = [item.strip('NZMed_') for item in column_header]
            columns = len(column_header)
            # print column_header
        else:
            timepoint.append(value_list[1].split('[')[0])
            row_data.append(value_list[2:])
        count += 1
    rows = len(timepoint)
    data = np.array(row_data, dtype='float', ndmin=2)
    labels = np.array(valid_labels, dtype='int', ndmin=1)
corr = np.corrcoef(data)
temp = out_file
if temp[-4:] == '.mat':
    temp = temp[:-4]
fileName = os.path.abspath(temp)
savemat(file_name=temp + '_corr', mdict={'data':corr}, appendmat=True, oned_as='row')
savemat(file_name=temp + '_labels', mdict={'data':labels}, appendmat=True, oned_as='row')
savemat(file_name=temp + '_raw', mdict={'data':data}, appendmat=True, oned_as='row')
# return out_file
# s = timepoint[0]
# print timepoint
# print valid_labels
print data.shape, corr.shape, labels.shape

