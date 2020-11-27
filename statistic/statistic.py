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
    def _fixTime(time,data,timeStep:dict,zeroPara:dict,storageForward:bool,starttime:datetime.datetime=None,endtime:datetime.datetime=None):
    # def _fixTime(time,data,timeStep:dict,ratio:int,zeroPara:dict,storageForward:bool,starttime:datetime.datetime=None,endtime:datetime.datetime=None):
        '''
        zeroPara: set start datetime para
        season enum:
            1: spring
            2: summer
            3: autumn
            4: winter
        '''
        minTime = np.nanmin(time) if starttime==None else starttime
        maxTime = np.nanmax(time) if endtime==None else endtime
        if 'season' in timeStep.keys():
            dt = relativedelta(months=3)
            if not storageForward: time+=dt; time+=datetime.timedelta(microseconds=-1)
            maxTime+=dt
            if zeroPara!=None: minTime=minTime.replace(**zeroPara)
            dummy = []
            tummy = []
            count = []

            # deal with perfix date before a new start
            i = Timean._get_season(minTime.month)
            year = minTime.year if minTime.month!=12 else minTime.year+1
            mask=np.where(time<datetime.datetime(year,3*i,1))[0]
            t,d,c = Timean._nofixTime(time[mask],data[mask],parameter='season')
            tummy+=list(t); dummy+=(d); count+=list(c)
            minTime=datetime.datetime(year,3*i,1)

            while minTime<=maxTime:
                if minTime>max(time): break
                mask=np.where((time>=minTime) & (time<minTime+dt))[0]
                t,d,c = Timean._nofixTime(time[mask],data[mask],parameter='season')
                tummy+=list(t); dummy+=(d); count+=list(c)
                minTime+=dt
        else:
            dt = relativedelta(**timeStep)
            if not storageForward: time+=dt; time+=datetime.timedelta(microseconds=-1)
            maxTime+=dt
            if zeroPara!=None: minTime=minTime.replace(**zeroPara)
            # if ratio==None: ratio=0

            dummy = []
            tummy = []
            count = []
            while minTime<=maxTime:
                mask = np.where((time>=minTime) & (time<minTime+dt))[0]
                if mask.size==0: minTime+=dt; continue
                tummy.append(minTime)
                count.append(np.sum(np.isfinite(data[mask])))
                dummy.append(np.nanmean(data[mask],axis=0))
                # dummy.append(np.nanmean(data[mask],axis=0) if count[-1]>=ratio else np.array([np.nan]*len(data[0])))
                minTime+=dt
        return tummy,dummy,count

    @staticmethod
    def _nofixTime(time,data,parameter:str):
    # def _nofixTime(time,data,parameter:str,ratio:int):
        '''
        parameter: set the datetime parameter (second, minute ...etc) will be used to calculate
        season enum:
            1: winter
            2: spring
            3: summer
            4: autumn
        '''
        season_dict = {
            1: 'Winter',
            2: 'Spring',
            3: 'Summer',
            4: 'Autumn',
        }
        if parameter.lower()=='season':
            time_para_list = [Timean._get_season(val.month) for val in time]
        else:
            time_para_list = [eval(f"val.{parameter}") for val in time]
        time_para_list = np.array(time_para_list)
        if time_para_list.size==0: return np.array(np.nan),np.array(np.nan),np.array(np.nan)
        minTime = np.nanmin(time_para_list)
        maxTime = np.nanmax(time_para_list)
        # if ratio==None: ratio=0

        dummy = []
        tummy = []
        count = []
        for i in range(minTime,maxTime+1):
            mask = np.where(time_para_list==i)[0]
            tummy.append(i if parameter.lower()!='season' else [time[mask[0]].year,season_dict[i]])
            count.append(np.sum(np.isfinite(data[mask])))
            dummy.append(np.nanmean(data[mask],axis=0))
            # dummy.append(np.nanmean(data[mask],axis=0) if count[-1]>=ratio else np.array([np.nan]*len(data[0])))
        return tummy,dummy,count
    
    @staticmethod
    def _get_season(month):
        '''
        enum:
            1: winter
            2: spring
            3: summer
            4: autumn
        '''
        return (month%12+3)//3

    @staticmethod
    def _QC_numbers(data,count,threshold):
        if threshold==None: return data
        count = np.array(count)
        data = np.array(data)
        mask = np.where(count<threshold)[0]
        data[mask,:]=np.nan
        return data

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

    def input(self,time,data,dtype=float,ratio=None,header=None,starttime:datetime.datetime=None,endtime:datetime.datetime=None):
        '''
        time <datetime> : input timelist of data
        data <numerical>: input data array
        '''
        self.time = np.array(time)
        self.data = np.array(data,dtype=dtype)
        self.ratio = ratio
        self.header = header
        self.starttime = starttime
        self.endtime = endtime
        self.counts = []
        return "Successfully"

    def isrepeat(self):
        '''
        Check weather data repeat depend on time.
        '''
        if len(self.time.reshape(-1))==len(set(self.time)):
            return False
        else:
            return True

    def second(self,ratio=None,base=1000):
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(seconds=1),
                    zeroPara=dict(microsecond=0),storageForward=self.config['storageForward'],
                    starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(seconds=1),
                    starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='second')

        dummy = self._QC_numbers(dummy,count,ratio)

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
    
    def minute(self,ratio=None,base=60):
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(minutes=1),
                    zeroPara=dict(second=0,microsecond=0),storageForward=self.config['storageForward'],
                    starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(minutes=1),
                starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='minute')

        dummy = self._QC_numbers(dummy,count,ratio)

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

    def hour(self,ratio=None,base=60):
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(hours=1)
                    ,zeroPara=dict(minute=0,second=0,microsecond=0),storageForward=self.config['storageForward'],
                    starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(hours=1),
                starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='hour')

        dummy = self._QC_numbers(dummy,count,ratio)

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
    
    def day(self,ratio=None,base=24):
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(days=1),
                    zeroPara=dict(hour=0,minute=0,second=0,microsecond=0),storageForward=self.config['storageForward'],
                    starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(days=1),
                    starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='day')

        dummy = self._QC_numbers(dummy,count,ratio)

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
    
    def month(self,ratio=None,base=30):
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(months=1),
                    zeroPara=dict(day=1,hour=0,minute=0,second=0,microsecond=0),
                    storageForward=self.config['storageForward'], starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(months=1),
                    starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='month')

        dummy = self._QC_numbers(dummy,count,ratio)

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
    
    def season(self,ratio=None,base=3):
        '''
        Spring: March, April, May
        Summer: June, July, August
        Autumn: September, October, November 
        Winter: December, January, February
        '''
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(season=1),
                    zeroPara=dict(day=1,hour=0,minute=0,second=0,microsecond=0),
                    storageForward=self.config['storageForward'], starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(season=1),
                    starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='season')

        dummy = self._QC_numbers(dummy,count,ratio)

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

    def year(self,ratio=None,base=12):
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(years=1),
                    zeroPara=dict(month=1,day=1,hour=0,minute=0,second=0,microsecond=0),storageForward=self.config['storageForward'],
                    starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(years=1),
                    starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='year')

        dummy = self._QC_numbers(dummy,count,ratio)

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
    number = 50000
    time = [st+datetime.timedelta(hours=val) for val in range(number)]
    data = [[random.gauss(10,5) for _ in range(4)] for _ in range(number)]
    myobj.input(time,data,header=['a','b','c','d'])

    # Calculate and Get result
    # myobj.hour(1,500)
    myobj.season()
    myobj.set_config(asDict=True)
    result = myobj.get()
    print(result)