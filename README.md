# SAV-FITS-convert-APPSS
 Utility for converting IDL SAV files from AO to SDFITS for APPSS

 This originally began as a notebook using `scipy.io.readsav` and
 `astropy.io.fits` to convert Arecibo HI spectrum data from IDL `.sav` files 
 to FITS files for use by the [Undergrad ALFALFA
 team](http://egg.astro.cornell.edu/alfalfa/ugradteam/ugradteam.php)

 Documentation of readsav:
 [scipy.io.readsav](https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.readsav.html)

 ## Plan is to convert the notebook to a CLI utility for bulk conversion of .sav to FITS.

 ### ideas:

 -  make the CLI interface better with
    [argparse](https://docs.python.org/3/howto/argparse.html#argparse-tutorial)
 -  Fix all the SDFITS tags
 -  Make the output **filename** include a date/time stamp. 
    Make this optional later.
 -  Make sure there's not any more data in the .sav files


