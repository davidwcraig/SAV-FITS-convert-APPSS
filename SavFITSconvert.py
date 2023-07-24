# SavFITSconvert.py
# D. Craig 2023-07-21
# WORKING NON-NOTEBOOK VERSION
# Usage python SavFITSconvert <infile>
#  - will strip off .sav from file name and write .fits file with same base name

import sys, argparse
from os.path import splitext # for filename extension splitting
import numpy as np
import matplotlib.pyplot as plt
# from sav_manip import sav_dict #small module for .sav files -dwc
from astropy.io import fits
import datetime

glVerboseFlag = False # global verbosity flag for script


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


# The `sav_manip.sav_dict` function opens the LBW data structure from IDL and puts
# the elements in a python dictionary. Most of its elements are reduced to scalars
# or simple arrays keyed by their keywords. A few are more nested structures that
# need a little more manipulation to be placed in the FITS HDUs.  This unpacks the
# `lbwsrc` variable in the idl structure.
# initial filenam for testing: 'S000018.4+273720.sav'
def make_hdu_list(sav_file_name, verbose=glVerboseFlag): 
    """make a fits HDU list structure for sav_file_name"""
    # get some APPSS data:
    appssd = sav_dict(sav_file_name)
     #diagnostic:
    if verbose:
        print("Items found in .sav structure:")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        for thing in appssd.items():
             print(thing)
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    ## Assemble parts of FITS file
    # Make the astropy data structure for a new fits file.
    tstamp = datetime.datetime.utcnow()
    t_str = tstamp.isoformat() + ' UTC'
    #This makes the first (primary) HDU, which is not very complicated.
    hdr = fits.Header()
    hdr['COMMENT'] = 'FITS file from idl .sav made using SavFITSconvert.py'
    hdr['HISTORY'] = 'David Craig for APPSS'
    hdr['HISTORY'] = 'Generated ' + t_str
    primary_hdu = fits.PrimaryHDU(header=hdr)
    # This makes the binary table hdu:
    col1 = fits.Column(name='VHELIO', format='D', array=appssd['VEL'], coord_unit='km/s')
    col2 = fits.Column(name='FREQUENCY', format='D', array=appssd['FREQ'], coord_unit='MHz')
    col3 = fits.Column(name='FLUX', format='D', array=appssd['SPEC'], coord_unit='mJy')
    col4 = fits.Column(name='BASELINE', format='D', array=appssd['BASELINE'], coord_unit='mJy')
    cols = fits.ColDefs([col1,col2,col3,col4])
    hdu = fits.BinTableHDU.from_columns(cols)
    # Now put in various keywords
    hdr = hdu.header # Make .FITS header structure
    # TODO: these need to be cross-checked with .sav structure if possible
    hdr.set('EXTNAME', 'Single Dish', 'APPSS Survey')
    hdr.set('OBSERVAT', 'Arecibo Observatory','Designation of Observatory')
    hdr.set('TELESCOP','Arecibo Radio Telescope','Designation of Telescope')
    hdr.set('INSTRUME','LBW receiver','Instrument in use')
    hdr.set('BEAM','3.3x3.8 ', 'Beam size [arcminutes] REVISE FOR LBW?')  #TODO                      
    hdr.set('NANVALUE',-999.000,'Value of missing/null data')                     
    hdr.set('OBJECT' , 'UNASSIGNED  ', 'Name of observed object')  #TODO NEEDS IMPORT if found               
    hdr.set( 'NAME'    , ' ' ,'Common name' )   #TODO NEEDS IMPORT if found 
    #appss idl text data is still in bytes, does it work? 
    #NOPE! So it must be decoded. .FITS standard accepts ASCII only:                      
    #NOTE: .sav files seem to have AGC tag but it is often zero (0)
    hdr.set('HISRC ', appssd['LBWSRCNAME'].decode('ascii'), 'HI source name')    
    hdr.set('ORIGIN', 'SavFITSconvert.py conversion D Craig', 'File creation location') 
    hdr.set('RA', appssd['RA'],'Right ascension in degrees')
    hdr.set('DEC', appssd['DEC'], 'Declination in degrees')
    hdr.set('EPOCH',2000.0,'Epoch for coordinates (years)')
    hdr.set('CHAN', appssd['NCHAN'], 'Number of spectral channels')
    hdr.set('BW', appssd['BANDWIDTH'],'Bandwidth [MHz]')
    hdr.set('WINDOW', appssd['WINDOW'].decode('ascii'), 'h for Hamming(?)')
    hdr.set('FITTYPE', appssd['FITTYPE'].decode('ascii'), 'P for polynomial')
    hdr.set('RMS', appssd['RMS'], 'RMS of spectrum (noise)')
    hdr.set('W50', appssd['W50'], 'estimated velocity width at 50%')
    hdr.set('W50ERR', appssd['W50ERR'], 'error in W50')
    hdr.set('W20', appssd['W20'], 'estimated velocity width at 20%')
    hdr.set('W20ERR', appssd['W20ERR'], 'error in W20')
    hdr.set('VSYS', appssd['VSYS'], 'systemic velocity [km/s]')
    hdr.set('VSYSERR',appssd['VSYSERR'], 'error in Vsys [km/s]')
    hdr.set('FLUX', appssd['FLUX'], 'integrated flux [Jy km/s]')
    hdr.set('FLUXERR', appssd['FLUXERR'], 'error in integrated flux')
    hdr.set('SN',appssd['SN'],'estimated signal-to-noise ratio')

    # now include all comments from the sav structure that are in the dict
    # this will insert a new comment for each of those lines.
    for line in range(appssd['COMMENTS'].COUNT[0]):
         hdr.set('COMMENT',appssd['COMMENTS'].TEXT[0][line].decode('ascii'))

    #comments for test file
    hdr.set('COMMENT', 'WARNING! Converted by early version of SavFITSconvert.py')

    #make the overall .FITS structure and RETURN IT:
    return fits.HDUList([primary_hdu, hdu])
    # END OF make_hdu_list

#script execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    parser.add_argument("input_file", type=str,
                    help=".SAV file to be converted to FITS")
    args = parser.parse_args()
    infile = args.input_file
    nameparts = splitext(infile)
    outfile = nameparts[0]+'.fits'
    hdul = make_hdu_list(infile, verbose=args.verbose)
    if args.verbose:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("OUTPUT:------------MAIN FITS HEADER----------------------")
        print(repr(hdul[0].header))
            
        print("OUTPUT:------------BINTABLE HEADER-----------------------")
        print(repr(hdul[1].header))
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print("Writing FITS file: ", outfile)
    hdul.writeto(outfile, overwrite = True)
