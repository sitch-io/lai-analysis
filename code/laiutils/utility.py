import glob
import os
from geo_util import GeoUtil as geo
from ocid_csv import OcidCsv as OcidCsv
class Utility(object):
    @classmethod
    def mcc_mnc_lac_from_filename(cls, filename):
        basename = os.path.basename(filename).split(".")[0]
        mcc = basename.split("-")[0]
        mnc = basename.split("-")[1]
        lac = basename.split("-")[2]
        return(mcc, mnc, lac)

    @classmethod
    def cgi_from_ocid_row(cls, row):
        return "%s-%s-%s-%s" % (row["mcc"], row["net"], row["area"], row["cell"])

    @classmethod
    def build_report_file_name(cls, mcc, mnc, lac, csv_out_dir):
        filename = "%s-%s-%s-neighbors.csv" % (mcc, mnc, lac)
        return os.path.join(csv_out_dir, filename)

    @classmethod
    def get_source_files_from_dir(cls, directory):
        dirglob = str(directory + "*gz")
        print "Getting files from %s" % dirglob
        files = glob.glob(dirglob)
        return files

    @classmethod
    def create_preliminary_neighbors_struct(cls, source_set):
        dist_calc = geo.calculate_distance
        first_cgi = Utility.cgi_from_ocid_row(source_set[0])
        print("\tProcessing %s rows, starting %s" % (str(len(source_set)),
                                                     first_cgi))
        prelim = []
        while source_set:
            left = source_set.pop()
            left_cgi = Utility.cgi_from_ocid_row(left)
            for right in source_set:
                try:
                    right_cgi = Utility.cgi_from_ocid_row(right)
                    distance = dist_calc(left["lon"], left["lat"],
                                         right["lon"], right["lat"])
                    if not (left_cgi, right_cgi, distance) in prelim:
                        if not (right_cgi, left_cgi, distance) in prelim:
                            measurement = (left_cgi, right_cgi, distance)
                            prelim.append(measurement)
                except ValueError as e:
                    message = "Trouble processing %s.  Error: %s" % (str(right), e)
                    print(message)
        return prelim

    @classmethod
    def build_nearest_neighbors_struct(cls, file_iter):
        # prelim = [('cgi_1', 'cgi_2', '3000'),]
        prelim = []
        # final = {'cgi_1': {'distance': 3000, 'nearest': 'cgi_2'},}
        final = {}
        full_set = [x for x in file_iter]
        prelim = Utility.create_preliminary_neighbors_struct(full_set)
        final = Utility.transform_prelim_into_final(prelim)
        return final

    @classmethod
    def transform_prelim_into_final(cls, prelim):
        final = {}
        prelim_original = list(prelim)
        while prelim:
            x = prelim.pop()
            target_cgi = x[0]
            if target_cgi in final:
                continue
            best_distance, closest_cgi = Utility.find_nearest_cgi(target_cgi,
                                                                  prelim_original)
            final[target_cgi] = {'distance': best_distance,
                                 'nearest': closest_cgi}
        return final

    @classmethod
    def find_nearest_cgi(cls, target_cgi, prelim_original):
        best_distance = 20037500  # ~1/2 circumfrence of the earth
        closest_cgi = ""
        for y in prelim_original:
            if target_cgi in y and y[2] < best_distance:
                best_distance = y[2]
                if y[0] == target_cgi:
                    closest_cgi = y[1]
                else:
                    closest_cgi = y[0]
        if closest_cgi == "":
            print("BIG PROBLEM FINDING CLOSEST_NEIGHBOR FOR %s" % target_cgi)
            print("prelim_original = %s" % str(prelim_original))
        return(best_distance, closest_cgi)

    @classmethod
    def create_lai_report(cls, in_file, carrier):
        mcc, mnc, lac = Utility.mcc_mnc_lac_from_filename(in_file)
        file_iter = OcidCsv(in_file)
        return Utility.build_nearest_neighbors_struct(file_iter)
