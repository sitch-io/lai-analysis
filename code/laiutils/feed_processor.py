import laiutils
import os


class FeedProcessor(object):
    def __init__(self, carrier_reference):
        self.target_mcc_list = ["310", "311"]
        self.thread_pool_size = 6
        self.here_dir = os.path.dirname(os.path.abspath(__file__))
        self.src_dir = os.path.join(self.here_dir, '../../data/derived/lai/')
        self.reports_dir = os.path.join(self.here_dir, '../../reports/')
        self.csv_out_dir = os.path.join(self.reports_dir, 'outliers/csv/')
        self.md_out_dir = os.path.join(self.reports_dir, 'outliers/md/')
        self.infile_columns = ["radio", "mcc", "net", "area", "cell", "unit",
                               "lon", "lat", "range", "samples", "changeable",
                               "created", "updated", "averageSignal"]
        self.outfile_columns = ["subject_CGI", "distance", "nearest_CGI"]
        self.carrier_reference = carrier_reference
        self.distance_threshold = 30000

    @classmethod
    def get_carrier_name(cls, mcc, mnc, carrier_reference):
        carrier = "Unrecognized Carrier"
        for ref_row in carrier_reference:
            if mcc == ref_row["mcc"] and mnc == ref_row["mnc"]:
                carrier = ref_row["carrier"]
                break
        return carrier

    @classmethod
    def process_source_file(cls, in_file, carrier_reference, base_path):
        here_dir = base_path
        reports_dir = os.path.join(here_dir, '../reports/')
        csv_out_dir = os.path.join(reports_dir, 'outliers/csv/')
        carrier_reference = carrier_reference
        distance_threshold = 30000
        print("Processing %s" % in_file)
        mcc, mnc, lac = laiutils.Utility.mcc_mnc_lac_from_filename(in_file)
        carrier = FeedProcessor.get_carrier_name(mcc, mnc)
        report_file_name = laiutils.Utility.build_report_file_name(mcc, mnc,
                                                                   lac,
                                                                   csv_out_dir)
        report = laiutils.Utility.create_lai_report(in_file, carrier)
        laiutils.Report.write_lai_report(report, report_file_name)
        laiutils.Report.write_lai_report_md(report, report_file_name, carrier,
                                            distance_threshold)
        print("Finished processing %s" % in_file)
