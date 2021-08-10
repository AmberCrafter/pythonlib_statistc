# Getting Start
---
install git library
```
pip install git
or
pip3 install git
```

simple code:
1. Objective: Wanna download lib from url: git@github.com:AmberCrafter/toolbox_meteo.git
2. Save location: want to save the file at ./lib/
```
def download_lib():
    import git
    git.Git('./lib/').clone('git@github.com:AmberCrafter/toolbox_meteo.git')
```

---
## ChangeLog
[version 1.1.2]
Update time: 2021-08-07
1. change file name: statistic -> timeseries

[version 1.1.1]
Update time: 2020-12-29
1. append quartile method
feture: need to change the sequence data process method.

[version 1.1.0]
Update time: 2020-12-02
1. append std, max, min, maxTime, minTime method
2. change class name. Timean->Time
3. change output data structure. data[haeder]->data[statistic][haeder]

In this version, there still has some old data structure code, and weird data stucture.