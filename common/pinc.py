#
#  This file contains some common code that can be used in many
#  ipython notebooks.  As we find little gems of programming
#  that can benefit the PINC lab, they should be put here.
#
#  From your private notebook library "/ipldev/sharedopt/ipython_notebooks/${LOGNAME}/"
#  make a link to "../common/pinc.py"
#
#  From your notebook, do a "from pinc import *" to get all these functions
#
#

import keyring
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import collections, transforms
from matplotlib.colors import colorConverter
import numpy as np
import psycopg2 as sql
import SimpleITK as sitk

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
    fig=plt.figure(1)
    fig.add_subplot(121)
    myplot=plt.imshow(np_image, cmap=mpl.cm.gray, interpolation=None)
    myplot.set_label("T2_image")
    plt.title(title)
    fig.add_subplot(122)
    myplot=plt.imshow(np_image, cmap=mpl.cm.Reds, interpolation=None)
    myplot.set_label("xxxT2_image")
    plt.title(title)
    plt.show()
    return fig


def vDisplayCenterSlice(images, titles, referenceSlicePercentage=0.5):
    """ Display the center slice of an sitkImage"""
    num_images=len(images)
    num_title=len(titles)
    if num_images != num_title:
        print "ERROR: images and titles must be the same length."
        return None
    fig=plt.figure(1)
    for img_idx in range(0,num_images):
        subplotnumber=100+(num_images)*10+(1+img_idx)
        size=list(images[img_idx].GetSize())
        dims=images[img_idx].GetDimension()
        if dims == 2:
            index=[0,0]
        else:
           index=[0,0,int(size[2]*referenceSlicePercentage)]
           size[2]=0
        twoDImage=sitk.Extract(images[img_idx],size,index)
        np_image=sitk.GetArrayFromImage(twoDImage)
        fig.add_subplot(subplotnumber)
        myplot=plt.imshow(np_image, cmap=mpl.cm.gray, interpolation=None)
#myplot.set_label(titles[img_idx])
        plt.title(titles[img_idx])
#plt.show()
#return fig

def binaryBoundingBoxMask(image, returnPoints=False):
    """ Given a binary image, return a binary bounding box mask image in the same space """
    array = sitk.GetArrayFromImage(image)
    non_zero = np.nonzero(array)
    extremes = []
    for dd in range(array.ndim):
        extremes.append((np.min(non_zero[dd]), np.max(non_zero[dd])))
    evalString = ""
    for ii in range(array.ndim):
        evalString += "np.arange(*extremes[{0}]), ".format(ii)
    evalString = evalString[:-2]
    indicies = eval("np.ix_(" + evalString + ")")
    array[indicies] = array.max()
    output = sitk.GetImageFromArray(array)
    output.CopyInformation(image)
    if True:
        vDisplayCenterSlice([output-image], ['Double-check'], 0.5)
    if returnPoints:
        pt1 = []
        pt2 = []
        for jj in range(len(extremes)):
            pt1.append(extremes[jj][0])
            pt2.append(extremes[jj][1])
        return output, (pt1, pt2)
    return output


def connectToPostgres(user='autoworkup', database='imagingmeasurements'):
    """
    Connect to postgres databases at psych-db.psychiatry.uiowa.edu
    Nota Bene: You must have your password in your keyring

    Inputs:
        user: string, default = 'autoworkup'
        database: string, default = 'imagingmeasurements'

    Outputs: psycopg2.connection
    """
    password = keyring.get_password('Postgres', user)
    connection = sql.connect(host='psych-db.psychiatry.uiowa.edu', port=5432, database=database,
                             user=user, password=password)
    return connection
