from .celery import app
import os
import laiutils

@app.task
def process_feed_file(feed_file, carrier_reference, base_path):
    print "processing %s" % feed_file
    # feed_processor(feed_file, carrier_reference, base_path)
    target_mcc_list = ["310", "311"]
    thread_pool_size = 6
    here_dir = base_path
    source_dir = os.path.join(here_dir, '../data/derived/lai/')
    reports_dir = os.path.join(here_dir, '../reports/')
    csv_out_dir = os.path.join(reports_dir, 'outliers/csv/')
    md_out_dir = os.path.join(reports_dir, 'outliers/md/')
    infile_columns = ["radio", "mcc", "net", "area", "cell", "unit", "lon", "lat",
                      "range", "samples", "changeable", "created", "updated",
                      "averageSignal"]
    outfile_columns = ["subject_CGI", "distance", "nearest_CGI"]
    carrier_reference = carrier_reference
    distance_threshold = 30000
    print("Processing %s" % feed_file)
    mcc, mnc, lac = laiutils.Utility.mcc_mnc_lac_from_filename(feed_file)
    carrier = laiutils.FeedProcessor.get_carrier_name(mcc, mnc, carrier_reference)
    report_file_name = laiutils.Utility.build_report_file_name(mcc, mnc, lac,
                                                               csv_out_dir)
    report = laiutils.Utility.create_lai_report(feed_file, carrier)
    laiutils.Report.write_lai_report(report, report_file_name)
    laiutils.Report.write_lai_report_md(report, report_file_name, carrier,
                                        distance_threshold)
