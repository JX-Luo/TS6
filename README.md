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

Here ```renewal='exp'``` tells the function to read our TS-6 experiment log online. The input variables ```date``` and ```shot_in_the_date``` are the date and shot number within the date that we recorded in the TS-6 experiment log (note "shot_in_the_date" is not the digitizer shot number!!!). For example,
```
>>>ts6.psi_plot(240619, 20, renewal='exp')
```


Oh yeah!!! If succeeded, the function would save the rawdata into the ```./240619/shot20.csv```.

During the experiments, there may be newly dead channels and we update the calibration sheet. I created a google spreadsheet [here](https://docs.google.com/spreadsheets/d/1izM2mY1kjGAxIqMIXwhyzw1iuuMF3k5VXFJqi9Sy2U4/edit?pli=1&gid=1603179474#gid=1603179474). If we update the calibration sheet in this link and run the following code, the function should be able to see the difference (sorry I have not tested yet, because I failed to do any experiment since I finished this code).   
```
>>>ts6.psi_plot(240619, 20, renewal='both') 
```
Here ```renewal='both'``` tells the function to renew both experiment log and calibration log at the same time. If you just want to renew the calibration log, change it to ```renewal='cali'```. Similarly, if you don't want to renew anthing, run ```renewl=None```. 


By default, TS6.py uses the 'Latest' sheet in the calibration log. But if we want to use another sheet, run
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

If there is any bugs, please raise an issue and I will try my best to fix them (without guarantee)

Have fun!!!!!!


------------------------------------


# <b>Late Overview</b>
### <b>What is this code for? And its principle?</b>
Two dimonsional magnetic field measurement is necessary for merging experiments (otherwise how do we when know when and where do the plasmas merge?).   
To do so, on TS6, we use 2D pickup coil arrays. The idea, Faraday's law, is simple: the change of magnetic flux in the coil generates voltage, which can be written as

$$V_{coil}=-\frac{\partial\Psi}{\partial t}\approx-NS\frac{\partial B_{avg}}{\partial t}$$

so that 

$$B_{avg}=-\frac{1}{NS}\int V_{coil} \, dt$$

where $V_{coil}$ is the voltage, $\Psi$ is the magnetic flux, $t$ is time, $N$ and $S$ are the turns and area of the coil, and $B$ is the magetic field. Our TS6 magnetic coils use RC integrator to integrate the voltage signal, so that $\int V_{coil} \, dt = RC \, V_{out}$, where $RC$ is the time constant of the coil, and $V_{out}$ is the measured value.     

Finally, we get 

$$B_{avg} = \frac{RC}{NS}V_{out}$$  

Remember that $V_{out}$ is just the measured value, $RC$ and $NS$ are just some calibration constants that someone elso will give you, so this part is actuall super easy (especially with the help of the python pandas module). But keep in mind that $B_{avg}$ is only the time variant part, and there should be a background, which is the equilibrium field along the $Z$ direction. The equations are

$$B_{z, EF}=\frac{\mu_0I}{2\pi}\frac{1}{\sqrt{(R+r)^2+z^2}}\left[K(k)+\frac{R^2-r^2-z^2}{(R+r)^2+z^2-4rR}E(k)\right]$$

$$k^2=\frac{4Rr}{(R+r)^2+z^2}$$

where $R$ is the radius of the equilibrium field coils, $r$ and $z$ is the radial and vertical distance to the center of the equilibrium coils, $\mu$ is the permeability constant, and $I=N\times I_{EF}$ is the current in the coils. $E(k), K(k)$ are the canonical elliptical integral of the first and second kind. Don't get scared by this equation and its name, it can be super easily done with one line of python code. For how this equation comes to play, check [this website](https://tiggerntatie.github.io/emagnet-py/offaxis/off_axis_loop.html). Another very important thing to keep in mind is that, different libraies might calculate canonical elliptical integral using diffent notations. For example, python scipy library takes $m=k^2$ as input instead of $k$. Be careful.

Now we are ready to recover the 2D magnetic field. An initial guess may be to directly pick up the $B_z$ and $B_r$ and plot their stream line. However, a problem is that $B_r$ measurement is very untrustworthy as $B_r$ becomes very small through out the reconnection area. Luckily, in a cylindrical symmetric geometry, this can be solved by the magnetic flux $\Psi$ along the $r$ direction. The contour of $\Psi$ along the $r$ direction should be the magnetic lines on the poloidal plane (if they do not overlap, then the contour should change), and all other parameters can be derived from $\Psi$.

$$\Psi = \int_{r_0}^r 2\pi rB_z \, dr$$

$$B_r=\frac{1}{2\pi r} \frac{\partial \Psi}{\partial z}$$

$$E_t=-\frac{1}{2\pi r}\frac{\partial\Psi}{\partial t} $$





### <b>Miscelluous engineering problems</b>
Theory is straight forward, but engineering is forever imperfect. We always have problems too dirty to be written explicitly out. Throughout development and maintainence of the TS6_0.0 version, I encountered

1. <b>TF shot and offset noise</b>  
   This is related to two issues: TFshot and offset noise. Confusing as its name is, TFshot originates from the fact that the pickup coils in the $Z$ direction do not only pick up magnetic field in the $Z$ direction. Other components, toroidal and radial ones, also exist. The question is that when guide field is used, usually the toroidal field's (TF's) strength is way larger than that of the $Z$ field, imposing great noise. Before we found a better idea to overcome this problem, usually we measure a shot where there is only TF, and substract them from the experiment data. Offset noise is the electric circuit problem where the $V_{out}$ is not 0 when it is supposed to be. Usually, substracting the mean value of the first a tens of points should be enough, but sometimes the offset noise may still remain there after the completion of merging, and we need to substract the offset noise after merging.

   These above problems are previously deemed minor and are being take care of right at the time of reading and saving data (yes, in the previous versions, data reading and saving are done at the same time). However, these above miscelluous problems continues to be more annoying than ever thought, code tuning is very very very tiring and tedious, so I decided to change the way of data management completely.

   After TS6_1.0, no more date/shot_in_the_date style data saving will be used. All data is saved to a directory with its digizer shot number. Additionally, there will be two seperate functions dealing with the TF clearing and offset clearing. Finally, there would be a seperate function read_tree_data, which would open a tree in the local computer if offline mode is specified. Of course, this requires the tree to be copied to a local directory first.

2. <b>Probe signal noise</b>     
    It is easily understandable that the probe itself has some noise. The problem is how much problem will we have depending on how we smoooth them before feeding into a interpolation algorithm. After TS61.0 there will be a seperate function handling this problem. I will use gaussian kernel to do the smoothing instead of average smoothing, as average smoothing can be simply recogonized as gaussian kernel smoothing with infinite standard deviation. Note that the ```gaussian_filter1d``` used here relies heavily on trial and error. It is said an initial guess would be around 1/10 of the data range, and since our range of interest is just 460~490, and after a lot of trial and error, I decided on an appropriate sigma value is 0.12 or 0.15.

4. <b>Interpolation with dead channels</b>     
    Perhaps the biggest hidden / runtime bug in the TS6_0.0 version (which took me around one week to find). As we know that our TS6 magnetic probes pick up magnetic fields on a rectangular grid, which we then use to interpolate a higher resolution meshgrid. Nice and sweet as it sounds, an extremely dirty problem is that, what do we do when there are dead channels?... Can these remaining measured values still be used as a rectangular grid? If not, how do we fix this problem? Do we first interpolate the missing values on the grid, and then use it for high resolution interpolation? Or, do we directly use it as unstructured data?
    There is no perfect answer. Previously the TS6_0.0 version directly feeds the alive data to a interpolation algorithm. However, this is by default treating the alive channels as unstructured data, and might have imposed great bias on the result until discovered by accident. This problem is still under investigation...

6. <b>Interpolation range</b>    
    Perhaps another annoying problem is deciding the interpolation meshgrid. The problem is that we are interpolating $B_z$, but wanting to plot $\psi$, which is the integral of $B_z$ along the $r$ direction. This brings a problem that, if our $B_z$ did not cover the smallest radius as possible, then there must be an systematic bias to $\psi$, as there are some $B_z$ that is not integrated in the inner radius region. However, if we extend our integration area to the inner radius region, the interpolation inherently becomes extrapolation there, bringing new problems to the result.

   (However, this occurred to me and should be helpful. Since we never need the absolute value of $\psi$ (all other physical properties derived from $\psi$ is its derivative), and $B$ is almost completely parallel to the $z$ direction in the inner $r$ region (this means that $B_z$ is constant at a $r$ postion as long as $r$ is small enough), we can conclude that the incomplete integration of $B_z$ only causes a constant bias to $\psi$, which never affects the magnetic field line plot, nor the derivative of $\psi$.)



