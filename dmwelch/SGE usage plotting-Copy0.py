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
filename = '/hjohnson/HDNI/20121219_MakeClusterAccountingGraphs/tempAcct'
header = ('qname', 'hostname', 'group', 'owner', 'job_name', 'job_number', 'account', 'priority', 'submission_time', 'start_time', 
          'end_time', 'failed', 'exit_status', 'ru_wallclock', 'ru_utime', 'ru_stime', 'ru_maxrss', 'ru_ixrss', 'ru_ismrss', 'ru_idrss', 
          'ru_isrss', 'ru_minflt', 'ru_majflt', 'ru_nswap', 'ru_inblock', 'ru_oublock', 'ru_msgsnd', 'ru_msgrcv', 'ru_nsignals', 'ru_nvcsw', 
          'ru_nivcsw', 'project', 'department', 'granted_pe', 'slots', 'task_number', 'cpu', 'mem', 'io', 'category', 'iow', 'pe_taskid',
          'maxvmem', 'arid', 'ar_submission_time')
subtime = []
submissiontime = []
usertime = []
systime = []
cputime = []
wallclock = []
with open(filename, 'rb') as fid:
    csvOut = csv.DictReader(fid, fieldnames=header, restkey='Extra_stuff', delimiter=':', quotechar='"')
    count = 0
    #test = dict()
    #values = [()]*45
    for row in csvOut.reader:
        temp = dict(zip(header, row))
        #test[str(count)] = temp
        #count += 1
        submissiontime.append(temp['submission_time'])
        subtime.append(time.ctime(int(temp['submission_time'])))
        usertime.append(temp['ru_utime'])
        systime.append(temp['ru_stime'])
        cputime.append(temp['cpu'])
        wallclock.append(temp['ru_wallclock'])
        #print temp# ', '.join(row)
        #print '\n'
        #if count > 1:
        #    break

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
mcount = 0
for month in ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'):
    mcount += 1
    monthDict = timeDict['2012'][month]
    # print month
    for day in range(1,32):
        if str(day) in monthDict.keys():
            # print month, day
            count.append(monthDict[str(day)]['cputime'])
            stimes.append(mcount*100 + day)
mysum = sum(count)
print "Years: %g" % ((mysum / (((60.0**2) * 24.0) * 365.25)))

# <codecell>

import matplotlib.dates as mdates

locator = mdates.AutoDateLocator(minticks=0, maxticks=12, interval_multiples=True)
locator.intervald[MONTHLY] = [6]
formator = mdates.AutoDateFormatter(locator)

fig = figure()
fig.add_subplot(111)
gca().xaxis.set_major_formatter(formator)
gca().xaxis.set_major_locator(locator)
plot(stimes, count, color='black', marker=',')
gcf().autofmt_xdate()
fig.suptitle('Helium Usage: HJohnson')
myaxes = gca()
gca().xaxis.set_label_text('Days')
gca().yaxis.set_label_text('CPU time')

# <codecell>

gcf().display()

# <codecell>


