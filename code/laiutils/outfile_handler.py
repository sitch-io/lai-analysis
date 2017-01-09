import csv
import os
import time


class OutfileHandler(object):
    def __init__(self, base_path, ocid_columns):
        self.base_path = base_path
        self.ensure_path_exists(self.base_path)
        self.ocid_columns = ocid_columns
        self.feed_files = []

    def lai_from_row(self, row):
        return "-".join([row["mcc"], row["net"], row["area"]])

    def write_ocid_record(self, row):
        dir_name = self.base_path
        file_name = "%s.csv" % self.lai_from_row(row)
        file_path = os.path.join(dir_name, file_name)
        if file_path in self.feed_files:
            self.append_feed_file(file_path, self.ocid_columns, row)
        else:
            self.start_feed_file(file_path, self.ocid_columns, row)
            self.feed_files.append(file_path)

    def start_feed_file(self, file_path, columns, row):
        print "Starting a new feed file: %s" % file_path
        with open(file_path, 'w') as outfile:
            producer = csv.DictWriter(outfile, fieldnames=columns)
            producer.writeheader()
            producer.writerow(row)
        return

    def append_feed_file(self, file_path, columns, row):
        with open(file_path, 'a') as outfile:
            producer = csv.DictWriter(outfile, fieldnames=columns)
            try:
                producer.writerow(row)
            except ValueError as e:
                print "ValueError!"
                print repr(e)
                print str(row)
        return

    @classmethod
    def ensure_path_exists(cls, dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            time.sleep(1)
