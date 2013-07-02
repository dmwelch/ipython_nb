import os.path
import SimpleITK as sitk

def imageList(d, keys):
    images = []
    for key in keys:
        images.append(d[key])
    return images

def sumOverKeys(d, keys):
    castList = [sitk.Cast(image, sitk.sitkFloat32) for image in imageList(d, keys)]
    return sitk.NaryAdd(castList)

def clamp(image, lowerThreshold=0.001, lowerValue=0.0, upperThreshold=0.999, upperValue=1.0):
    """
    Given an image, clamp all values below the lower threshold to the lower value and all values
    above the upper threshold to the upper value

    Inputs:
    `image`:  <SimpleITK Image>
    `lowerThreshold`:  float, default=0.001
    `lowerValue`:  float, default=0.0
    `upperThreshold`:  float, default=0.999
    `upperValue`:  float, default=1.0
    """
    stats = sitk.Statistics(image)
    image_max = stats["Maximum"]
    # Lower clamping
    lowered = sitk.Threshold(image, lower=lowerThreshold, upper=image_max, outsideValue=lowerValue)
    l_stats = sitk.Statistics((lowered >= lowerValue) - (lowered >= lowerThreshold))
    assert l_stats["Sum"] == 0, "There are values between %g and %g!" % (lowerValue, lowerThreshold)
    # Upper clamping
    clamped = sitk.Threshold(lowered, lower=lowerValue, upper=upperThreshold, outsideValue=upperValue)
    c_stats = sitk.Statistics((clamped < upperValue) - (clamped <= upperThreshold))
    assert c_stats["Sum"] == 0, "There are values between %g and %g!" % (upperValue, upperThreshold)
    return clamped

def truncate(image, ndigits=0):
    """ Truncate to the given number of digits """
    from decimal import Decimal
    import numpy as np
    narray = sitk.GetArrayFromImage(image)
    rounded = np.around(narray, decimals=ndigits)
    truncated = sitk.GetImageFromArray(rounded)
    truncated.CopyInformation(image)
    return truncated

def newfilename(filename, dirname, suffix, sep="_", extension=".nii.gz"):
    """ Create new filename in dirname with suffix before extension """
    fname = os.path.basename(filename)
    strList = fname.split(sep)
    newfname = ""
    if sep != ".":
        newfname = sep.join(strList[:-1] + [suffix + extension])
    return os.path.join(dirname, newfname)

def createImageMap(**kwds):
    """
    d = createImageMap(AIR='/my/dir/POSTERIOR_AIR.nii.gz')
    """
    output = {}
    for key, value in kwds.items():
        if not os.path.exists(value):
            raise IOError, value
        output[key] = sitk.ReadImage(value)
    return output

def dumpImageMap(d, dirname, prefix="", suffix="", sep="", ext=".nii.gz"):
    for key, value in d.items():
        fList = [prefix, key, suffix]
        if prefix == "":
            fList = fList[1:]
        if suffix == "":
            fList = fList[:-1]
        filename = sep.join(fList) + ext
        print filename
        sitk.WriteImage(value, osjoin(dirname, filename))

def checkStats(d, checks=['max', 'min'], tolerance=1e-5, verbose=False):
    for key, value in d.items():
        stat = sitk.Statistics(value)
        for check in checks:
            if check == 'min':
                assert stat["Minimum"] == abs(stat["Minimum"]), "Minimum is {0} for {1}".format(stat["Minimum"], key)
            elif check == 'max':
                assert stat["Maximum"] < 1.0 + tolerance, "Maximum is {0} more than tolerance for {1}".format(stat["Maximum"] - (1.0 + tolerance), key)
            else:
                raise NotImplementedError
        if verbose:
            #for skey, svalue in stat.items():
            #    print key, ":", skey, "---", svalue
            print key, ":", "Maximum ---", stat["Maximum"]
            print key, ":", "Minimum ---", stat["Minimum"]
            print "=" * 50
    print "Check passes for", checks

def sumPosteriors(inputDict):
    airKeys = [key for key in inputDict.keys() if key[1] != "_"]  # Get all the keys that **aren't** a segmentation
    posteriorSum = sumOverKeys(inputDict, airKeys)
    return posteriorSum

def correctAir(air, summed, show=False):
    """ Given the air image and the summed image of all posteriors, correct the air values lying on the periphery and return the image """
    from myshow import myshow, myshow3d

    sum_mask = sitk.BinaryThreshold(summed, lowerThreshold=1.0, insideValue=0, outsideValue=1)
    if show: myshow(sum_mask, "Mask of summed @ 1.0")
    relabel_mask = sitk.RelabelComponent(sitk.ConnectedComponent(sum_mask))
    if show: myshow(sitk.LabelToRGB(relabel_mask), "Relabeled mask")
    clean_mask = relabel_mask==1
    if show:
        myshow(clean_mask, "Cleaned mask")
        myshow(air, "Original air")
    fixed_air = air + sitk.Cast(clean_mask, air.GetPixelIDValue())
    open_mask = sitk.BinaryMorphologicalOpening(fixed_air>0.01, 3)
    fixed_air = sitk.Mask(fixed_air, open_mask)
    if show: myshow(fixed_air, "Fixed air")
    return fixed_air

def createResidualImage(d, ikeys, mkeys):
    """
    For a list of images and masks, sum both groups (summed image and summed mask) and return the summed image
    masked with the NOT summed mask
    """
    invert_mask = sumOverKeys(d, mkeys) < 1
    res_sum = sumOverKeys(d, ikeys)
    residual = sitk.Mask(res_sum, invert_mask)
    # assert sitk.Statistics(residual)["Maximum"] > 0.0, "residual is empty for %s" % orig
    return residual

def maskImages(d, mask, maskKeys=[]):
    """
    If mask is inverted, maskKeys must be given so that the images making up the mask aren't masked themselves
    """
    dout = {}
    for key in maskKeys:
        dout[key] = d[key]
    for key in d.keys():
        if not key in maskKeys:
            dout[key] = sitk.Mask(d[key], mask)
    return dout

def createMask(d, maskKeys, invert=False):
    mask = sumOverKeys(d, maskKeys)
    if invert:
        mask = mask < 1
    return mask

def SoftMask(image, x, method='FWTM'):
    """
    Returns the Gaussian blurred (soft) mask of a binary (hard) mask with either:
        * full-width-approx-zero (FWAZ) width
        * full-width-tenth-max (FWTM) width (default)
        * full-width-half-max (FWHM) width

    Note: FWTM has been found to be the most intuitive of the three, giving a 'noticible' blur for 1 mm
    """
    import math
    if method.lower() == "fwtm":
        # print "FWTM"
        z = 10.0
    elif method.lower() == "fwaz":
        # print "FWAZ"
        z = 100.0
    elif method.lower() == "fwhm":
        # print "FWHM"
        z = 2.0
    factor = 2.0 * math.sqrt(2.0 * math.log(z))
    sigma = float(x) / factor
    # print sigma
    variance = sigma ** 2
    if image.GetPixelIDValue() != sitk.sitkUInt8:
        raise IOError
    soft = sitk.DiscreteGaussian(sitk.Cast(image, sitk.sitkFloat32), variance=float(variance))
    return soft


def gammaScale(img1, img2, variance):
    mass = img1 + img2
    assert sitk.Statistics(mass)['Minimum'] == abs(sitk.Statistics(mass)['Minimum'])
    img1_g = sitk.DiscreteGaussian(img1, variance)
    img2_g = sitk.DiscreteGaussian(img2, variance)
    # Bring up values to > 0.0
    min1 = sitk.Statistics(img1_g)['Minimum']
    img1_g = img1_g - min1
    min2 = sitk.Statistics(img2_g)['Minimum']
    img2_g = img2_g - min2
    summed = img1_g + img2_g
    assert sitk.Statistics(summed)['Minimum'] == abs(sitk.Statistics(summed)['Minimum'])
    scale = mass / summed
    return img1_g * scale, img2_g * scale

def normalizeImages(d, verify=True, tolerance=1e-5):
    """
    Takes in a list of images and normalizes them s.t. the voxels in the sum of the images is rougly equivalent to 1
    """
    mag = sumOverKeys(d, d.keys())  # Magnitude image
    # Normalize by the magnitude image
    n_image_list = []
    count = 0
    dout = {}
    verifyImage(mag, "magnitude", tolerance)
    for key, image in d.items():
        n_img = sitk.Cast(image, sitk.sitkFloat32) / mag  ### <--- How to handle over/underflow?
        if verify: verifyImage(n_img, key, tolerance)
        dout[key] = n_img
    if verify:
        testNormalizeImages(mag, imageList(dout, dout.keys()), tolerance=tolerance)
    return dout

def verifyImage(image, image_key, tolerance):
    c_stats = sitk.Statistics(image)
    for key, value in c_stats.items():
        if isnan(value):
            print "%s is NaN for image %s" % (key, image_key)
            raise ValueError
        if isinf(value):
            print "%s is Inf for image %s" % (key, image_key)
            raise ValueError
        if key == 'Minimum' and value < 0.0:
            print "Minimum is negative for image {0}".format(image_key)
        if key == "Maximum" and value > 1.0 + tolerance:
            print "Maximum is greater than 1.0 for image {0}".format(image_key)

def testNormalizeImages(mag, n_image_list, tolerance=1e-5):
    n_mag = sitk.NaryAdd(n_image_list)
    # Verify the normalization
    m_stats = sitk.Statistics(mag)
    n_stats = sitk.Statistics(n_mag)
    assert n_stats["Variance"] <= m_stats["Variance"], "Variance in image sum was not reduced! Original: %f\t Normal: %f" % (n_stats["Variance"], m_stats["Variance"])
    assert n_stats["Maximum"] < 1.0 + tolerance, "Maximum summed value is outside tolerance: %f" % n_stats["Maximum"]
    assert n_stats["Minimum"] > 1.0 - tolerance, "Minimum summed value is outside tolerance: %f" % n_stats["Minimum"]

def copyDict(old, new={}):
    """
    Copy key, value pairs into new dictionary from old, unless new already has the key
    """
    for key in old.keys():
        if key in new.keys():
            continue
        else:
            new[key] = old[key]
    return None, new
