#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-04-28
# Last Modified: 2018-04-28
from __future__ import print_function, division, absolute_import
__author__     =['Victor Calderon']
__copyright__  =["Copyright 2018 Victor Calderon"]
__email__      =['victor.calderon@vanderbilt.edu']
__maintainer__ =['Victor Calderon']
__all__        =[   "myceil",
                    "myfloor",
                    "Bins_array_create",
                    "sigma_calcs",
                    "Stats_one_arr"]
"""
Set of statistical functions
"""

## Import modules
import math
import numpy as np
from   cosmo_utils.utils             import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

# Upper-bound values
def myceil(x, base=10):
    """
    Determines the upper-bound interger for a given number with a given base.

    Parameters
    ----------
    x : float
        Number to be approximated to closest number to `base`

    base : float
        Base used to calculate the closest largest number

    Returns
    ----------
    y : float
        Closest float number to `x`, i.e. upper-bound float

    Example
    ----------
    >>> myceil(12, 10)
    20.0

    >>> myceil(12.05, 1.)
    13.0

    >>> myceil(12.05, 0.5)
    12.5
    """
    y = float(base * math.ceil(float(x)/base))

    return y

## Lower-bound values
def myfloor(x, base=10):
    """
    Determines the lower-bound interger for a given number with a given base.

    Parameters
    ----------
    x : float
        Number to be approximated to closest number to `base`

    base : float
        Base used to calculate the closest largest number

    Returns
    ----------
    y : float
        Closest float number to `x`, i.e. upper-bound float

    Example
    ----------
    >>> myfloor(12, 10)
    10.0

    >>> myfloor(12.05, 1.)
    12.0

    >>> myfloor(12.05, 0.2)
    12.0
    """
    y = float(base * math.floor(float(x)/base))

    return y

## Generation of bins evenly spaced out
def Bins_array_create(arr, base=10):
    """
    Generates an evenly-spaced array between the minimum and maximum value 
    of a given array,

    Parameters
    ----------
    arr : array_like
        Array of of numbers or floats

    base : int or float, optional
        Interval used to create the evenly-spaced array of elements

    Returns
    ----------
    bins_arr : `numpy.ndarray`
        Array of elements separated in intervals of `base`

    Examples
    --------
    >>> Bins_array_create([1,2,3,4], base=2)
    array([0., 2., 4.])

    >>> Bins_array_create([5, 7, 13, 12], base=5)
    array([ 5., 10., 15.])
    """
    file_msg = fd.Program_Msg(__file__)
    # Transforming input data
    base = float(base)
    arr = np.asarray(arr)
    # Checking array dimensions
    if arr.ndim != 1:
        msg = '{0} The input array is not of dimension 1, but of `{1}`'.format(
            file_msg, arr.ndim)
        raise LSSUtils_Error(msg)
    # Creating evenly-spaced array
    arr_min  = myfloor(arr.min(), base=base)
    arr_max  = myceil(arr.max(), base=base)
    bins_arr = np.arange(arr_min, arr_max + 0.5*base, base)

    return bins_arr

## Calculations of percentiles and sigmas
def sigma_calcs(data_arr, type_sigma='std', perc_arr = [68., 95., 99.7],
    return_mean_std=False):
    """
    Calcualates the 1-, 2-, and 3-sigma ranges for `data_arr`

    Parameters
    -----------
    data_arr: numpy.ndarray, shape( param_dict['nrpbins'], param_dict['itern_tot'])
        array of values, from which to calculate percentiles or St. Dev.

    type_sigma: string, optional (default = 'std')
        option for calculating either `percentiles` or `standard deviations`
        Options:
            - 'perc': calculates percentiles
            - 'std' : uses standard deviations as 1-, 2-, and 3-sigmas

    perc_arr: array_like, optional (default = [68., 95., 99.7])
        array of percentiles to calculate

    return_mean_std: boolean, optional (default = False)
        option for returning mean and St. Dev. along with `sigma_dict`

    Return
    ----------
    sigma_dict: python dicitionary
        dictionary containg the 1-, 2-, and 3-sigma upper and lower 
        ranges for `data-arr`

    mark_mean: array_like
        array of the mean value of `data_arr`.
        Only returned if `return_mean_std == True`

    mark_std: array_like
        array of the St. Dev. value of `data_arr`.
        Only returned if `return_mean_std == True`
    """
    ## Determining shape of `data_arr`
    if data_arr.ndim == 1:
        axis = 0
    else:
        axis = 1
    ## Creating dictionary for saving `sigma`s
    sigma_dict = {}
    for ii in range(len(perc_arr)):
        sigma_dict[ii] = []
    ## Using Percentiles to estimate errors
    if type_sigma=='perc':
        for ii, perc_ii in enumerate(perc_arr):
            mark_lower = np.nanpercentile(data_arr, 50.-(perc_ii/2.),axis=axis)
            mark_upper = np.nanpercentile(data_arr, 50.+(perc_ii/2.),axis=axis)
            # Saving to dictionary
            sigma_dict[ii] = np.column_stack((mark_lower, mark_upper)).T
    ## Using standard deviations to estimate errors
    if type_sigma=='std':
        mean_val = np.nanmean(data_arr, axis=axis)
        std_val  = np.nanstd( data_arr, axis=axis)
        for ii in range(len(perc_arr)):
            mark_lower = mean_val - ((ii+1) * std_val)
            mark_upper = mean_val + ((ii+1) * std_val)
            # Saving to dictionary
            sigma_dict[ii] = np.column_stack((mark_lower, mark_upper)).T
    ##
    ## Estimating mean and St. Dev. of `data_arr`
    mark_mean = np.nanmean(data_arr, axis=axis)
    mark_std  = np.nanstd (data_arr, axis=axis)
    ## Fixing values for when `axis == 0`
    if data_arr.ndim == 1:
        for ii in range(len(sigma_dict.keys())):
            sigma_dict[ii] = sigma_dict[ii].flatten()

    if return_mean_std:
        return sigma_dict, mark_mean, mark_std
    else:
        return sigma_dict

## Main framework for `Stats_one_arr` and `Stats_two_arr`
def Stats_one_arr(x, y, base=1., arr_len=0, arr_digit='n', 
    weights=None, statfunc=np.nanmean, bin_statval='average', 
    failval = np.nan):
    """
    Calculates statists for 2 arrays

    Parameters
    ----------
    x1, y1 : array_like, shape(N,)
        Sets of elements for the 1st and 2nd observable

    base : float, optional
        Bin width in units of `x1`. This variable is set to 1. by default.

    arr_len : int, optional
        Minimum number of elements in each bin of `x1`

    arr_digit : {'n', 'y', 'o'} str, optional
        Option for which elements to return.
        - 'n' : Returns `x1_stat`, `y1_stat`, `y1_std`, `y1_std_err`
        - 'n' : Returns `x1_stat`, `y1_stat`, `y1_std`, `y1_std_err`, 
        - 'n' : Returns `x1_stat`, `y1_stat`, `y1_std`, `y1_std_err`

    weights : array_like or NoneType, optional
        Array of weights for values in `y1`. This is set to None by default.

    statfunc : {`numpy.nanmean`, `numpy.nanmedian`}statistical function, optional
        Numerical function used to calculate on bins of data.
        By default, this variable is set to `numpy.nanmean`

    bin_statval : {'average', 'left', 'right'} str, optional
        Option for where to put the bin values of `x1` and `y1`.
        By default, this variable is set to `average`, which means 
        that the values are those of the averages of the bins in `x1` and 
        `y1`.

    failval : int, float, NoneType, or NaN, optional
        This is the value used when no data is available for the bin.
        This is set to `numpy.nan` by default

    Returns
    ----------
    x1_stat, y1_stat : array_like
        Binned array of elements from `x1`

    y1_std : array_like
        Standard deviation of the binned array in `x1`

    y1_std_err : array_like
        Error in the `statfunc` of `y1`

    x1_bins_data : array_like, optional
        Elements of `x1` in each bin with spacing of `base`.
        Only returned if `arr_digit` == 'y' or 'o'

    y1_bins_data : array_like, optional
        Elements of `y1` in each bin with spacing of `base`.
        Only returned if `arr_digit` == 'y' or 'o'

    perc_lims : array_like, shape(N,3)
        Percentiles in each bin of `x1_stat`.
        Only returned if `arr_digit` == 'y' or 'o'
    """
    file_msg = fd.Program_Msg(__file__)
    ## Verifying input values
    # `arr_digit`
    if not ((arr_digit == 'y') or (arr_digit == 'n') or (arr_digit == 'o')):
        msg = '{0} `arr_digit` ({1}) is not a valid input. Exiting'.format(
            file_msg, arr_digit)
        raise LSSUtils_Error(msg)
    # Array dimensions
    if not ((len(x) > 0) and (len(y) > 0)):
        msg = '{0} The arrays `x1` and `y2` must have at least one value'
        msg = msg.format(file_msg)
        raise LSSUtils_Error(msg)
    # `arr_len`
    if not (arr_len > 0):
        msg = '{0} `arr_len` ({1}) must be greated than zero!'.format(
            file_msg, arr_len)
        raise LSSUtils_Error(msg)
    # `bin_statval`
    if not (bin_statval in ['average', 'left', 'right']):
        msg = '{0} `bin_statval` ({1}) is not a valid input! Exiting'.format(
            file_msg, bin_statval)
        raise LSSUtils_Error(msg)
    ##
    ## Converting arrays to numpy arrays
    x       = np.asarray(x)
    y       = np.asarray(y)
    nelem   = len(x1)
    arr_len = int(arr_len - 1.) if arr_len != 0 else int(arr_len)
    ##
    ## Statistics calculations
    x_bins   = Bins_array_create(x1, base=base)
    x_digits = np.digitize(x, x_bins)
    ##
    ## Elements in each bin
    # X-values
    x_bins_data = np.array([x[x_digits == ii] if
        len(x[x_digits == ii]) > arr_len else failval for ii
        in range(1, len(x_bins))])
    # Y-values
    y_bins_data = np.array([y[x_digits == ii] if
        len(y[x_digits == ii]) > arr_len else failval for ii
        in range(1, len(x_bins))])
    ##
    ## Selecting data in bins
    # Centered around the average
    if (bin_statval == 'average'):
        x_stat = np.array([statfunc(ii) if len(ii) > arr_len else failval
            for ii in x_bins_data])
    # Left-hand side of the bin
    if (bin_statval == 'left'):
        x_stat = np.array([x_bins[:-1][ii] if 
            len(x_bins_data[ii]) > arr_len else failval for ii
            in range(len(x_bins_data))])
    # Right-hand side of the bin
    if (bin_statval == 'right'):
        x_stat = np.array([x_bins[1:][ii] if
            len(x_bins_data[ii]) > arr_len else failval for ii
            in range(len(x_bins_data))])
    ##
    ## Determining the values in `y`
    # `stat_function`
    y_stat = np.array([statfunc(ii) if len(ii) > arr_len else failval
        for ii in y_bins_data])
    # Standard Deviation
    y_std  = np.array(np.nanstd(ii) if len(ii) > arr_len else failval
        for ii in y_bins_data)
    # Error in the mean/median
    y_std_err = np.array([
        np.nanstd(ii)/math.sqrt(len(ii)) if len(ii) > arr_len else failval
        for ii in y_bins_data])
    ##
    ## Removing `failval` elements
    x_fail_idx  = np.where(x_stat != failval)[0]
    x_stat      = x_stat     [x_fail_idx]
    y_stat      = y_stat     [x_fail_idx]
    y_std_err   = y_std_err  [x_fail_idx]
    x_bins_data = x_bins_data[x_fail_idx]
    y_bins_data = y_bins_data[x_fail_idx]
    ##
    ## Correcting error inf `statfunc` == `numpy.nanmedian`
    if statfunc == np.nanmedian:
        y_std_err *= 1.253
    ##
    ## Returning percentiles
    if return_perc:
        perc_arr_lims = sigma_calcs(y_stat)
    ##
    ## Returning values
    if return_perc:
        if arr_digit == 'n':
            return_val = [  x_stat, y_stat, y_std, y_std_err, perc_arr_lims]
        if arr_digit == 'y':
            return_val = [  x_stat, y_stat, y_std, y_std_err,
                            x_bins_data, y_bins_data, perc_arr_lims]
        if arr_digit == 'o':
            return_val = [  x_bins_data, y_bins_data, perc_arr_lims]
    else:
        if arr_digit == 'n':
            return_val = [  x_stat, y_stat, y_std, y_std_err]
        if arr_digit == 'y':
            return_val = [  x_stat, y_stat, y_std, y_std_err,
                            x_bins_data, y_bins_data]
        if arr_digit == 'o':
            return_val = [  x_bins_data, y_bins_data]

    return return_val