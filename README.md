
# Metstat Meteorological statistics

The purpose of this project is to try and get some statistics on
meteorological data and visualize them

The current target is to make a 3D graph of maximum and minimum 
temperatures per day of year, for a range of years

So far it has reached the stage of downloading data, and no futher, 
since I can only work on it a couple of hours every week

Currently data is to be downloaded from NOAA's Web services API 
version 2.

Note that you need a token to do this. Obtain a token from
https://www.ncdc.noaa.gov/cdo-web/token
and place it in _~/.metstat/token_ (since the token entry
dialog box isn't written yet.

Note that you can only download one year's worth of data at a time.
(We should fix that later by automatic downloading of 
larger chunks).

* Only works for cities right now - need to develop something 
for met stations

* The first time you use it, download the list of cities. This will 
be saved in a database for later
* Next, get the data types for the city you want.
* Now choose a range of dates. Doesn't support dates before 1900
(Python limit, needs fixing). Choose a year or less 
* Finally get the data (if it works...)
* That's all I've developed so far.
