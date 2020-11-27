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