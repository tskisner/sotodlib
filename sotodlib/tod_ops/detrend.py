import numpy as np

def detrend_data(tod, method='linear', axis_name='samps', 
            signal_name='signal'):
    
    """Returns detrended data. Decide for yourself if it goes
        into the axis manager. Generally intended for use before filter.
        Using this with method ='mean' and axis_name='dets' will remove a 
        common mode from the detectors
    
    Arguments:
    
        tod: axis manager
    
        method: method of detrending can be 'linear' or 'mean'
        
        axis_name: the axis along which to detrend. default is 'samps'
        
        signal_name: the name of the signal to detrend. defaults to 'signal'
            if it isn't 2D it is made to be.
        
    Returns:
        
        detrended signal: does not actually detrend the data in the axis
            manager, let's you decide if you want to do that.
    """
    assert len(tod._assignments[signal_name]) <= 2
        
    signal = np.atleast_2d(getattr(tod, signal_name))
    axis = getattr(tod, axis_name)
    
    if len(tod._assignments[signal_name])==1:
        ## will have gotten caught by atleast_2d
        idx = 1
        other_idx = None
        
    elif len(tod._assignments[signal_name])==2:
        checks = np.array([x==axis_name for x in tod._assignments[signal_name]],dtype='bool')
        idx = np.where(checks)[0][0]
        other_idx = np.where(~checks)[0][0]
    
    if other_idx is not None and other_idx == 1:
        signal = signal.transpose()
        
    if method == 'mean':
        signal = signal - np.mean(signal, axis=1)[:,None]
    elif method == 'linear':
        x = np.linspace(0,1, axis.count)
        slopes = signal[:,-1]-signal[:,0]
        signal = signal - slopes[:,None]*x 
        signal -= np.mean(signal, axis=1)[:,None]
    else:
        raise ValueError("method flag must be linear or mean")

    if other_idx is not None and other_idx == 1:
        signal = signal.transpose()
    return signal

def detrend_tod(tod, method='linear'):
    """simple wrapper: to be more verbose"""
    tod.signal = detrend_data(tod, method='linear')
    return tod
