# Statistic Document

## Getting Start

install git library
```
pip install git
or
pip3 install git
```

simple code:

1. Objective: Wanna download lib from url: git@github.com:AmberCrafter/pythonlib_statistic.git

2. Save location: want to save the file at ./lib/

```
def download_lib():
    import git
    git.Git('./lib/').clone('git@github.com:AmberCrafter/pythonlib_statistic.git')
```

## ChangeLog

* 2.0.0 (2021-08-09)
    - append data type constraint
    - finished document by mkdocs

* 1.1.2 (2021-08-07)
    - change file name: statistic -> timeseries

* 1.1.1 (2020-12-29)
    - append quartile method
> feture: need to change the sequence data process method.

* 1.1.0 (2020-12-02)
    - append std, max, min, maxTime, minTime method   - 
    - change class name. Timean->Time - 
    - change output data structure. data\[haeder]->data\[statistic]\[haeder]
> In this version, there still has some old data structure code, and weird data stucture.