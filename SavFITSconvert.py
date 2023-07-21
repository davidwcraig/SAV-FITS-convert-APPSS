# SavFITSconvert0.py
# D. Craig 2023-07-20
# This is a copy of the chain of python code in 
# Storage/davidwcraigx/persistent/appss-alfalfa-fits/alfalfa-apps-fits-0.ipynb
#
# WORKING NON-NOTEBOOK VERSION

import numpy as np
import matplotlib.pyplot as plt
from sav_manip import sav_dict #small module for .sav files -dwc
from astropy.io import fits
import datetime

# The `sav_manip.sav_dict` function opens the LBW data structure from IDL and puts
# the elements in a python dictionary. Most of its elements are reduced to scalars
# or simple arrays keyed by their keywords. A few are more nested structures that
# need a little more manipulation to be placed in the FITS HDUs.  It unpacks the
# `lbwsrc` variable in the idl structure.

# get some APPSS data:
appssd = sav_dict('S000018.4+273720.sav')
#diagnostic:
print("Items found in .sav structure:")
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
for thing in appssd.items():
    print(thing)

## Assemble parts of FITS file
# Make the astropy data structure for a new fits file.
tstamp = datetime.datetime.utcnow()
t_str = tstamp.isoformat() + ' UTC'
#This makes the first (primary) HDU, which is not very complicated.
hdr = fits.Header()
hdr['COMMENT'] = 'TEST .FITS file from idl .sav made using SavFITSconvert.py'
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
hdr.set('COMMENT', 'WARNING! Converted by early version of SavFITSconvert.py !')

#make the overall .FITS structure and write:
hdu_lst = fits.HDUList([primary_hdu, hdu])
hdu_lst.writeto('APPSS_test_tab.fits', overwrite = True)
