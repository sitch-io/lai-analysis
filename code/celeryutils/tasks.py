from .celery import app
import os
import laiutils


@app.task
def process_feed_file(feed_file, carrier_reference, base_path):
    print "processing %s" % feed_file
    here_dir = base_path
    reports_dir = os.path.join(here_dir, '../reports/')
    csv_out_dir = os.path.join(reports_dir, 'outliers/csv/')
    debug = False
    carrier_reference = carrier_reference
    distance_threshold = 30000
    print("Processing %s" % feed_file)
    mcc, mnc, lac = laiutils.Utility.mcc_mnc_lac_from_filename(feed_file)
    carrier = laiutils.FeedProcessor.get_carrier_name(mcc, mnc,
                                                      carrier_reference)
    report_file_name = laiutils.Utility.build_report_file_name(mcc, mnc, lac,
                                                               csv_out_dir)
    report = laiutils.Utility.create_lai_report(feed_file, carrier, debug)
    laiutils.Report.write_lai_report(report, report_file_name)
    laiutils.Report.write_lai_report_md(report, report_file_name, carrier,
                                        distance_threshold)
