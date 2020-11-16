#!/bin/python3
# if used ubuntu 20.10 or later, interpreter set as #!/bin/python and use pip instead of pip3

# =================================================================== #
# platfrom check
# dateutil check and import
try:
    from dateutil.relativedelta import relativedelta
except:
    import os,sys,subprocess
    if os.name=='nt':
        subprocess.check_call([sys.executable, "-m", "pip", "install", "dateutil"])
    elif os.name=='posix'
        subprocess.check_call([sys.executable, "-m", "pip3", "install", "dateutil"])
    else:
        raise "Unknow platform, please install 'dateutil' by yourself."
    from dateutil.relativedelta import relativedelta
# =================================================================== #
# platfrom check
# numpy check and import
try:
    import numpy as np
except:
    import os,sys,subprocess
    if os.name=='nt':
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    elif os.name=='posix'
        subprocess.check_call([sys.executable, "-m", "pip3", "install", "numpy"])
    else:
        raise "Unknow platform, please install 'numpy' by yourself."
    import numpy as np
# =================================================================== #
import datetime

class Timean(object):
    def _check_data(self):
        if not "self.time" in locals(): raise "Please check input time."
        if not "self.data" in locals(): raise "Please check input data."
        return True

    def input(self,time,data):
        '''
        time <datetime> : input timelist of data
        data <numerical>: input data array
        '''
        self.time = np.array(time)
        self.data = np.array(data)
        self.counts = []
        return "Successfully"

    def isrepeat(self):
        if len(self.time.reshape(-1))==len(set(self.time)):
            return False
        else:
            return True

    def second(self):
        minTime = np.nanmin(self.time)
        maxTime = np.nanmax(self.time)
        dt = datetime.timedelta(seconds=1)

        if maxTime.microsecond==0: maxTime+=datetime.timedelta(seconds=1)

        dummy = []
        tummy = []
        count = []
        while minTime<=maxTime:
            mask = np.where(self.time>=minTime and self.time<maxTime)[0]
            dummy.append(np.nanmean(self.data[mask],axis=0))
            tummy.append(self.time[mask[0]])
            count.append(np.sum(np.isfinite(self.data[mask])))
        self.data = np.array(dummy)
        self.time = np.array(tummy)
        self.counts = np.array(count)
    
    def minute(self):
        minTime = np.nanmin(self.time)
        maxTime = np.nanmax(self.time)
        dt = datetime.timedelta(minutes=1)

        if maxTime.microsecond==0: maxTime+=datetime.timedelta(minutes=1)

        dummy = []
        tummy = []
        count = []
        while minTime<=maxTime:
            mask = np.where(self.time>=minTime and self.time<maxTime)[0]
            dummy.append(np.nanmean(self.data[mask],axis=0))
            tummy.append(self.time[mask[0]])
            count.append(np.sum(np.isfinite(self.data[mask])))
        self.data = np.array(dummy)
        self.time = np.array(tummy)
        self.counts = np.array(count)

    def hour(self):
        minTime = np.nanmin(self.time)
        maxTime = np.nanmax(self.time)
        dt = datetime.timedelta(hours=1)

        if maxTime.microsecond==0: maxTime+=datetime.timedelta(hours=1)

        dummy = []
        tummy = []
        count = []
        while minTime<=maxTime:
            mask = np.where(self.time>=minTime and self.time<maxTime)[0]
            dummy.append(np.nanmean(self.data[mask],axis=0))
            tummy.append(self.time[mask[0]])
            count.append(np.sum(np.isfinite(self.data[mask])))
        self.data = np.array(dummy)
        self.time = np.array(tummy)
        self.counts = np.array(count)
    
    def day(self):
        minTime = np.nanmin(self.time)
        maxTime = np.nanmax(self.time)
        dt = datetime.timedelta(days=1)

        if maxTime.microsecond==0: maxTime+=datetime.timedelta(days=1)

        dummy = []
        tummy = []
        count = []
        while minTime<=maxTime:
            mask = np.where(self.time>=minTime and self.time<maxTime)[0]
            dummy.append(np.nanmean(self.data[mask],axis=0))
            tummy.append(self.time[mask[0]])
            count.append(np.sum(np.isfinite(self.data[mask])))
        self.data = np.array(dummy)
        self.time = np.array(tummy)
        self.counts = np.array(count)
    
    def month(self):
        minTime = np.nanmin(self.time)
        maxTime = np.nanmax(self.time)
        dt = relativedelta(months=1)

        if maxTime.microsecond==0: maxTime+=relativedelta(months=1)

        dummy = []
        tummy = []
        count = []
        while minTime<=maxTime:
            mask = np.where(self.time>=minTime and self.time<maxTime)[0]
            dummy.append(np.nanmean(self.data[mask],axis=0))
            tummy.append(self.time[mask[0]])
            count.append(np.sum(np.isfinite(self.data[mask])))
        self.data = np.array(dummy)
        self.time = np.array(tummy)
        self.counts = np.array(count)
    
    def year(self):
        minTime = np.nanmin(self.time)
        maxTime = np.nanmax(self.time)
        dt = relativedelta(years=1)

        if maxTime.microsecond==0: maxTime+=relativedelta(years=1)

        dummy = []
        tummy = []
        count = []
        while minTime<=maxTime:
            mask = np.where(self.time>=minTime and self.time<maxTime)[0]
            dummy.append(np.nanmean(self.data[mask],axis=0))
            tummy.append(self.time[mask[0]])
            count.append(np.sum(np.isfinite(self.data[mask])))
        self.data = np.array(dummy)
        self.time = np.array(tummy)
        self.counts = np.array(count)
    
    def get(self,parameter=None):
        if parameter==None: return dict(time=self.time, data=self.data, counts=self.counts)
        if parameter=='time' return self.time
        if parameter=='data' return self.data
        if parameter=='counts' return self.counts