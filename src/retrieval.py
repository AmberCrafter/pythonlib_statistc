#!/bin/python3
# if used ubuntu 20.10 or later, interpreter set as #!/bin/python and use pip instead of pip3

# # =================================================================== #
# # platfrom check
# # dateutil check and import
# try:
#     from scipy.linalg import fractional_matrix_power
# except:
#     import os,sys,subprocess
#     if os.name=='nt':
#         subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])
#     elif os.name=='posix':
#         subprocess.check_call([sys.executable, "-m", "pip3", "install", "scipy"])
#     else:
#         raise "Unknow platform, please install 'scipy' by yourself."
#     from scipy.linalg import fractional_matrix_power
# # =================================================================== #
# # platfrom check
# # numpy check and import
# try:
#     import numpy as np
# except:
#     import os,sys,subprocess
#     if os.name=='nt':
#         subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
#     elif os.name=='posix':
#         subprocess.check_call([sys.executable, "-m", "pip3", "install", "numpy"])
#     else:
#         raise "Unknow platform, please install 'numpy' by yourself."
#     import numpy as np
# # =================================================================== #
from typing import List, Union
import numpy as np
from scipy.linalg import fractional_matrix_power
import unittest

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class var1d(AttrDict):
    '''
    1D var method base on Hewison (2007)(http://tim.hewison.org/IEEE_1D-VAR.pdf)      <br>
    '''
    # '''
    # 1D var method base on Hewison (2007)                                            <br>
    # # input:                                                                        <br>
    # B : background error                                                            <br>
    # R : observation error                                                           <br>
    # gamma : Levenberg Marquardt parameter                                           <br>
    # func_forward : Forward function                                                 <br>
    # x_background : x background value.                                              <br>
    # y_obs : y observation value.                                                    <br>
    # x_step : used to cal. jacobian matrix (H)                                       <br>

    # min_runtime : limit of minimun iteration times to trigger return function       <br>
    # max_runtime : limit of maximun iteration times to trigger return function       <br>
    # min_reject_runtime : minimun iteration times of reject this loop                <br>
    # min_X2 : threshold of cost funciton(X2)                                         <br>

    # # optional:                                                                     <br>
    # x_init (option) : x initialization. if None, set as x_background                <br>
    # weighting : multiplier of the dx, default is 1 --> x1 = x0 + weighting*dx       <br>
    # func_plugin : custom plugin function. please define funtion as                  <br>

    # ```
    #     def your_plugin(retri_obj):
    #         ...
    # ```

    # # output:                                                                       <br>
    # y_retri : y retrieval value.                                                    <br>
    # #------------------------------------------------------------                   <br>
    # # Old parameter: (abandoned)                                                    <br>
    # func_jacobian : Jacobian function                                               <br>
    # #------------------------------------------------------------                   <br>
    # ref: http://tim.hewison.org/IEEE_1D-VAR.pdf                                     <br>
    # '''
    @staticmethod
    def get_require_input_parameter():
        return dict(
            B = None,
            R = None,
            gamma = None,
            func_forward = None,
            x_background = None,
            y_obs = None,
            x_step = None,
            min_runtime = None,
            max_runtime = None,
            min_reject_runtime = None,
            min_X2 = None,
            x_init = None,
            weighting = 1,
        )

    def __init__(self, *args,**kwargs) -> None:
        '''
        Initialize the iD var object.

        Parameters:
            B : backgorund error matrix
            R : observation error matrix
            gamma : Levenberg Marquardt parameter
            func_forward : forward function
            x_background : x background value
            y_obs : y observation value
            x_step : delta x, used to calculate Jacobian matrix (H)
            
            min_runtime : limit of minimun iteration times to trigger return function
            max_runtime : limit of maximun iteration times to trigger return function
            min_reject_runtime : minimun iteration times of reject this loop         
            min_X2 : threshold of cost funciton(X2)                                  

            x_init : [optional] x initialization. if None, set as x_background          
            weighting : [optional] multiplier of the dx, default is 1 --> x1 = x0 + weighting*dx 
            func_plugin : [optional] custom plugin function. please define funtion as

                def your_plugin(retri_obj):
                    ...     
        '''


        super(var1d,self).__init__(*args,**kwargs)
        self.x_background = np.array(self.x_background)
        self.y_obs = np.array(self.y_obs)

        if not hasattr(self,'x_init'): self.x_init = self.x_background.copy()
        if not hasattr(self,'weighting'): self.weighting = 1
        self.count = 0

        class Record:
            X2 = []
            x = []
            y = []
            X2_XX = []
            X2_YY = []

        self.record = Record()

    def _cal_jacobian(self):
        '''
        This function used to calculate the jacobian matrix
        '''
        xl = []
        xr = []
        for i in range(len(self.x)):
            dxl = self.x.copy()
            dxr = self.x.copy()
            dxl[i] = dxl[i]-self.x_step[i]
            dxr[i] = dxr[i]+self.x_step[i]
            xl.append(self.func_forward(dxl))
            xr.append(self.func_forward(dxr))
        xl = np.transpose(xl)
        xr = np.transpose(xr)
        self.H = (xr-xl)/(np.ones_like(xr)*self.x_step*2)

    def _preprocess(self):
        '''
        1. calculate [background, observation] error inversion
            B -> Bi
            R -> Ri
        2. calculate jacobian matrix H
        3. calculate y_retri depend on the i-th iteration x
        '''
        # self.R = np.eye(10)*0.01
        self.Bi = np.linalg.inv(self._B)
        self.Ri = np.linalg.inv(self.R)
        self._cal_jacobian()
        self.HT = self.H.T
        if self.count == 0: self.y_retri = self.func_forward(self.x)
        
    def _cal_dx(self):
        # 1d method
        total_error_cov = np.linalg.inv((1+self.gamma)*self.Bi + np.dot(np.dot(self.HT,self.Ri),self.H))
        retri_diff = np.dot(np.dot(self.HT,self.Ri),(self.y_obs-self.y_retri)) - np.dot(self.Bi,(self.x-self.x_background))
        self.dx = np.dot(total_error_cov,retri_diff)

    def _cal_X2(self):
        self.y_retri_pre = self.y_retri.copy()
        self.y_retri = self.func_forward(self.x)
        if hasattr(self, 'X2'): self.X2_pre = self.X2.copy()
        # self.X2 = np.nansum(np.abs(self.y_retri-self.y_obs))
        YY = fractional_matrix_power(self.R,-0.5)
        YY = np.linalg.norm(np.dot(YY,self.y_obs-self.y_retri))
        YY = YY**2
        XX = fractional_matrix_power(self._B,-0.5)
        XX = np.linalg.norm(np.dot(XX,self.x_background-self.x))
        XX = XX**2
        self.record.X2_XX.append(XX)
        self.record.X2_YY.append(YY)
        self.X2 = XX+YY

        if hasattr(self, 'X2_best'):
            if self.X2<self.X2_best:
                self.x_best = self.x.copy()
                self.X2_best = self.X2.copy()
                self.count_best = self.count
        else:
            self.x_best = self.x.copy()
            self.X2_best = self.X2.copy()
            self.count_best = self.count
        if hasattr(self, 'X2_pre'): 
            self.weighting = 1 if abs(self.X2-self.X2_pre)<100 else self.weighting
            if self.X2/self.X2_pre<1: 
                if self.gamma>0.1:
                    if self.isX2dec: self.gamma=self.gamma*0.5 
                else:
                    self.gamma = 0
                self.isX2dec = True
            else:
                self.gamma = self.gamma*1.5 if self.gamma!=0 else 1
                self.x = self.x_pre
                self.X2 = self.X2_pre
                self.y_retri = self.y_retri_pre
                self.isX2dec = False

    def _x_retri_update(self):
        self.x_pre = self.x.copy()
        self.x = self.x + (self.dx*self.weighting)

    def _update(self):
        # first run
        if self.count == 0: 
            self.x = self.x_init 
            self.isX2dec = True

        self._preprocess()
        self._cal_dx()
        self._x_retri_update()
        if hasattr(self, 'func_plugin'): self.func_plugin(self)
        self._cal_X2()
        self.count += 1

    def start(self) -> int:
        '''
        Start to run the 1D Var method base on __init__ set.

        Returns: 
            processing status:                                                      <br>
            0: finished                                                             <br>
            1: X2==nan, sometime due to invalid input data set                      <br>
        '''
        res_status = 0
        self._B = self.B.copy()

        while self.count<self.max_runtime:
            self._update()
            self.record.X2.append(self.X2)
            self.record.x.append(self.x)
            self.record.y.append(self.y_retri)
            if np.isnan(self.X2): res_status=1; break
            if (self.X2<self.min_X2) & (self.count>self.min_runtime): break
        self._claen_parameter()
        return 0
    
    def get(self, parameters: Union[None, str, List[str]], asDict:bool = False):
        '''
        export the select parameters.

        Parameters:
            parameters: select the parameters you what to export

                    [
                        count,
                        count_best,
                        X2_best,
                        x_best,
                        record,
                    ]
            
            asDict: Export the data as dictionary. This work only for List[str] of parameters.
        '''
        if parameters==None: return self
        if isinstance(parameters,str): return self[parameters]
        if isinstance(parameters,list):
            if asDict:
                res = {}
                for key in parameters:
                    res[key] = self[key]
            else:
                res = [self[key] for key in parameters]
            return res
        

    def _claen_parameter(self):
        parameter_list = [
            'B',
            '_B',
            'Bi',
            'H',
            'HT',
            'R',
            'Ri',
            'X2',
            'X2_pre',
            'dx',
            'isX2dec',
            'max_runtime',
            'min_X2',
            'min_reject_runtime',
            'min_runtime',
            'weighting',
            'x',
            'x_background',
            'x_init',
            'x_pre',
            'x_step',
            'y_obs',
            'y_retri',
            'y_retri_pre',
            'gamma',
            'clean',
        ]

        if hasattr(self,'clean'):
            if self.clean:
                for val in parameter_list:
                    delattr(self,val)

    def main(self):
        pass

class Example:
    def __init__(self):
        pass
    def exmaple_1(self, config=None):
        def forward_model(x):
            '''
            x: [x0,x1,x2]
            y: [
                y1=exp(x0),
                y2=x0*x1,
                y3=x0+x1+x2,
                y4=x0*x1*x2
            ]
            '''
            return [
                np.exp(x[0]),
                x[0]*x[1],
                np.sum(x),
                x[0]*x[1]*x[2]
            ]
        
        background_x = [1,1,1]
        true_x = [2,5,8]
        true_y = forward_model(true_x)
        measurement_y = list(map(lambda x: x[1]+x[1]*0.1*(-1)**x[0], enumerate(true_y)))
        step_dx = [1E-5,1E-5,1E-5]

        # background error matrix
        B = [
            [10, 0, 0],
            [0, 10, 0],
            [0, 0, 10],
        ]
        # observation error matrix
        R = [
            [10, 3, 1, 0],
            [5, 7, 3, 2],
            [1, 3, 9, 8],
            [0, 0, 1, 5],
        ]


        config = dict(
            B = B,
            R = R,
            gamma = 0.7,
            func_forward = forward_model,
            x_background = background_x,
            y_obs = measurement_y,
            x_step = step_dx,
            min_runtime = 1,
            max_runtime = 20,
            min_reject_runtime = 1,
            min_X2 = 1,
            weighting = 1,
            clean = True
        )

        retri_obj = var1d(**config)
        status = retri_obj.start()
        res = retri_obj.get(None)
        pass

# class Test_1dVar(unittest.TestCase):
#     def test_

if __name__=='__main__':
    ex = Example()
    ex.exmaple_1()
    pass