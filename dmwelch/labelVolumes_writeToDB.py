# -*- coding: utf-8 -*-
import os
from decimal import Decimal
import pinc

# CSVFileName = '/raid0/homes/dmwelch/Desktop/predicthd_volumes.csv'
# baseDir = '/paulsen/Experiments/20130202_PREDICTHD_Results'
CSVFileName = '/raid0/homes/dmwelch/Desktop/trackon_volumes.csv'
baseDir = '/hjohnson/TrackOn/Experiments/20130109_TrackOn_Results/'
# Connect to database
connection = pinc.connectToPostgres()

insertFunction = "SELECT add_measurements(%s,%s,%s,%s,%s,%s)"
# Read csv file
printOut = False
count = 0
found = None
allValues = []
with open(CSVFileName, 'r') as fid:
    for record in fid.readlines():
        values = []
        if count == 0:
            count += 1
            # print "Header found"
        else:
            values = record.split(',')
            if not found is None and printOut:
                print "x", # print without c/r, similar to printf
            else:
                if printOut:
                    print ".", # print without c/r, similar to printf
                    if (count - 1) % 13 == 0:
                        print ""
                if values[4][2:] == "accumben":
                    # Fix accumbens typo in csv file
                    values[4] += 's'
                allValues.append((values[0], values[3], values[4], 'mm_3', Decimal(values[-2]), 'BRAINSTools_20130109'))
                count += 1
# Insert values
count = 0
for test in allValues:
    print '.',
    cursor = connection.cursor()
    try:
        # print cursor.mogrify(insertFunction, test)
        cursor.execute(insertFunction, test)
        count += 1
    except Exception, err:
        connection.close()
        raise err
    connection.commit()
    # if count > 30:
    #     break
connection.close()

