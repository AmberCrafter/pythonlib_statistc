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
    elif os.name=='posix':
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
    elif os.name=='posix':
        subprocess.check_call([sys.executable, "-m", "pip3", "install", "numpy"])
    else:
        raise "Unknow platform, please install 'numpy' by yourself."
    import numpy as np
# =================================================================== #
import datetime

class Timean(object):
    '''
    storageForward: True ->
        storage value in starttime
    storageForward: False ->
        storage value in endtime
    '''
    def __init__(self):
        self.set_config(init=True)

    def _check_data(self):
        if not "self.time" in locals(): raise "Please check input time."
        if not "self.data" in locals(): raise "Please check input data."
        return True
    
    def _set_header(self,data):
        '''
        only used to format output data
        '''
        if self.header!=None:
            dummy={}
            for i,key in enumerate(self.header):
               dummy[key]=data[:,i] 
            return dummy
        return data

    @staticmethod
    def _fixTime(time,data,timeStep:dict,zeroPara:dict,storageForward:bool):
        '''
        zeroPara: set start datetime para
        '''
        dt = relativedelta(**timeStep)
        if not storageForward: time+=dt; time+=datetime.timedelta(microseconds=-1)
        minTime = np.nanmin(time)
        maxTime = np.nanmax(time)
        maxTime+=dt
        if zeroPara!=None: minTime=minTime.replace(**zeroPara)

        dummy = []
        tummy = []
        count = []
        while minTime<=maxTime:
            mask = np.where((time>=minTime) & (time<minTime+dt))[0]
            if mask.size==0: minTime+=dt; continue
            dummy.append(np.nanmean(data[mask],axis=0))
            tummy.append(minTime)
            count.append(np.sum(np.isfinite(data[mask])))
            minTime+=dt
        return tummy,dummy,count

    @staticmethod
    def _nofixTime(time,data,parameter:str):
        '''
        parameter: set the datetime parameter (second, minute ...etc) will be used to calculate
        '''
        time_para_list = [eval(f"val.{parameter}") for val in time]
        minTime = np.nanmin(time_para_list)
        maxTime = np.nanmax(time_para_list)

        dummy = []
        tummy = []
        count = []
        for i in range(minTime,maxTime+1):
            mask = np.where(eval(f"time.{parameter}")==i)[0]
            tummy.append(i)
            dummy.append(np.nanmean(data[mask],axis=0))
            count.append(np.sum(np.isfinite(data[mask])))
        return tummy,dummy,count

    def set_config(self,init:bool=False,**kwargs):
        '''
        config['storageForward']: save the value at the start time
        '''
        if init==True:
            self.config = dict(
                asDict=False,
                storageForward=True,
                fixTime=True,
                zeroStart=True,
                selfUpdate=True
            )
        else:
            for key in kwargs.keys():
                self.config[key] = kwargs[key]

    def input(self,time,data,dtype=float,header=None):
        '''
        time <datetime> : input timelist of data
        data <numerical>: input data array
        '''
        self.time = np.array(time)
        self.data = np.array(data,dtype=dtype)
        self.counts = []
        self.header = header
        return "Successfully"

    def isrepeat(self):
        '''
        Check weather data repeat depend on time.
        '''
        if len(self.time.reshape(-1))==len(set(self.time)):
            return False
        else:
            return True

    def second(self):
        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(seconds=1),zeroPara=dict(microsecond=0)
                    ,storageForward=self.config['storageForward'])
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(seconds=1))
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='second')

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = self._set_header(dummy)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def minute(self):
        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(minutes=1),zeroPara=dict(second=0,microsecond=0)
                    ,storageForward=self.config['storageForward'])
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(minutes=1))
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='minute')

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = self._set_header(dummy)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count

    def hour(self):
        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(hours=1),zeroPara=dict(minute=0,second=0,microsecond=0)
                    ,storageForward=self.config['storageForward'])
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(hours=1))
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='hour')

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = self._set_header(dummy)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def day(self):
        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(days=1),zeroPara=dict(hour=0,minute=0,second=0,microsecond=0)
                    ,storageForward=self.config['storageForward'])
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(days=1))
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='day')

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = self._set_header(dummy)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def month(self):
        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(months=1),
                    zeroPara=dict(day=1,hour=0,minute=0,second=0,microsecond=0)
                    ,storageForward=self.config['storageForward'])
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(months=1))
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='month')

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = self._set_header(dummy)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def year(self):
        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(years=1),
                    zeroPara=dict(month=1,day=1,hour=0,minute=0,second=0,microsecond=0)
                    ,storageForward=self.config['storageForward'])
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(years=1))
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='year')

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = self._set_header(dummy)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def get(self,parameter=None):
        if parameter=='config': return self.config
        if (parameter==None) and (self.config['asDict']): return dict(time=self.time, data=self._set_header(self.data), counts=self.counts)
        if parameter=='time': return self.time
        if parameter=='data': return self._set_header(self.data)
        if parameter=='counts': return self.counts
        print("Please select the return parameter or set config['asDict']=True.")

if __name__ == "__main__":
    # Implement the object
    myobj = Timean()

    # Input data
    import datetime, random
    st = datetime.datetime(2020,1,1)
    number = 1000
    time = [st+datetime.timedelta(minutes=val) for val in range(number)]
    data = [[random.gauss(10,5) for _ in range(4)] for _ in range(number)]
    myobj.input(time,data,header=['a','b','c','d'])

    # Calculate and Get result
    myobj.hour()
    myobj.set_config(asDict=True)
    result = myobj.get()
    print(result)