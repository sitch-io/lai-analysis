# LAI Study
## Using OpenCellID to determine geofence for LAI

So far, there are two scripts of interest:

* towers_by_lai.py: Breaks OpenCellID DB into files for each LAI, in CSV and
  KML format.
* report_outliers.py: Takes the files produced by the first script and produces
  CSV and MD reports on nearest neighbor CGI, with distances beyond 30km
  appearing in bold on MD reports.


In order to run these scripts, you will need API access to Twilio, because
that's where we get the information to correlate MCC+MNC with the owning
provider.  You will also need to get a copy of the OpenCellID database from
http://opencellid.org/#action=database.downloadDatabase

Place the OpenCellID database at `lai-study/data/source`.  It should be named
`cell_towers.csv.gz` when you download it.  Just move it into place without
decompressing or renaming it.
