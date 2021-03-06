import numpy as np
import scipy.stats as stats

from so3g.proj import Ranges, RangesMatrix

from .tod_ops import filters
from .tod_ops import fourier_filter

def get_turnaround_flags(tod, qlim=1, merge=True, overwrite=False,
                         name='turnarounds'):
    """Flag the scan turnaround times.

    Args:
        tod: AxisManager object
        qlim: percentile used to find turnaround
        merge: If true, merge into tod.flags
        name: name of flag when merged into tod.flags

    Returns:
        flag: Ranges object of turn-arounds 

    """
    az = tod.boresight.az
    lo, hi = np.percentile(az, [qlim,100-qlim])
    m = np.logical_or(az < lo, az > hi)
    
    flag = Ranges.from_bitmask(m)
    
    if merge:
        if name in tod.flags and not overwrite:
            raise ValueError('Flag name {} already exists in tod.flags'.format(name))
        elif name in tod.flags:
            tod.flags[name] = flag
        else:
            tod.flags.wrap(name, flag)
    return flag


def get_glitch_flags(tod, params={}, signal='signal', merge=True, 
                     overwrite=False, name='glitches'):
    """ Find glitches with fourier filtering
    Translation from moby2 as starting point
    
    Args:
        tod (AxisManager): the tod 
        params (dictionary): Use to overwrite the default values
                n_sig: significance of detection
                t_glitch: Gaussian filter width
                hp_fc: high pass filter cutoff
                buffer: amount to buffer flags around found location
        merge (bool): if true, add to tod.flags
        name (string): name of flag to add to tod.flags
        overwrite (bool): if true, write over flag. if false, don't
    
    Returns:
        flag: RangesMatrix object of glitches
    """
    gparams = {'n_sig':10, 
               't_glitch':0.002, 
               'hp_fc':5.0, 
               'buffer':200,}
    gparams.update(params)
    params=gparams
    
    # f-space filtering
    filt = filters.high_pass_sine2(params['hp_fc']) * filters.gaussian_filter(params['t_glitch'])
    fvec = fourier_filter(tod, filt, detrend='linear', 
                          signal_name=signal, resize='zero_pad')
    # get the threshods based on n_sig x nlev = n_sig x iqu x 0.741
    fvec = np.abs(fvec)
    thres = 0.741 * stats.iqr(fvec, axis=1) * params['n_sig']
    # get flags
    msk = fvec > thres[:,None]
    flag = RangesMatrix( [Ranges.from_bitmask(m) for m in msk])
    flag.buffer(params['buffer'])
    
    if merge:
        if name in tod.flags and not overwrite:
            raise ValueError('Flag name {} already exists in tod.flags'.format(name))
        elif name in tod.flags:
            tod.flags[name] = flag
        else:
            tod.flags.wrap(name, flag)
        
    return flag
