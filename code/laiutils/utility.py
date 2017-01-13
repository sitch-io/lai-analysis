import glob
import operator
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
    def create_preliminary_neighbors_struct(cls, source_set, debug):
        dist_calc = geo.calculate_distance
        source_len = len(source_set)
        first_cgi = Utility.cgi_from_ocid_row(source_set[0])
        print("\tProcessing %s rows, starting %s" % (str(source_len),
                                                     first_cgi))
        source_lst = list(source_set)
        prelim = {}
        item_iter = 0
        for item in source_lst:
            item_iter += 1
            left = item
            left_cgi = Utility.cgi_from_ocid_row(left)
            prelim[left_cgi] = {}
            if debug is True:
                of_str = "(%s of %s)" % (str(item_iter), str(source_len))
                print("Creating list of all neighbors for %s %s" % (left_cgi,
                                                                    of_str))
            for right in source_set:
                try:
                    right_cgi = Utility.cgi_from_ocid_row(right)
                    distance = dist_calc(left["lon"], left["lat"],
                                         right["lon"], right["lat"])
                    # if not (left_cgi, right_cgi, distance) in prelim:
                    #     if not (right_cgi, left_cgi, distance) in prelim:
                    #        measurement = (left_cgi, right_cgi, distance)
                    #        prelim.append(measurement)
                    # measurement = {left_cgi: {right_cgi: distance}}
                    # prelim.append(measurement)
                    prelim[left_cgi][right_cgi] = distance
                except ValueError as e:
                    message = "Trouble processing %s.  Error: %s" % (str(right), e)
                    print(message)
        return prelim

    @classmethod
    def build_nearest_neighbors_struct(cls, file_iter, debug):
        # prelim = [('cgi_1', 'cgi_2', '3000'),]
        prelim = []
        # final = {'cgi_1': {'distance': 3000, 'nearest': 'cgi_2'},}
        final = {}
        full_set = [x for x in file_iter]
        prelim = Utility.create_preliminary_neighbors_struct(full_set, debug)
        final = Utility.transform_prelim_into_final(prelim, debug)
        return final

    @classmethod
    def transform_prelim_into_final(cls, prelim, debug):
        final = {}
        for x, y in prelim.items():
            target_cgi = x
            if debug:
                print("Getting nearest neighbor for %s" % x)
            best_distance, closest_cgi = Utility.find_nearest_cgi(y, debug)
            final[target_cgi] = {'distance': best_distance,
                                 'nearest': closest_cgi}
        return final

    @classmethod
    def transform_prelim_into_final_OLD(cls, prelim, debug):
        final = {}
        prelim_original = list(prelim)
        while prelim:
            x = prelim.pop()
            target_cgi = x[0]
            if target_cgi in final:
                continue
            if debug:
                print("Finding nearest neighbor for %s" % target_cgi)
            best_distance, closest_cgi = Utility.find_nearest_cgi(target_cgi,
                                                                  prelim_original,
                                                                  debug)
            final[target_cgi] = {'distance': best_distance,
                                 'nearest': closest_cgi}
        return final

    @classmethod
    def find_nearest_cgi_OLD(cls, target_cgi, prelim_original, debug):
        best_distance = 20037500  # ~1/2 circumfrence of the earth
        closest_cgi = ""
        for y in prelim_original:
            if debug is True:
                print("Searching for nearest to %s" % y[0])
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
    def find_nearest_cgi(cls, neighbors, debug):
        best_distance = 0.0
        closest_cgi = ""
        neighbs_by_dist = sorted(neighbors.items(), key=operator.itemgetter(1))
        if neighbs_by_dist[0][1] == 0.0:
            try:
                closest_cgi = neighbs_by_dist[1][0]
                best_distance = neighbs_by_dist[1][1]
            except IndexError:
                print("Unable to find neighbor!")
        return(best_distance, closest_cgi)

    @classmethod
    def find_nearest_cgi_old(cls, neighbors, debug):
        best_distance = 20037500  # ~1/2 circumfrence of the earth
        closest_cgi = ""
        for y in neighbors.items():
            if y[1] == 0.0:
                continue
            elif y[1] > best_distance:
                continue
            else:
                best_distance = y[1]
                closest_cgi = y[0]
        if closest_cgi == "":
            print("BIG PROBLEM FINDING CLOSEST_NEIGHBOR!")
            print("prelim_original = %s" % str(neighbors))
        return(best_distance, closest_cgi)

    @classmethod
    def create_lai_report(cls, in_file, carrier, debug=False):
        mcc, mnc, lac = Utility.mcc_mnc_lac_from_filename(in_file)
        file_iter = OcidCsv(in_file)
        return Utility.build_nearest_neighbors_struct(file_iter, debug)
