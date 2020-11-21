# Document
>lib :      statistic
>verison :  v0.0.2
>Author :   Weiru-Chen
>Date :     2020-11-21

---
### Timean
>Structure: OOP

* method
    * set_config
    * input
    * get
    * isrepeat
    * second
    * minute
    * hour
    * day
    * month
    * year
* attribute
    * time
    * data
    * counts

1. Getting start with simple example
    ```
    from lib import statistic
    or 
    import statistic

    # Implement the object
    myobj = statistic.Timean()

    # Input data
    import datetime, random
    st = datetime.datetime(2020,1,1)
    number = 1000
    time = [st+datetime.timedelta(minutes=val) for val in range(number)]
    data = [[random.gauss(10,5) for _ in range(4)] for _ in range(number)]
    myobj.input(time,data)

    # Calculate and Get result
    myobj.hour()
    myobj.set_config(asDict=True)
    result = myobj.get()
    print(result)
    ```
2. **Config Setting** 
    ___config table___
    <div id="configTable"></div>
|ID     |Parameter      |Type       |Valid value        |Default        |Description                    |
|:-----:|:-------------:|:---------:|:-----------------:|:-------------:|:------------------------------|
|1      |asDict         |bool       |True or False      |False          |Set output format              |
|2      |storageForward |bool       |True or False      |True           |Set the data save point        |
|3      |fixTime        |bool       |True or False      |True           |Set statistic method<br>True: countiune with datetime<br>False: seperate by method|
|4      |zeroStart      |bool       |True or False      |True           |Set start time point           |
|5      |selfUpdate     |bool       |True or False      |True           |Set weather update self attributes |

3. mehtod and arguments
    * set_config(init,**kwargs)
        + init \<bool>: initialize or not, default is False
        + **kwargs: see [Config Table #2]()
    * input(time,data,dtype,header):
        + time: data time list
        + data: numerical data array
        + dtype: data type, use np.array(data,dtype=dtype) to regular data format, default is float
        + header: data header. If setted, output data will be formatted with header into dictionary, not control by config['asDict'], default is None
    * get(parameter)
        + parameter: select output parameter, default is None
            - config
            - time
            - data
            - counts
            - None  -- need set config['asDict']=True
    * isrepeat() -> bool<br>
        Check weather time repeat or not
    * second()<br>
        Statistic method, depend on config setting.
    * minute()<br>
        Statistic method, depend on config setting.
    * hour()<br>
        Statistic method, depend on config setting.
    * day()<br>
        Statistic method, depend on config setting.
    * month()<br>
        Statistic method, depend on config setting.
    * year()<br>
        Statistic method, depend on config setting.
