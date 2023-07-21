""" Module for manipulating idl .sav data files to convert them to sdfits.

sav_manip.py
David Craig
Initial version: 2019-Aug-8

"""

def sav_dict(sav_file):
    """Converts IDL sav file from lbwsrc etc. to return python dict"""
    from scipy.io import readsav
    
    idl_data = readsav(sav_file, verbose=False)  # this will be a numpy recarray, somewhat nested
    di = idl_data.lbwsrc # shorten name (lbwsrc is only top-level attribute)
    dd = {}   # data dict
    for ob in di.dtype.names:
        dd[ob] = getattr(di,ob)[0] # the [0] index gets the value for most of the pieces of the recarray.
                                   # Some are a bit more nested and will need recursing into.
    return dd

