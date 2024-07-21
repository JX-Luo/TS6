# TS6
The TS6.py file contains functions that will be frequently used when doing experiments on TS6,   
such to plot $\psi$(currently the only useful function).

# Pre-request
* numpy
* matplotlib
* pandas
* scipy
* MDSplus
  
Modules except MDSplus can be easily downloaded by pip, for example: ```pip install numpy```  

Installing MDSplus can be actually kind of bothersome. (面倒くさいな…)  
I tried my best to write down how to install the MDSplus module for python on our TS-group wiki's [MDSplus page](http://tanuki.t.u-tokyo.ac.jp/wiki/index.php/MDSplus).  
That should both work on Mac and Windows Subsystem Linux.

# Quick start
Simply download the file, place it in any directory you like,    
open the terminal, type in python, and run 
```
~$python
>>>import TS6 as ts6
```   
As the only useful function up to date, to plot $\psi$, simply run the following code:
```
>>>ts6.psi_plot(date, shot_in_the_date, renewal='exp')
```

here ```date``` and ```shot_in_the_date``` are the "date" and "shot" as we recorded in the TS-6 log. (Not the digitizer shot!!!)   
For example:
```
>>>ts6.psi_plot(240619, 20, renewal='exp')
```
```renewal='exp'``` tells the function to read our TS-6 log online.   
Oh yeah!!! If the above ```psi_plot``` function succeeded, it would save the rawdata into the ```./240619/shot20.csv``` file.

During the experiments, there may be newly dead channels and we update the calibration sheet.   
I created a google spreadsheet [here](https://docs.google.com/spreadsheets/d/1izM2mY1kjGAxIqMIXwhyzw1iuuMF3k5VXFJqi9Sy2U4/edit?pli=1&gid=1603179474#gid=1603179474),    
if we update the calibration sheet in the above link, the function should be able to see the difference.   
(I have not tested yet, because I didn't make it to do any experiment after I finished this)   

By default, the TS6 module use the 'Latest' sheet, but if we want to use another sheet, run:
```
>>>ts6.set_cali_date(date)
```
here  ```date``` is the sheet name.


# For more general usage....
As a not very useful module... currently the only useful function is ```psi_plot```    
But if you want to continue developing this module, (which is so much appreciated!!!)    
```psi_at_t(date, shot_in_the_date, m)``` should return you the derived $\psi$ from $B_z$ at $t=m$ in microseconds $\mu s$    
for example:
```
>>>ts6.psi_at_t(240619, 20, 460)
```
will return you the $\psi$ at 460 $\mu s$ in shot20 of 240619.


Have fun!!!!!!



