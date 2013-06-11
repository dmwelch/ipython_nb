#!/bin/env python

import os

import psycopg2 as sql

def main():
    POSTERIOR_DIR = '/paulsen/Experiments/20130202_PREDICTHD_Results/SubjectToAtlasWarped/'
    connection = pinc.connectToPostgres(database='AutoWorkUp')

    atlas = sitk.ReadImage('/ipldev/scratch/welchdm/bld/BTools-20130312/ReferenceAtlas-build/Atlas/Atlas_20130106/avg_t1.nii.gz')
    zero_l = atlas * 0
    zero_r = atlas * 0
    sumImg_r = sitk.Cast(zero_r, sitk.sitkFloat32)
    sumImg_l = sitk.Cast(zero_l, sitk.sitkFloat32)
    count_r = 0
    count_l = 0
    query_r = "select review_id, putamen_right from image_reviews where record_id = (select record_id from derived_images where _session = '%s' and _analysis = '20130202_PREDICTHD_Results') and putamen_right = 1"
    query_l = "select review_id, putamen_left from image_reviews where record_id = (select record_id from derived_images where _session = '%s' and _analysis = '20130202_PREDICTHD_Results') and putamen_left = 1"

    for directory in os.listdir(POSTERIOR_DIR):
        if os.path.isdir(os.path.join(POSTERIOR_DIR, directory)):
            print directory
            cursor = connection.cursor()
            cursor.execute(query_r % directory)
            result = cursor.fetchone()
            if not result is None:
                filepath = os.path.join(POSTERIOR_DIR, directory, 'cleaned_r_putamen_seg_trans.nii.gz')
                if os.path.exists(filepath):
                    test = sitk.ReadImage(filepath)
                    sumImg_r += test
                    del test
                    count_r +=1
            cursor.execute(query_l % directory)
            result = cursor.fetchone()
            if not result is None:
                filepath = os.path.join(POSTERIOR_DIR, directory, 'cleaned_l_putamen_seg_trans.nii.gz')
                if os.path.exists(filepath):
                    test = sitk.ReadImage(filepath)
                    sumImg_l += test
                    del test
                    count_l +=1
            cursor.close()
            # if count_l > 20:
            #     break
    print "There were %d right and %d left files found" % (count_r, count_l)
    sumImg_r = sumImg_r / float(count_r)
    sumImg_l = sumImg_l / float(count_l)
    sitk.WriteImage(sumImg_r, '/ipldev/scratch/welchdm/generateNewPriors-20130426/sumGood/averagePutamen_%d_right.nii.gz' % count_r)
    sitk.WriteImage(sumImg_l, '/ipldev/scratch/welchdm/generateNewPriors-20130426/sumGood/averagePutamen_%d_left.nii.gz' % count_l)


if __name__ == "__main__":
    import sys
    sys.path = ['/ipldev/scratch/welchdm/bld/rs-fMRI/BSA/SimpleITK-build/Wrapping',
                '/ipldev/scratch/welchdm/bld/rs-fMRI/BSA/SimpleITK-build/lib',
                '/ipldev/scratch/welchdm/bld/rs-fMRI/BSA/SimpleITK-build/bin',
                '/ipldev/sharedopt/ipython_notebooks/common'] + sys.path
    import SimpleITK as sitk
    import pinc
    main()
