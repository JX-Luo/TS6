import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import ticker

import MDSplus as mds

import scipy.interpolate as interp
import scipy.integrate as integ
import scipy.special as sp


plt.rcParams['mathtext.default'] = 'regular'


sheet_id = '1wG5fBaiQ7-jOzOI-2pkPAeV6SDiHc_LrOdcbWlvhHBw'
url = f'https://docs.google.com/spreadsheets/d/%s/export?format=csv' %sheet_id


exp_log = pd.read_csv(url)
exp_log['date'] = exp_log['date'].ffill()


dgt_ch_dic = {39:192, 40:120} # a dictionary which store the number of the digitizer's channels 
dgt_no = 39 # digitizer number
dgt_ch_no = dgt_ch_dic[dgt_no] # the number of the digitizer' channels


sheet_name_cali = 'latest'
sheet_id_cali = '1izM2mY1kjGAxIqMIXwhyzw1iuuMF3k5VXFJqi9Sy2U4'
url_cali = f'https://docs.google.com/spreadsheets/d/%s/gviz/tq?tqx=out:csv&sheet=%s' %(sheet_id_cali, sheet_name_cali)


cali_data = pd.read_csv(url_cali) # the calibration file.
cali_data['dtacq_num'] = cali_data['dtacq_num'].ffill() #filling the missing data


R_EF = 0.5
mu = 4e-7 * np.pi
n_EF = 234


Z_EF1 = 0.78 # the position of the equilibrium coils
Z_EF2 = -0.78 







def read_parameter(date, shot_in_the_date):
    '''
    this function read the experiment parameters which was taken in 'date', with a shot number 'shot_in_the_date'
    '''
    
    # reading TS-6 log, where date is 'date'(user input value) and shot is shot_in_the_date
    exp_in = exp_log.query('date=="%s" and shot=="%s"' %(date, shot_in_the_date))
    
    # the following code reads the parameter for you
    shot = exp_in['a039'].astype(int).iloc[0]
    tfshot = exp_in['a039_TF'].astype(int).iloc[0]
    exp_in = exp_in.infer_objects(copy=False).fillna(0)
    I_EF = exp_in['EF[A]'].astype(int).iloc[0]
    TF_voltage = exp_in['TF[kV]'].astype(int).iloc[0]

    return shot, tfshot, I_EF, TF_voltage





def read_data(date, shot_in_the_date):
    '''
    this function returns the rawdate which was taken in 'date', with a shot number 'shot_in_the_date'
    '''

    shot, tfshot, I_EF, TF_voltage = read_parameter(date, shot_in_the_date)

    try:
        
        rawdata = np.genfromtxt('./%s/shot%s.csv' %(date, shot_in_the_date), delimiter=',')

        print('using local file.')
        
    except FileNotFoundError:


        
        conn = mds.Connection('192.168.1.140')
        
        

        rawdata = np.empty([1000, dgt_ch_no]) # rawdata is to hold the data that is originally stored in Fourier
        
        conn.openTree('a%03i' %dgt_no, shot) # loading the shot data
        for i in range(dgt_ch_no):
            rawdata[:, i] = conn.get('AI:CH%03i' %(i+1))

        rawdata = rawdata - rawdata[600:650, :].mean(axis=0) # clear out the offset
        
    
        rawdata_tf = np.zeros_like(rawdata) # again, to hold the tfshot rawdata. BUT!!! MUST be zeros_like instead of empty here. 
                                            # because there maybe no TF current
        
        if tfshot != 0:

            conn.openTree('a%03i' %dgt_no, tfshot) # loading the tfshot data
            for i in range(dgt_ch_no):
                rawdata_tf[:, i] = conn.get('AI:CH%03i' %(i+1))
                
            rawdata_tf = rawdata_tf - rawdata_tf[600:650, :].mean(axis=0) # clear out the offset

            rawdata = rawdata - rawdata_tf # the useful, processable data
        
                
        try:
            np.savetxt('./%s/shot%s.csv' %(date, shot_in_the_date), rawdata, delimiter=',')
        except FileNotFoundError:
            os.mkdir('./%s' %date)
            np.savetxt('./%s/shot%s.csv' %(date, shot_in_the_date), rawdata, delimiter=',')

        print('using online file. new local file saved.')


    
    return rawdata #notice the indent here...





def rawdata_calibration(date, shot_in_the_date):
    '''
    this function reads the rawdata, calibrat it, and return the calibrated one.
    '''

    rawdata = read_data(date, shot_in_the_date)
    
    # take out the calibration data where digitizer is 39, ok is not 0 and direction is z
    cali_data_alivez = cali_data.query('dtacq_num==%s and ok!=0 and direction=="z"' %dgt_no)
    
    # take out the alive channels, remember to minus 1 because in python columns starts from 0
    rawdata_alive = rawdata[:, cali_data_alivez['dtacq_ch'].astype(int).values-1]
    
    # NS and polarity calibration
    rawdata_alive = rawdata_alive * cali_data_alivez['RC/NS'].values[None, :]
    rawdata_alive = rawdata_alive * cali_data_alivez['polarity'].values[None, :]

    return rawdata_alive





def RZ_coordinate():
    '''
    return the R-Z coordinate of our measurement points.
    '''

    cali_data_alivez = cali_data.query('dtacq_num==%s and ok!=0 and direction=="z"' %dgt_no)
    
    r_position = cali_data_alivez['rpos']
    z_position = cali_data_alivez['zpos']

    return r_position, z_position





def RZ_range():
    '''
    return the interpolated R and Z range of the measurement area.
    '''

    r_position, z_position = RZ_coordinate()

    
    r_interp = np.linspace(r_position.min(), r_position.max(), 40) # interpolation, for further integration
    z_interp = np.linspace(z_position.min(), z_position.max(), 50)

    return r_interp, z_interp





def Bz_interp_at_t(date, shot_in_the_date, m):
    '''
    this function interpolate the mearsured Bz and return the interpolated value.
    '''
    
    rawdata_alive = rawdata_calibration(date, shot_in_the_date)

    r_position, z_position = RZ_coordinate()

    r_interp, z_interp = RZ_range()
    
    tck = interp.bisplrep(r_position, z_position, rawdata_alive[m, :])

    return interp.bisplev(r_interp, z_interp, tck)





K = lambda k: sp.ellipk(k) # the canonical elliptical integral of the first kind
E = lambda k: sp.ellipe(k) # the canonical elliptical integral of the second kind





def B_EF(date, shot_in_the_date, Z):
    '''
    this equation calculates the Bz field generated by the equilibrium coils.
    It only takes Z as input, which is the Z coordinates of the coils
    '''

    shot, tfshot, I_EF, TF_voltage = read_parameter(date, shot_in_the_date)
    
    I = n_EF * I_EF

    r_interp, z_interp = RZ_range()
    
    z_ef = z_interp[None, :] + Z
    r_ef = r_interp[:, None]

    k = np.sqrt(4 * R_EF * r_ef / ((R_EF+r_ef)**2 + z_ef ** 2))
    
    return I * mu  / 2 / (np.pi * np.sqrt((R_EF+r_ef)**2 + z_ef**2)) * \
                         (E(k)*(R_EF**2-r_ef**2-z_ef**2)/((R_EF+r_ef)**2+z_ef**2-4*R_EF*r_ef) + K(k)) 
                               ## forgive me for giving something like this....
                               ## the thing inside the first big parenthesis is the big denomiator
                               ## the thing inside the second big parenthesis is the square brackets





def Bz_at_t(date, shot_in_the_date, m):
    '''
    this function returns the Bz at a certain time t.
    input m is the frame number, which corresponds to t=m*1us in experiment
    '''
    return Bz_interp_at_t(date, shot_in_the_date, m) - B_EF(date, shot_in_the_date, Z_EF1) - B_EF(date, shot_in_the_date, Z_EF2)





def RZ_mesh():
    '''
    this function returns the meshgrid of the interpolated RZ plane
    '''

    r_interp, z_interp = RZ_range()
    R_interp, Z_interp = np.meshgrid(r_interp, z_interp)

    return R_interp, Z_interp





def psi_at_t(date, shot_in_the_date, m):
    '''
    this function returns the psi at a certain time t.
    input m is the frame number, which corresponds to t=m*1us in experiment
    '''
    
    r_interp, z_interp = RZ_range()
    
    return integ.cumulative_trapezoid(Bz_at_t(date, shot_in_the_date, m) * r_interp[:, None], r_interp, axis=0) * 2 * np.pi





def psi_plot(date, shot_in_the_date, save=True, renewal=False, start=450, stop=490, lvs=90, psi_lim=[-10e-3, 10e-3]):
    '''
    this function only takes date and shot in the date as input
    and returns the psi plot

    input:
    ------
    date: the date at which the experiment is done
    shot_in_the_date: the shot number of the experiment within the date
    save: whether to save the plot. Default value is true.
    renewal: whether to renew the experiment log or the calibration log. Default is False,
             accepted values are 'exp', 'cali', and 'both'
    start: the start time of plotting 
    stop: the stop time of plotting
    lvs: the number of levels of the contourf plot of the magnetic lines
    '''

    if renewal:
        log_renewal(renewal)

    shot, tfshot, I_EF, TF_voltage = read_parameter(date, shot_in_the_date)
    
    R_interp, Z_interp = RZ_mesh()

    times_to_plot = np.linspace(start, stop, 9, dtype=int)
    

    fig, ax = plt.subplots(3, 3, figsize=[6, 6])
    fig.subplots_adjust(hspace=0.3)

    psi_upper, psi_lower = psi_lim
    levels = np.linspace(psi_upper, psi_lower, lvs)
    

    for idx, t in enumerate(times_to_plot):
        
            i, k = [idx//3, idx%3]
    
            CS = ax[i, k].contourf(R_interp[:, 1:], Z_interp[:, 1:], psi_at_t(date, shot_in_the_date, t).T, 30, cmap='RdBu', levels=levels)
            ax[i, k].contour(CS, levels=CS.levels[1:-1:3], colors='k')
            ax[i, k].set_title(r'%i $\mu s$' %t)

            # ax[i, k].plot(np.arange(0, 7) * 25e-3 + 9e-2, np.ones(7) * 2.1e-2, 'x', c='pinks', ms=4)
    
            if k!=0:
                ax[i, k].tick_params(labelleft=False)
            if i!=2:
                ax[i, k].tick_params(labelbottom=False)
    

    ax[2, 1].set_xlabel('R[m]')
    ax[1, 0].set_ylabel('Z[m]')
    
    cbar = fig.colorbar(CS, ax=ax, shrink=0.6)
    cbar.set_label('$\\psi$[mWb]')
    
    cbar.ax.yaxis.set_major_locator(ticker.MultipleLocator(2.5e-3))
    cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '%.1f' %(x*1e3)))
    
    
    fig.text(0.78, 0.86, 'TF=%ikV' %TF_voltage, fontdict={'weight':'bold', 'size':12})

    fig.suptitle('%s-shot%s' %(date, shot_in_the_date), fontproperties={'weight':'bold'})


    if save:
        fig.savefig('./%s/shot%s-9psi.jpg' %(date, shot_in_the_date), dpi=600)


    plt.show()





def log_renewal(renewal=False):
    '''
    this function renews the cali log and exp log,
    according to the user input

    the purpose of this function is to make sure you can 
    get the newest exp log or cali log, 
    as you write something new on those two files.
    '''

    global exp_log
    global cali_data
    
    if renewal =='both':

        exp_log = pd.read_csv(url)
        exp_log['date'] = exp_log['date'].ffill()
        
        cali_data = pd.read_csv(url_cali) # the calibration file.
        cali_data['dtacq_num'] = cali_data['dtacq_num'].ffill() #filling the missing data

        print('both exp log and cali log successfully updated!')

    elif renewal == 'cali':

        cali_data = pd.read_csv(url_cali) # the calibration file.
        cali_data['dtacq_num'] = cali_data['dtacq_num'].ffill() #filling the missing data

        print('calibration log successfully updated!!')

    elif renewal == 'exp':

        exp_log = pd.read_csv(url)
        exp_log['date'] = exp_log['date'].ffill()

        print('exp log successfully updated!!')

    else:

        raise NameError("unkown keyword!!! acceptable renewal keywords are 'both', 'cali', and 'exp'")





def set_cali_date(date):
    '''
    this function sets the calibration sheet you use.
    input the date and the code will automatically update the cali log
    '''
    global url_cali

    url_cali = f'https://docs.google.com/spreadsheets/d/%s/gviz/tq?tqx=out:csv&sheet=%s' %(sheet_id_cali, date)

    log_renewal('cali')

    print('now use %s calibration sheet.' %date)
