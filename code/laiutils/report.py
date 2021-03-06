import csv
from utility import Utility as util


class Report(object):
    @classmethod
    def write_lai_report_md(cls, report, report_file_name, carrier_name,
                            distance_threshold):
        mcc, mnc, lac = util.mcc_mnc_lac_from_filename(report_file_name)
        lai_report = "# %s-%s-%s\n## %s\n\n\n" % (mcc, mnc, lac,
                                                  carrier_name)
        lai_report += "| CGI | Nearest CGI | Distance |\n"
        lai_report += "|-----|-------------|----------|\n"
        for cgi, relations in sorted(report.items()):
            if relations['distance'] >= distance_threshold:
                lai_report += Report.format_row(cgi, relations['nearest'],
                                                relations['distance'], True)
            else:
                lai_report += Report.format_row(cgi, relations['nearest'],
                                                relations['distance'], False)

        with open(report_file_name.replace("csv", "md"), 'w') as markdown_file:
            markdown_file.write(lai_report)

    @classmethod
    def format_row(cls, cgi, nearest, distance, bold=False):
        if bold:
            s = "| **%s** | **%s** | **%s** |\n" % (cgi, nearest, distance)
        else:
            s = "| %s | %s | %s |\n" % (cgi, nearest, distance)
        return s

    @classmethod
    def write_lai_report(cls, report, report_file_name):
        mcc, mnc, lac = util.mcc_mnc_lac_from_filename(report_file_name)
        columns = ["cgi", "nearest", "distance"]
        with open(report_file_name, 'w') as outfile:
            producer = csv.DictWriter(outfile, fieldnames=columns)
            producer.writeheader()
            for cgi, relations in report.items():
                producer.writerow({'cgi': cgi, 'nearest': relations['nearest'],
                                   'distance': relations['distance']})
