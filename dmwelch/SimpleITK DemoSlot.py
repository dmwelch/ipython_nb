# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import SimpleITK as sitk
import os
import sys
print "Hello Dave"

# <codecell>


# <codecell>

# !ls /ipldev/sharedopt/ipython_notebooks/DATA
files=!ls /ipldev/sharedopt/ipython_notebooks/DATA/083006668/083006668_20120420_30/TissueClassify/BABC/*.nii.gz
t1=!ls /ipldev/sharedopt/ipython_notebooks/DATA/083006668/083006668_20120420_30/TissueClassify/BABC/t1_*.nii.gz
t2=!ls /ipldev/sharedopt/ipython_notebooks/DATA/083006668/083006668_20120420_30/TissueClassify/BABC/t2_*.nii.gz
lb=!ls /ipldev/sharedopt/ipython_notebooks/DATA/083006668/083006668_20120420_30/TissueClassify/BABC/brain_label_seg.nii.gz

# <codecell>

lb

# <codecell>

t1_image=sitk.ReadImage(t1[0])
t2_image=sitk.ReadImage(t2[0])
lb_image=sitk.ReadImage(lb[0])

# <codecell>

def DisplayCenterSlice(image, title=""):
    """ Display the center slice of an sitkImage"""
    size=list(image.GetSize())
    dims=image.GetDimension()
    if dims == 2:
        index=[0,0]
    else:
       index=[0,0,int(size[2]/2)]
       size[2]=0
    twoDImage=sitk.Extract(image,size,index)
    np_image=sitk.GetArrayFromImage(twoDImage)
    figure(1)
    subplot(121)
    myplot=plt.imshow(np_image, cmap=cm.gray, interpolation=None)
    myplot.set_label("T2_image")
    plt.title(title)
    subplot(122)
    myplot=plt.imshow(np_image, cmap=cm.gray, interpolation=None)
    myplot.set_label("xxxT2_image")
    plt.title(title)
    
    plt.show()
    return myplot


def vDisplayCenterSlice(images, titles):
    """ Display the center slice of an sitkImage"""
    num_images=len(images)
    num_title=len(titles)
    if num_images != num_title:
        print "ERROR: images and titles must be the same length."
        return None
    figure(1)
    for img_idx in range(0,num_images):
        subplotnumber=100+(num_images)*10+(1+img_idx)
        size=list(images[img_idx].GetSize())
        dims=images[img_idx].GetDimension()
        if dims == 2:
            index=[0,0]
        else:
           index=[0,0,int(size[2]/2)]
           size[2]=0
        twoDImage=sitk.Extract(images[img_idx],size,index)
        np_image=sitk.GetArrayFromImage(twoDImage)
        subplot(subplotnumber)
        myplot=plt.imshow(np_image, cmap=cm.gray, interpolation=None)
        myplot.set_label(titles[img_idx])
        plt.title(titles[img_idx])
    plt.show()
    return plt

# <codecell>

vDisplayCenterSlice([t1_image,t2_image],["t1","t2"])
sitk.sitkLabelUInt16?

f64=sitk.Cast(t1_image,sitk.sitkFloat64)
im_uint32=sitk.Cast(f64,sitk.sitkInt8)
print sitk.sitkUInt32
print sitk.sitkInt64
print sitk.sitkFloat64
print sitk.sitkUInt64

# <codecell>

binimages_fn=!ls /Users/johnsonhj/Dropbox/DATA/BinaryImages/[bs]*.nhdr
print binimages_fn
im=list()
for image_fn in binimages_fn:
    im.append(sitk.ReadImage(image_fn))
    
for index in range(0,len(im)):
    erd=sitk.DiscreteGaussian(im[index],1)
    #sitk.Show(erd,'gauss45.nii')
    dil=sitk.BinaryThreshold(erd,50)
    mask=sitk.Cast(dil,sitk.sitkFloat32)
    dist=sitk.SignedMaurerDistanceMap(dil)*mask*-1.0
    
    x=sitk.Statistics(dist)
    immax=x.GetVectorOfMeasurementValues()[0] ## The first element is the maximum
    out=sitk.Cast( (dist*(1.0/immax)*50.0+50.0)*mask, sitk.sitkUInt8)
    #out[10,10]=255
    out_dir=os.path.dirname(binimages_fn[index])
    out_fn=os.path.basename(binimages_fn[index])
    out_fn=out_fn.replace('nhdr','nii.gz')
    sitk.WriteImage(out,os.path.join(out_dir,'dist_'+out_fn))
    DisplayCenterSlice(out)
    
    
#sitk.Show(out)

# <codecell>

newbinimages_fn=!ls /Users/johnsonhj/Dropbox/DATA/BinaryImages/dist*.nii.gz
#print newbinimages_fn
test_images=!ls /Users/johnsonhj/Dropbox/DATA/083006668/083006668_20090219_30/TissueClassify/BABC/t1_average_BRAINSABC.nii.gz
myimage=sitk.ReadImage(test_images[0])
DisplayCenterSlice(sitk.DiscreteGaussian(myimage,5),'t1avg')

sitk.CannyEdgeDetection?

# <codecell>

x.GetVectorOfMeasurementValues()[0]
#x.GetVectorOfMeasurementNames()

# <markdowncell>

# My favorite formula is $\int_a^b x dx$

# <codecell>

t1_candidate=sitk.BinaryThreshold(t1_image,200,2200,1,0)
t2_candidate=sitk.BinaryThreshold(t2_image,0,500,1,0)
blood_candidate=t1_candidate*t2_candidate
dist_blood=sitk.SignedMaurerDistanceMap(blood_candidate)
#sitk.Show(t1_image,'t1.nii')
#sitk.Show(t2_image,'t2.nii')
seed_blood=sitk.BinaryThreshold(lb_image,5,5,1,0)
signed_dist_orig=sitk.SignedMaurerDistanceMap(seed_blood)

#simple_test=sitk.ThresholdSegmentationLevelSet(sitk.Cast(seed_blood,sitk.sitkFloat32),sitk.Cast(blood_candidate,sitk.sitkFloat32)-0.5)#,1,1,0.02,1.0,1.0,1000)
#simple_test=sitk.BinaryThreshold(simple_test,0,1000000000)
#DisplayCenterSlice(seed_blood)
#sitk.Show(seed_blood*1000)
seed_blood=seed_blood+1
test=sitk.LaplacianSegmentationLevelSet(dist_blood,sitk.Cast(seed_blood,sitk.sitkFloat32))

# <codecell>

#test=sitk.BinaryThreshold(test,-10000000000,0,1,0)
sitk.Show(sitk.LabelOverlay(t1_image,simple_test,0.15,0))
sitk.Show(simple_test*100, 'st.nii')
print "DONE"
#sitk.ThresholdSegmentationLevelSet?
#sitk.LabelOverlay?
sitk.LaplacianSegmentationLevelSet?

# <markdowncell>

# $ \int_a^b $
# 
# help(sitk.ThresholdSegmentationLevelSetImageFilter)
# ls = sitk.ThresholdSegmentationLevelSet( img1, img2, 76, 147 )
# sitk.Show( ls )
# sitk.Show( sitk.LabelOverlay( img, ls >=0 ) )
# 
# sitk.Show( sitk.LabelContourOverlay( img, ls >=0 ) )
# sitk.Show( sitk.LabelOverlay( img, sitk.LabelContour( ls <0 ) ) )

# <codecell>

import SimpleITK as sitk
#img = sitk.ReadImage( "/Users/johnsonhj/Dashboard/src/SimpleITK/Testing/Data/Input/cthead1.png" )
#img1 = sitk.ReadImage( "/Users/johnsonhj/Dashboard/src/SimpleITK/Testing/Data/Input/cthead1-ls-seed.nrrd" )
#img2 = sitk.ReadImage( "/Users/johnsonhj/Dashboard/src/SimpleITK/Testing/Data/Input/cthead1-Float.mha" )
head = sitk.ReadImage( "/Users/johnsonhj/Dashboard/src/SimpleITK/Testing/Data/Input/cthead1-Float.mha")
tissue=sitk.BinaryThreshold(head,30,140,1,0)
new_dist=sitk.SignedMaurerDistanceMap(tissue)
DisplayCenterSlice(new_dist)
dist = sitk.ReadImage( "/Users/johnsonhj/Dashboard/src/SimpleITK/Testing/Data/Input/2th_cthead1_distance.nrrd")
#out_img=sitk.ThresholdSegmentationLevelSet( img1, img2, 76, 147 )
#erode=sitk.ErodeObjectMorphology(out_img,2)
#edge=sitk.CannyEdgeDetection(sitk.GradientAnisotropicDiffusion(img2))
#DisplayCenterSlice(erode)
#test=sitk.LaplacianSegmentationLevelSet(erode, img2,0.2,3,2,2000)
sitk.Show(new_dist)
test=sitk.LaplacianSegmentationLevelSet(new_dist,head)
test=sitk.BinaryThreshold(test,-10000000000,0,1,0)

# <codecell>

DisplayCenterSlice(head,'head')
DisplayCenterSlice(dist,'dist')

#aa=DisplayCenterSlice(img)
#bb=DisplayCenterSlice(img1)
#cc=DisplayCenterSlice(img2)
out_disp=DisplayCenterSlice(test,'test')
sitk.Show(test,'test.nii.gz')
#sitk.Show( img )
#sitk.Show( img1 )
#sitk.Show( test-erode )

# <codecell>


# <codecell>

tt=sitk.SmoothingRecursiveGaussian(t2_image,1.0)-sitk.SmoothingRecursiveGaussian(t2_image,1.1)
xx=DisplayCenterSlice(tt,title=os.path.basename(t2[0]))
plt.show()

# <codecell>

fig = plt.figure()
fig.subplots_adjust(left=0.2, wspace=0.6)
labelx=-0.3

ax2 = fig.add_subplot(121)
ax2.set_title('ylabels aligned')
ax2.plot(2000*np.random.rand(10))
ax2.set_ylabel('aligned 1')
ax2.yaxis.set_label_coords(labelx, 0.5)
ax2.set_ylim(0, 2000)

ax4 = fig.add_subplot(122)
ax4.plot(np.random.rand(10))
ax4.set_ylabel('aligned 2')
ax4.yaxis.set_label_coords(labelx, 0.5)
ax2.set_ylim(0, 2000)

plt.show()

# <codecell>

%loadpy http://matplotlib.org/mpl_examples/api/collections_demo.py

# <codecell>

#!/usr/bin/env python
'''Demonstration of LineCollection, PolyCollection, and
RegularPolyCollection with autoscaling.

For the first two subplots, we will use spirals.  Their
size will be set in plot units, not data units.  Their positions
will be set in data units by using the "offsets" and "transOffset"
kwargs of the LineCollection and PolyCollection.

The third subplot will make regular polygons, with the same
type of scaling and positioning as in the first two.

The last subplot illustrates the use of "offsets=(xo,yo)",
that is, a single tuple instead of a list of tuples, to generate
successively offset curves, with the offset given in data
units.  This behavior is available only for the LineCollection.

'''

import matplotlib.pyplot as plt
from matplotlib import collections, transforms
from matplotlib.colors import colorConverter
import numpy as np

nverts = 50
npts = 100

# Make some spirals
r = np.array(range(nverts))
theta = np.array(range(nverts)) * (2*np.pi)/(nverts-1)
xx = r * np.sin(theta)
yy = r * np.cos(theta)
spiral = list(zip(xx,yy))

# Make some offsets
rs = np.random.RandomState([12345678])
xo = rs.randn(npts)
yo = rs.randn(npts)
xyo = list(zip(xo, yo))

# Make a list of colors cycling through the rgbcmyk series.
colors = [colorConverter.to_rgba(c) for c in ('r','g','b','c','y','m','k')]

fig = plt.figure()

a = fig.add_subplot(2,2,1)
col = collections.LineCollection([spiral], offsets=xyo,
                                transOffset=a.transData)
trans = fig.dpi_scale_trans + transforms.Affine2D().scale(1.0/72.0)
col.set_transform(trans)  # the points to pixels transform
    # Note: the first argument to the collection initializer
    # must be a list of sequences of x,y tuples; we have only
    # one sequence, but we still have to put it in a list.
a.add_collection(col, autolim=True)
    # autolim=True enables autoscaling.  For collections with
    # offsets like this, it is neither efficient nor accurate,
    # but it is good enough to generate a plot that you can use
    # as a starting point.  If you know beforehand the range of
    # x and y that you want to show, it is better to set them
    # explicitly, leave out the autolim kwarg (or set it to False),
    # and omit the 'a.autoscale_view()' call below.

# Make a transform for the line segments such that their size is
# given in points:
col.set_color(colors)

a.autoscale_view()  # See comment above, after a.add_collection.
a.set_title('LineCollection using offsets')


# The same data as above, but fill the curves.

a = fig.add_subplot(2,2,2)

col = collections.PolyCollection([spiral], offsets=xyo,
                                transOffset=a.transData)
trans = transforms.Affine2D().scale(fig.dpi/72.0)
col.set_transform(trans)  # the points to pixels transform
a.add_collection(col, autolim=True)
col.set_color(colors)


a.autoscale_view()
a.set_title('PolyCollection using offsets')

# 7-sided regular polygons

a = fig.add_subplot(2,2,3)

col = collections.RegularPolyCollection(7,
                                        sizes = np.fabs(xx)*10.0, offsets=xyo,
                                        transOffset=a.transData)
trans = transforms.Affine2D().scale(fig.dpi/72.0)
col.set_transform(trans)  # the points to pixels transform
a.add_collection(col, autolim=True)
col.set_color(colors)
a.autoscale_view()
a.set_title('RegularPolyCollection using offsets')


# Simulate a series of ocean current profiles, successively
# offset by 0.1 m/s so that they form what is sometimes called
# a "waterfall" plot or a "stagger" plot.

a = fig.add_subplot(2,2,4)

nverts = 600
ncurves = 20
offs = (0.1, 0.0)

yy = np.linspace(0, 2*np.pi, nverts)
ym = np.amax(yy)
xx = (0.2 + (ym-yy)/ym)**2 * np.cos(yy-0.4) * 0.5
segs = []
for i in range(ncurves):
    xxx = xx + 0.02*rs.randn(nverts)
    curve = list(zip(xxx, yy*100))
    segs.append(curve)

col = collections.LineCollection(segs, offsets=offs)
a.add_collection(col, autolim=True)
col.set_color(colors)
a.autoscale_view()
a.set_title('Successive data offsets')
a.set_xlabel('Zonal velocity component (m/s)')
a.set_ylabel('Depth (m)')
# Reverse the y-axis so depth increases downward
a.set_ylim(a.get_ylim()[::-1])


plt.show()



# <codecell>

#!/usr/bin/env python
'''Demonstration of LineCollection, PolyCollection, and
RegularPolyCollection with autoscaling.

For the first two subplots, we will use spirals.  Their
size will be set in plot units, not data units.  Their positions
will be set in data units by using the "offsets" and "transOffset"
kwargs of the LineCollection and PolyCollection.

The third subplot will make regular polygons, with the same
type of scaling and positioning as in the first two.

The last subplot illustrates the use of "offsets=(xo,yo)",
that is, a single tuple instead of a list of tuples, to generate
successively offset curves, with the offset given in data
units.  This behavior is available only for the LineCollection.

'''

import matplotlib.pyplot as P
from matplotlib import collections, axes, transforms
from matplotlib.colors import colorConverter
import numpy as N

nverts = 50
npts = 100

# Make some spirals
r = N.array(range(nverts))
theta = N.array(range(nverts)) * (2*N.pi)/(nverts-1)
xx = r * N.sin(theta)
yy = r * N.cos(theta)
spiral = zip(xx,yy)

# Make some offsets
rs = N.random.RandomState([12345678])
xo = rs.randn(npts)
yo = rs.randn(npts)
xyo = zip(xo, yo)

# Make a list of colors cycling through the rgbcmyk series.
colors = [colorConverter.to_rgba(c) for c in ('r','g','b','c','y','m','k')]

fig = P.figure()

a = fig.add_subplot(2,2,1)
col = collections.LineCollection([spiral], offsets=xyo,
                                transOffset=a.transData)
trans = fig.dpi_scale_trans + transforms.Affine2D().scale(1.0/72.0)
col.set_transform(trans)  # the points to pixels transform
    # Note: the first argument to the collection initializer
    # must be a list of sequences of x,y tuples; we have only
    # one sequence, but we still have to put it in a list.
a.add_collection(col, autolim=True)
    # autolim=True enables autoscaling.  For collections with
    # offsets like this, it is neither efficient nor accurate,
    # but it is good enough to generate a plot that you can use
    # as a starting point.  If you know beforehand the range of
    # x and y that you want to show, it is better to set them
    # explicitly, leave out the autolim kwarg (or set it to False),
    # and omit the 'a.autoscale_view()' call below.

# Make a transform for the line segments such that their size is
# given in points:
col.set_color(colors)

a.autoscale_view()  # See comment above, after a.add_collection.
a.set_title('LineCollection using offsets')


# The same data as above, but fill the curves.

a = fig.add_subplot(2,2,2)

col = collections.PolyCollection([spiral], offsets=xyo,
                                transOffset=a.transData)
trans = transforms.Affine2D().scale(fig.dpi/72.0)
col.set_transform(trans)  # the points to pixels transform
a.add_collection(col, autolim=True)
col.set_color(colors)


a.autoscale_view()
a.set_title('PolyCollection using offsets')

# 7-sided regular polygons

a = fig.add_subplot(2,2,3)

col = collections.RegularPolyCollection(7,
                                        sizes = N.fabs(xx)*10.0, offsets=xyo,
                                        transOffset=a.transData)
trans = transforms.Affine2D().scale(fig.dpi/72.0)
col.set_transform(trans)  # the points to pixels transform
a.add_collection(col, autolim=True)
col.set_color(colors)
a.autoscale_view()
a.set_title('RegularPolyCollection using offsets')


# Simulate a series of ocean current profiles, successively
# offset by 0.1 m/s so that they form what is sometimes called
# a "waterfall" plot or a "stagger" plot.

a = fig.add_subplot(2,2,4)

nverts = 60
ncurves = 20
offs = (0.1, 0.0)

yy = N.linspace(0, 2*N.pi, nverts)
ym = N.amax(yy)
xx = (0.2 + (ym-yy)/ym)**2 * N.cos(yy-0.4) * 0.5
segs = []
for i in range(ncurves):
    xxx = xx + 0.02*rs.randn(nverts)
    curve = zip(xxx, yy*100)
    segs.append(curve)

col = collections.LineCollection(segs, offsets=offs)
a.add_collection(col, autolim=True)
col.set_color(colors)
a.autoscale_view()
a.set_title('Successive data offsets')
a.set_xlabel('Zonal velocity component (m/s)')
a.set_ylabel('Depth (m)')
# Reverse the y-axis so depth increases downward
a.set_ylim(a.get_ylim()[::-1])

P.show()

# <codecell>

import SimpleITK as sitk
print sitk.sitkUnknown, "sitk.sitkUnknown"
print sitk.sitkUInt8
print sitk.sitkInt8
print sitk.sitkUInt16
print sitk.sitkInt16
print sitk.sitkUInt32
print sitk.sitkInt32
print sitk.sitkUInt64, "sitk.sitkUInt64"
print sitk.sitkInt64, "sitk.sitkInt64"
print sitk.sitkFloat32
print sitk.sitkFloat64
print sitk.sitkComplexFloat32
print sitk.sitkComplexFloat64
print sitk.sitkLabelUInt16, "sitk.sitkLabelUInt16"
print sitk.sitkLabelUInt32
print sitk.sitkLabelUInt64, "sitk.sitkLabelUInt64"
print sitk.sitkVectorFloat32
print sitk.sitkVectorFloat64
print sitk.sitkVectorUInt8
print sitk.sitkVectorInt8
print sitk.sitkVectorUInt16
print sitk.sitkVectorInt16
print sitk.sitkVectorUInt32
print sitk.sitkVectorInt32, "sitk.sitkVectorInt32"

# <codecell>


