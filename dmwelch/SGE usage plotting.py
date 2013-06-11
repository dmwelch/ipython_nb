# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Cluster usage

# <markdowncell>

# <em>Generate the account file for user johnsonhj on Helium</em>
# 
#     qacct -o johnsonhj -b 1201010000 -f /opt/gridengine/default/common/accounting-10-15-2012
#     qacct -o johnsonhj
# 
# <em>The format of the accounting file is:</em>
# > qname:hostname:group:owner:job_name:job_number:account:priority:submission_time:start_time:end_time:failed:exit_status:
# ru_wallclock:...(UNIX getrusage)...:project:department:granted_pe:slots:task_number:cpu:mem:io:category:iow:pe_taskid:
# maxvmem:arid:ar_submission_time
# 
# * <em>submission_time - Submission time (GMT unix time stamp)</em>
# * <em>cpu - The cpu time usage in seconds</em>
# * <em>ru_wallclock - Difference between end_time and start_time</em>
# * <em>ru_utime - user time used (from getrusage)</em>
# * <em>ru_stime - system time used (from getrusage)</em>

# <codecell>

import csv
import time
filename1 = '/hjohnson/HDNI/20121219_MakeClusterAccountingGraphs/tempAcct'
filename2 = '/raid0/homes/dmwelch/regina.txt'

def parseSGElog(filename):
    header = ('qname', 'hostname', 'group', 'owner', 'job_name', 'job_number', 'account', 'priority', 'submission_time', 'start_time', 
              'end_time', 'failed', 'exit_status', 'ru_wallclock', 'ru_utime', 'ru_stime', 'ru_maxrss', 'ru_ixrss', 'ru_ismrss', 'ru_idrss', 
              'ru_isrss', 'ru_minflt', 'ru_majflt', 'ru_nswap', 'ru_inblock', 'ru_oublock', 'ru_msgsnd', 'ru_msgrcv', 'ru_nsignals', 'ru_nvcsw', 
              'ru_nivcsw', 'project', 'department', 'granted_pe', 'slots', 'task_number', 'cpu', 'mem', 'io', 'category', 'iow', 'pe_taskid',
              'maxvmem', 'arid', 'ar_submission_time')
    #subtime = []
    submissiontime = []
    #usertime = []
    #systime = []
    cputime = []
    #wallclock = []
    with open(filename, 'rb') as fid:
        csvOut = csv.DictReader(fid, fieldnames=header, restkey='Extra_stuff', delimiter=':', quotechar='"')
        count = 0
        for row in csvOut.reader:
            temp = dict(zip(header, row))
            submissiontime.append(int(temp['submission_time']))
            #subtime.append(time.ctime(int(temp['submission_time'])))
            #usertime.append(temp['ru_utime'])
            #systime.append(temp['ru_stime'])
            cputime.append(temp['cpu'])
            #wallclock.append(temp['ru_wallclock'])
    output = sorted(zip(submissiontime, cputime))
    return output
hans = parseSGElog(filename1)
regina = parseSGElog(filename2)

# <codecell>

test = zip([1,3,2,7,5,6,4], [20,6,4,14,10,12,8])
sorted_test = sorted(test)
sorted_test

# <codecell>

resultList = []
oldDay = 0
oldMonth = 'Xxx'
cpusum = 0.0
for tstamp, cpu in hans:
    readableTime = time.ctime(tstamp)
    dateList = readableTime.split(' ')
    if int(dateList[-1]) < 2011:
        pass
    month = dateList[1]
    if dateList[2] == '':
        day = int(dateList[3])
    else:
        day = int(dateList[2])
    if month != oldMonth or day != oldDay:
        resultList.append(('%s-%s'%(oldMonth, oldDay), cpusum))
        oldMonth = month
        oldDay = day
        cpusum = float(cpu)
    else:
        cpusum += float(cpu)
        
print len(resultList)

# <codecell>

dates, cpusums = zip(*resultList)
dayCount = [float(value) / ((60.0**2) * 24.0) for value in cpusums]
leftBar = [float(x) - 0.5 for x in range(1,13)]
fig = figure()
ax = fig.add_subplot(111)
bar(left, dayCount, color='red')

# <codecell>

timeDict = dict()
for index in range(len(subtime)):
    stime = subtime[index]
    dateList = stime.split(' ')
    month = dateList[1]
    year = dateList[-1]
    day = dateList[2]
    if day == '':
        day = dateList[3]
    if year in timeDict.keys():
        if month in timeDict[year].keys():
            if day in timeDict[year][month].keys():
                pass
            else:
                timeDict[year][month][day] = {'cputime':0.0,'systime':0.0, 'usertime':0.0, 'walltime':0.0}
        else:
            timeDict[year][month] = {day:{'cputime':0.0,'systime':0.0, 'usertime':0.0, 'walltime':0.0}}
    else:
        timeDict[year] = {month:{day:{'cputime':0.0,'systime':0.0, 'usertime':0.0, 'walltime':0.0}}}
    timeDict[year][month][day]['cputime'] += float(cputime[index])
    timeDict[year][month][day]['systime'] += float(systime[index])
    timeDict[year][month][day]['usertime'] += float(usertime[index])
    timeDict[year][month][day]['walltime'] += float(wallclock[index])

# <codecell>

print timeDict.keys()
print timeDict['1969']

# <codecell>

count = 0.0
for month, monthDict in timeDict['2012'].iteritems():
    for day, dayDict in monthDict.iteritems():
        count += dayDict['cputime']
print "Years: %g" % ((count / (((60.0**2) * 24.0) * 365.25)))

# <codecell>

count = []
stimes = []
for month in ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'):
    monthDict = timeDict['2012'][month]
    # print month
    mcount = 0.0
    for day in range(1,32):
        if str(day) in monthDict.keys():
            # print month, day
            mcount += monthDict[str(day)]['cputime']
    count.append(mcount)
    stimes.append(month)
    #stimes.append(str(mcount).zfill(2) + '-' + str(day).zfill(2))
mysum = sum(count)
print "Years: %g" % ((mysum / (((60.0**2) * 24.0) * 365.25)))

# <codecell>

import matplotlib.dates as mdates

locator = mdates.AutoDateLocator(minticks=12, maxticks=12, interval_multiples=False)
locator.intervald[MONTHLY] = [1]
formator = mdates.AutoDateFormatter(locator)
dayCount = [value / ((60.0**2) * 24.0) for value in count]
leftBar = [float(x) - 0.5 for x in range(1,13)]
fig = figure()
ax = fig.add_subplot(111)
#gca().xaxis.set_major_formatter(formator)
#gca().xaxis.set_major_locator(locator)
#plot(stimes, count, color='black', marker=',')
# gcf().autofmt_xdate()
ax.bar(leftBar, dayCount, color='red', capsize=0)
myaxes = gca()
fig.suptitle('Helium Usage (2011): Hans Johnson')
#fig.suptitle('Helium Usage (2011): Eun Young Kim')
myaxes.xaxis.set_label_text('Month')
myaxes.yaxis.set_label_text('CPU days / month')

# <codecell>

import matplotlib.collections as mcollect

import numpy as np
tlocs = myaxes.yaxis.get_majorticklocs() 
MAX = max(tlocs)
for tick in tlocs:
    if tick == MAX:
        pass
    for ADDME in range(1,11):
        thiscolor = ((1.0*(tick+float(ADDME)))/MAX, 
                     0.0, 
                     1.0 - (1.0*(tick+float(ADDME)))/MAX)
        red = thiscolor[0] - mod(thiscolor[0]*100, 1)/100
        blue = thiscolor[2] - mod(thiscolor[2]*100, 1)/100
        if red >= 1.0:
            red = 0.99
        if blue < 0:
            blue = 0
        #print thiscolor, red, blue
        collection = mcollect.BrokenBarHCollection.span_where(np.arange(0.5, 12.5, 0.5), ymin=0, 
                                                              ymax=1, #tick+10.0, 
                                                              where=[point > 0 for point in dayCount], 
                                                              facecolor=(red, 0.0, blue), 
                                                              alpha=0.5)
        ax.add_collection(collection)  
        show()

# <codecell>

from matplotlib.colors import LinearSegmentedColormap
mymap = LinearSegmentedColormap('cold2hot', {'red':[(0.0,)*3, (1.0, 0.0, 0.0)], 'green':[(0.0,)*3], 'blue':[(1.0, 0.0, 0.0), (0.0,)*3]}, N=256)

# <rawcell>

# http://stackoverflow.com/questions/10958835/matplotlib-color-gradient-in-patches

# <codecell>

Ymax = max(dayCount)
Ymin = 0.0
Xmax = 12.5
Xmin = 0.5
x = np.arange(Xmin, Xmax, 0.05)
y = np.arange(Ymin, Ymax+10.0, 0.05)
X,Y = meshgrid(x,y)
fig = figure(frameon=False)
import numpy as np
for item in dayCount:
    Xmax = Xmin + 1.0
    
    im = imshow(
    y = np.arange(Ymin, item, 0.05)
    

# <codecell>

thiscolor[0] - mod(thiscolor[0]*100, 1)/100

# <codecell>


