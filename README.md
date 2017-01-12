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


This is written for Python 2.7.  Required modules:

* celery
* haversine
* pykml
* twilio

The towers_by_lai file is the first stage.  It places the feed in files by LAI,
ready to be processed by report_outliers.py.  The report_outliers.py script
feeds rabbitmq on localhost, and you'll need to run
`celery worker -A celeryutils` to process the jobs.  If you want a nice web
interface to watch the jobs go by, install flower (from pip) and
`celery flower -A celeryutils`.  Go to the URL that comes up after starting
and you'll be able to adjust your queues, etc...
