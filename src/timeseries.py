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
from typing import Union

class Time(object):
    '''
    storageForward: True -> storage value in starttime <br>
    storageForward: False -> storage value in endtime
    '''

    def __init__(self):
        self.set_config(init=True)

    def _check_data(self):
        if not "self.time" in locals(): raise "Please check input time."
        if not "self.data" in locals(): raise "Please check input data."
        return True
    
    @staticmethod
    def _set_ndarray(data):
        if isinstance(data,dict):
            for key in data.keys():
                data[key]=np.array(data[key])
        else:
            data=np.array(data)
        return data

    @staticmethod
    def _set_header(data,header=None):
        '''
        only used to format output data
        '''
        # ----------------------------------------------------------- #
        # here i'm not sure what data type i need to use.
        # thus, if data=np.array(obj(dict)), then we need 
        # to use data.item() to get the data
        try:
            data=data.item()
        except:
            pass
        # ----------------------------------------------------------- #

        if header!=None:
            dummy={}
            for i,head in enumerate(header):
                if isinstance(data,dict):
                    for key in data.keys():
                        if i==0: dummy[key]={}
                        dummy[key][head]=data[key][:,i]
                else:
                    dummy[head]=data[:,i] 
            return dummy
        return data

    @staticmethod
    def _fixTime(time,data,timeStep:dict,zeroPara:dict,storageForward:bool,outputPara_list:list,
        starttime:datetime.datetime=None,endtime:datetime.datetime=None):
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

        # get data_value
        if isinstance(data,dict): 
            if 'mean' in data.keys(): data=data['mean']

        if 'season' in timeStep.keys():
            dt = relativedelta(months=3)
            if not storageForward: time+=dt; time+=datetime.timedelta(microseconds=-1)
            maxTime+=dt
            if zeroPara!=None: minTime=minTime.replace(**zeroPara)
            dummy={}
            for para in outputPara_list:
                if para=='quartile':
                    dummy['lower']=[]
                    dummy['median']=[]
                    dummy['upper']=[]
                else:
                    dummy[para]=[]
            tummy = []
            count = []

            # deal with perfix date before a new start
            i = Time._get_season(minTime.month)
            year = minTime.year if minTime.month!=12 else minTime.year+1
            mask=np.where(time<datetime.datetime(year,3*i,1))[0]
            t,d,c = Time._nofixTime(time[mask],data[mask],parameter='season',outputPara_list=outputPara_list)
            tummy+=list(t); count+=list(c)
            for key in dummy.keys(): dummy[key]+=list(d[key])
            minTime=datetime.datetime(year,3*i,1)

            while minTime<=maxTime:
                if minTime>max(time): break
                mask=np.where((time>=minTime) & (time<minTime+dt))[0]
                t,d,c = Time._nofixTime(time[mask],data[mask],parameter='season',outputPara_list=outputPara_list)
                tummy+=list(t); count+=list(c)
                for key in dummy.keys(): dummy[key]+=list(d[key])
                minTime+=dt
        else:
            dt = relativedelta(**timeStep)
            if not storageForward: time+=dt; time+=datetime.timedelta(microseconds=-1)
            maxTime+=dt
            if zeroPara!=None: minTime=minTime.replace(**zeroPara)
            # if ratio==None: ratio=0

            dummy = {}
            for para in outputPara_list:
                if para=='quartile':
                    dummy['lower']=[]
                    dummy['median']=[]
                    dummy['upper']=[]
                else:
                    dummy[para]=[]
            tummy = []
            count = []
            while minTime<=maxTime:
                mask = np.where((time>=minTime) & (time<minTime+dt))[0]
                if mask.size==0: minTime+=dt; continue
                tummy.append(minTime)
                count.append(np.sum(np.isfinite(data[mask])))
                if 'mean' in outputPara_list: dummy['mean'].append(np.nanmean(data[mask],axis=0))
                if 'std' in outputPara_list: dummy['std'].append(np.nanstd(data[mask],axis=0))
                if 'max' in outputPara_list: dummy['max'].append(np.nanmax(data[mask],axis=0))
                if 'min' in outputPara_list: dummy['min'].append(np.nanmin(data[mask],axis=0))
                if 'maxTime' in outputPara_list: dummy['maxTime'].append(time[mask][np.argmax(data[mask],axis=0)])
                if 'maxTime' in outputPara_list: dummy['minTime'].append(time[mask][np.argmin(data[mask],axis=0)])
                if 'quartile' in outputPara_list: dummy['lower'].append(np.nanpercentile(data[mask],25,axis=0))
                if ('quartile' in outputPara_list) | ('median' in outputPara_list): 
                    dummy['median'].append(np.nanpercentile(data[mask],50,axis=0))
                if 'quartile' in outputPara_list: dummy['upper'].append(np.nanpercentile(data[mask],75,axis=0))
                # dummy.append(np.nanmean(data[mask],axis=0) if count[-1]>=ratio else np.array([np.nan]*len(data[0])))
                minTime+=dt
        dummy = Time._set_ndarray(dummy)
        return tummy,dummy,count

    @staticmethod
    def _nofixTime(time,data,parameter:str,outputPara_list:list):
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
            time_para_list = [Time._get_season(val.month) for val in time]
        else:
            time_para_list = [eval(f"val.{parameter}") for val in time]
        time_para_list = np.array(time_para_list)
        if time_para_list.size==0: return np.array(np.nan),np.array(np.nan),np.array(np.nan)
        minTime = np.nanmin(time_para_list)
        maxTime = np.nanmax(time_para_list)
        # if ratio==None: ratio=0

        # get data_value
        if isinstance(data,dict): 
            if 'mean' in data.keys(): data=data['mean']

        dummy = {}
        for para in outputPara_list:
            if para=='quartile':
                dummy['lower']=[]
                dummy['median']=[]
                dummy['upper']=[]
            else:
                dummy[para]=[]
        tummy = []
        count = []
        for i in range(minTime,maxTime+1):
            mask = np.where(time_para_list==i)[0]
            tummy.append(i if parameter.lower()!='season' else [time[mask[0]].year,season_dict[i]])
            count.append(np.sum(np.isfinite(data[mask])))
            if 'mean' in outputPara_list: dummy['mean'].append(np.nanmean(data[mask],axis=0))
            if 'std' in outputPara_list: dummy['std'].append(np.nanstd(data[mask],axis=0))
            if 'max' in outputPara_list: dummy['max'].append(np.nanmax(data[mask],axis=0))
            if 'min' in outputPara_list: dummy['min'].append(np.nanmin(data[mask],axis=0))
            if 'maxTime' in outputPara_list: dummy['maxTime'].append(time[mask][np.argmax(data[mask],axis=0)])
            if 'maxTime' in outputPara_list: dummy['minTime'].append(time[mask][np.argmin(data[mask],axis=0)])
            if 'quartile' in outputPara_list: dummy['lower'].append(np.nanpercentile(data[mask],25,axis=0))
            if ('quartile' in outputPara_list) | ('median' in outputPara_list): 
                dummy['median'].append(np.nanpercentile(data[mask],50,axis=0))
            if 'quartile' in outputPara_list: dummy['upper'].append(np.nanpercentile(data[mask],75,axis=0))
            # dummy.append(np.nanmean(data[mask],axis=0) if count[-1]>=ratio else np.array([np.nan]*len(data[0])))
        dummy = Time._set_ndarray(dummy)
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

    def set_config(self,init:bool=False,**kwargs) -> None:
        '''
        config['storageForward']: save the value at the start time or not<br>
        config['outputPara_list]: select output parameter [mean,std,max,min]

        Arguments:
            init: Is the initialize status? Default is False
                If set True, will using the init state.
            **kwargs:
                Optional, this work only init set false. 

                    config: {
                        asDict: bool,
                        storage: bool,
                        fixTime: bool,
                        zeroStart: bool,
                        selfUpdate: bool,
                        outputPara_list: list = [
                            mean,
                            std,
                            max,
                            min,
                            maxTime,
                            minTime,
                            quartile,
                            median
                        ]
                    }
        '''
        if init==True:
            self.config = dict(
                asDict=False,
                storageForward=True,
                fixTime=True,
                zeroStart=True,
                selfUpdate=True,
                outputPara_list=['mean','std','mean'] # ['mean','std','max','min','maxTime','minTime','quartile','median'],
            )
        else:
            for key in kwargs.keys():
                self.config[key] = kwargs[key]

    def input(self,time: Union[list, np.ndarray],data: Union[list, np.ndarray],dtype:object =float,
        ratio: Union[int, float]=None,header: list=None,starttime:datetime.datetime=None,endtime:datetime.datetime=None) -> str:
        '''
        time <datetime> : input timelist of data <br>
        data <numerical>: input data array

        Arguments:
            time: list of time series
            data: list of data set depend on time series
            dtype: convert type of data elements
            ratio: require of the data numbers(int) or ratio(float)
            header: export tag of data header
            starttime: start of the time
            endtime: end of the time

        Returns:
            return 'Successfully' when process success.
        '''
        self.time = np.array(time)
        self.data = np.array(data,dtype=dtype)
        self.ratio = ratio
        self.header = header
        self.starttime = starttime
        self.endtime = endtime
        self.counts = []
        return "Successfully"

    def isrepeat(self) -> bool:
        '''
        Check weather data repeat depend on time.
        Returns:
            check there has repeat datetime in the data set.
        '''
        if len(self.time.reshape(-1))==len(set(self.time)):
            return False
        else:
            return True

    def second(self,ratio: Union[int, float]=None,base: int=1000) -> Union[None, tuple, list, dict]:
        '''
        Do statistic method base on config setting.

        Arguments:
            ratio: require of the data numbers(int) or ratio(float)
            base: base number of required data, use on ratio<=1

        Returns:
            structure of return data
            
                None: if config.selfUpdate==True, then export data by self.get()
                tuple or list: if config.selfUpdate==False & config.asDict==False, then return the data as tuple.
                    ( time, data, count )
                dict: if config.selfUpdate==False & config.asDict==True, then return the data as dictionary.
                    {
                        time: np.ndarray,
                        data: np.ndarray,
                        count: np.ndarray
                    }
        '''
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(seconds=1),
                    zeroPara=dict(microsecond=0),storageForward=self.config['storageForward'],
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(seconds=1),
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='second',outputPara_list=self.config['outputPara_list'])

        dummy = self._QC_numbers(dummy,count,ratio)

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = Time._set_header(dummy,header=self.header)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def minute(self,ratio: Union[int, float]=None,base: int=60) -> Union[None, tuple, list, dict]:
        '''
        Do statistic method base on config setting.

        Arguments:
            ratio: require of the data numbers(int) or ratio(float)
            base: base number of required data, use on ratio<=1

        Returns:
            structure of return data
            
                None: if config.selfUpdate==True, then export data by self.get()
                tuple or list: if config.selfUpdate==False & config.asDict==False, then return the data as tuple.
                    ( time, data, count )
                dict: if config.selfUpdate==False & config.asDict==True, then return the data as dictionary.
                    {
                        time: np.ndarray,
                        data: np.ndarray,
                        count: np.ndarray
                    }
        '''
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(minutes=1),
                    zeroPara=dict(second=0,microsecond=0),storageForward=self.config['storageForward'],
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(minutes=1),
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='minute',outputPara_list=self.config['outputPara_list'])

        dummy = self._QC_numbers(dummy,count,ratio)

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = Time._set_header(dummy,header=self.header)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count

    def hour(self,ratio: Union[int, float]=None,base: int=60) -> Union[None, tuple, list, dict]:
        '''
        Do statistic method base on config setting.

        Arguments:
            ratio: require of the data numbers(int) or ratio(float)
            base: base number of required data, use on ratio<=1

        Returns:
            structure of return data
            
                None: if config.selfUpdate==True, then export data by self.get()
                tuple or list: if config.selfUpdate==False & config.asDict==False, then return the data as tuple.
                    ( time, data, count )
                dict: if config.selfUpdate==False & config.asDict==True, then return the data as dictionary.
                    {
                        time: np.ndarray,
                        data: np.ndarray,
                        count: np.ndarray
                    }
        '''
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(hours=1)
                    ,zeroPara=dict(minute=0,second=0,microsecond=0),storageForward=self.config['storageForward'],
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(hours=1),
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='hour',outputPara_list=self.config['outputPara_list'])

        dummy = self._QC_numbers(dummy,count,ratio)

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = Time._set_header(dummy,header=self.header)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def day(self,ratio: Union[int, float]=None,base: int=24) -> Union[None, tuple, list, dict]:
        '''
        Do statistic method base on config setting.

        Arguments:
            ratio: require of the data numbers(int) or ratio(float)
            base: base number of required data, use on ratio<=1

        Returns:
            structure of return data
            
                None: if config.selfUpdate==True, then export data by self.get()
                tuple or list: if config.selfUpdate==False & config.asDict==False, then return the data as tuple.
                    ( time, data, count )
                dict: if config.selfUpdate==False & config.asDict==True, then return the data as dictionary.
                    {
                        time: np.ndarray,
                        data: np.ndarray,
                        count: np.ndarray
                    }
        '''
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(days=1),
                    zeroPara=dict(hour=0,minute=0,second=0,microsecond=0),storageForward=self.config['storageForward'],
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(days=1),
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='day',outputPara_list=self.config['outputPara_list'])

        dummy = self._QC_numbers(dummy,count,ratio)

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = Time._set_header(dummy,header=self.header)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def month(self,ratio: Union[int, float]=None,base: int=30) -> Union[None, tuple, list, dict]:
        '''
        Do statistic method base on config setting.

        Arguments:
            ratio: require of the data numbers(int) or ratio(float)
            base: base number of required data, use on ratio<=1

        Returns:
            structure of return data
            
                None: if config.selfUpdate==True, then export data by self.get()
                tuple or list: if config.selfUpdate==False & config.asDict==False, then return the data as tuple.
                    ( time, data, count )
                dict: if config.selfUpdate==False & config.asDict==True, then return the data as dictionary.
                    {
                        time: np.ndarray,
                        data: np.ndarray,
                        count: np.ndarray
                    }
        '''
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(months=1),
                    zeroPara=dict(day=1,hour=0,minute=0,second=0,microsecond=0),
                    outputPara_list=self.config['outputPara_list'],storageForward=self.config['storageForward'], starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(months=1),
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='month',outputPara_list=self.config['outputPara_list'])

        dummy = self._QC_numbers(dummy,count,ratio)

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = Time._set_header(dummy,header=self.header)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def season(self,ratio: Union[int, float]=None,base: int=3) -> Union[None, tuple, list, dict]:
        '''
        Do statistic method base on config setting.

        Arguments:
            ratio: require of the data numbers(int) or ratio(float)
            base: base number of required data, use on ratio<=1

        Returns:
            structure of return data
            
                None: if config.selfUpdate==True, then export data by self.get()
                tuple or list: if config.selfUpdate==False & config.asDict==False, then return the data as tuple.
                    ( time, data, count )
                dict: if config.selfUpdate==False & config.asDict==True, then return the data as dictionary.
                    {
                        time: np.ndarray,
                        data: np.ndarray,
                        count: np.ndarray
                    }
        '''
        '''
        Spring: March, April, May <br>
        Summer: June, July, August <br>
        Autumn: September, October, November <br>
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
                    outputPara_list=self.config['outputPara_list'],storageForward=self.config['storageForward'], starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(season=1),
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='season',outputPara_list=self.config['outputPara_list'])

        dummy = self._QC_numbers(dummy,count,ratio)

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = Time._set_header(dummy,header=self.header)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count

    def year(self,ratio:Union[int, float]=None,base:int=12) -> Union[None, tuple, list, dict]:
        '''
        Do statistic method base on config setting.

        Arguments:
            ratio: require of the data numbers(int) or ratio(float)
            base: base number of required data, use on ratio<=1
        
        Returns:
            structure of return data
            
                None: if config.selfUpdate==True, then export data by self.get()
                tuple or list: if config.selfUpdate==False & config.asDict==False, then return the data as tuple.
                    ( time, data, count )
                dict: if config.selfUpdate==False & config.asDict==True, then return the data as dictionary.
                    {
                        time: np.ndarray,
                        data: np.ndarray,
                        count: np.ndarray
                    }
        '''
        if ratio!=None:
            ratio=int(base*ratio) if ratio<=1 else int(ratio)
        else:
            if self.ratio!=None:
                ratio=int(base*self.ratio) if self.ratio<=1 else int(self.ratio)

        if self.config['fixTime']:
            if self.config['zeroStart']:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(years=1),
                    zeroPara=dict(month=1,day=1,hour=0,minute=0,second=0,microsecond=0),storageForward=self.config['storageForward'],
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
            else:
                tummy,dummy,count = self._fixTime(self.time,self.data,timeStep=dict(years=1),
                    outputPara_list=self.config['outputPara_list'],starttime=self.starttime,endtime=self.endtime)
        else: # self.config['fixTime']==False
            tummy,dummy,count = self._nofixTime(self.time,self.data,parameter='year',outputPara_list=self.config['outputPara_list'])

        dummy = self._QC_numbers(dummy,count,ratio)

        if self.config['selfUpdate']:
            self.data = np.array(dummy)
            self.time = np.array(tummy)
            self.counts = np.array(count)
        else:
            print("This is not object standard operation!")
            print("You need to set config[selfUpdate]=True and use get method to get the result.")
            dummy = Time._set_header(dummy,header=self.header)
            if self.config['asDict']:
                return dict(time=tummy,data=dummy,counts=count)
            else:
                return tummy,dummy,count
    
    def get(self,parameter: str=None) -> Union[list, dict, np.ndarray]:
        '''
        export the data from Time factory.

        Arguments:
            parameter: select the return parameter. 

                enum:
                    None: {
                        time,
                        data,
                        counts
                    },
                    config,
                    time,
                    data,
                    counts
        Returns:
            select parameter data set.
        '''
        if parameter=='config': return self.config
        if (parameter==None) and (self.config['asDict']): return dict(time=self.time, data=Time._set_header(self.data,header=self.header), counts=self.counts)
        if parameter=='time': return self.time
        if parameter=='data': return Time._set_header(self.data,header=self.header)
        if parameter=='counts': return self.counts
        print("Please select the return parameter or set config['asDict']=True.")

if __name__ == "__main__":
    # Implement the object
    myobj = Time()

    # Input data
    import datetime, random
    st = datetime.datetime(2020,1,1)
    number = 50000
    time = [st+datetime.timedelta(hours=val) for val in range(number)]
    data = [[random.gauss(10,5) for _ in range(4)] for _ in range(number)]
    myobj.input(time,data,header=['a','b','c','d'])

    # Calculate and Get result
    # myobj.hour(1,500)
    myobj.set_config(outputPara_list=['mean','std','max','quartile'])
    myobj.season()
    myobj.set_config(asDict=True)
    result = myobj.get()
    print(result)