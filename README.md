# TS6
The TS6.py file contains functions that will be frequently used when doing experiments on TS6 such as to plot $\psi$ during the merging (currently the only useful function).   

# Pre-request
* numpy
* matplotlib
* pandas
* scipy
* MDSplus
  
Modules except MDSplus can be easily downloaded by pip. For example, ```pip install numpy```.  

But installing MDSplus can be actually kind of bothersome (面倒くさいな…)... I tried my best to write down how to install the MDSplus module for python on our TS-group wiki's [MDSplus page](http://tanuki.t.u-tokyo.ac.jp/wiki/index.php/MDSplus). It should work both on Mac and Windows Subsystem Linux.

# How to install
Just download the TS6.py file and place it in any directory you like.

# Quick start
Simply download the TS6.py file, place it in any directory you like, open the terminal, go the directory where you placed TS6.py, type in python, and run 
```
~$python
>>>import TS6 as ts6
```   
To plot $\psi$ during the merging, as is the only useful function in this module up to date, simply run the following code:
```
>>>ts6.psi_plot(date, shot_in_the_date, renewal='exp')
```

Here ```renewal='exp'``` tells the function to read our TS-6 experiment log online. The input variables ```date``` and ```shot_in_the_date``` are the "date" and "shot" that we recorded in the TS-6 experiment log (note the shot is not the digitizer shot!!!). For example,
```
>>>ts6.psi_plot(240619, 20, renewal='exp')
```


Oh yeah!!! If the above ```psi_plot``` function succeeded, it would save the rawdata into the ```./240619/shot20.csv``` file.

During the experiments, there may be newly dead channels and we update the calibration sheet. I created a google spreadsheet [here](https://docs.google.com/spreadsheets/d/1izM2mY1kjGAxIqMIXwhyzw1iuuMF3k5VXFJqi9Sy2U4/edit?pli=1&gid=1603179474#gid=1603179474). If we update the calibration sheet in the above link, run the following code, the function should be able to see the difference (sorry I have not tested yet, because I failed to do any experiment since I finished this code).   
```
>>>ts6.psi_plot(240619, 20, renewal='both') 
```
Here ```renewal='both'``` tells the function to renew both experiment log and calibration log at the same time. If you just want to renew the calibration log, change it to ```renewal='cali'```


By default, TS6.py uses the 'Latest' sheet. But if we want to use another sheet, run
```
>>>ts6.set_cali_date(date)
```
Here  ```date``` is the sheet name.


# For more general usage....
As a not very useful module (...), currently the only useful function is ```psi_plot```. But if you want to continue developing this module (which is so much appreciated!!!), ```psi_at_t(date, shot_in_the_date, m)``` should return you the derived $\psi$ from $B_z$ at $t=m$ in microseconds $\mu s$. For example,
```
>>>ts6.psi_at_t(240619, 20, 460)
```
will return you the $\psi$ at 460 $\mu s$ in shot20 of 240619.

If there is any bugs, please raise an issue and I will try my best to fix them if I pass my entrance exam!!!

Have fun!!!!!!
