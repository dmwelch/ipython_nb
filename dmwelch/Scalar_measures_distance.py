# -*- coding: utf-8 -*-
import keyring
import math
import psycopg2 as sql
import os

def calculateIPD(dirname):
    """ Calculate the interpupilary distance from the left and right eye landmarks in BCD_ACPC_Landmarks.fcsv """
    filename = os.path.join(dirname, 'BCD_ACPC_Landmarks.fcsv')
    with open(filename, 'r') as fid:
        for line in fid.readlines():
            if line[:2] == 'LE':
                # print line
                left_eye = line
            elif line[:2] == 'RE':
                # print line
                right_eye = line
            else:
                pass
    _, x_left, y_left, z_left, __, ___ = left_eye.split(',')
    _, x_right, y_right, z_right, __, ___ = right_eye.split(',')
    dist = math.sqrt((float(x_left) - float(x_right)) ** 2 + (float(y_left) - float(y_right)) ** 2 + (float(z_left) - float(z_right)) ** 2)
    return dist

insertFunction = "SELECT add_measurements(%s,%s,%s,%s,%s,%s)"
# Connect to database
password = keyring.get_password('Postgres', 'autoworkup')
connection = sql.connect(host='psych-db.psychiatry.uiowa.edu',port=5432, database='imagingmeasurements',
                         user='autoworkup', password=password)
experimentPaths = ['/paulsen/Experiments/20130202_PREDICTHD_Results', '/hjohnson/TrackOn/Experiments/20130109_TrackOn_Results/']
for currentPath in experimentPaths:
    for base, dirs, files in os.walk(currentPath):
        if 'BCD_ACPC_Landmarks.fcsv' in files:
            print '.',
            pathElements = base.split(os.path.sep)
            assert pathElements.pop() == 'ACPCAlign'
            session = pathElements.pop()
            subject = pathElements.pop()
            site = pathElements.pop()
            experiment = pathElements.pop()
            tool = experiment.split('_')[0]
            tool = "BRAINSTools_" + tool
            cursor = connection.cursor()
            try:
                cursor.execute(insertFunction, (experiment, session, 'interpupilary_distance', 'mm', calculateIPD(base), tool))
            except Exception, err:
                connection.close()
                raise err # ???
            connection.commit()
connection.close()
print "Success"
