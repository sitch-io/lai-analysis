# LAI Study
## Using OpenCellID to determine geofence for LAI

So far, there are two scripts of interest:

* towers_by_lai.py: Breaks OpenCellID DB into files for each LAI, in CSV and KML format.
* report_outliers.py: Takes the files produced by the first script and produces CSV and MD reports on nearest neighbor CGI, with distances beyond 30km appearing in bold on MD reports.
