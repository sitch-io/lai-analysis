import glob
import operator
import os
from collections import deque
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
        return "%s-%s-%s-%s" % (row["mcc"], row["net"],
                                row["area"], row["cell"])

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
    def list_to_deque(cls, lst):
        ret = deque()
        for item in lst:
            ret.append((item))
        return ret

    @classmethod
    def create_preliminary_neighbors_struct(cls, source_set, debug):
        """This needs to be a generator..."""
        dist_calc = geo.calculate_distance
        source_len = len(source_set)
        first_cgi = Utility.cgi_from_ocid_row(source_set[0])
        print("\tProcessing %s rows, starting %s" % (str(source_len),
                                                     first_cgi))
        source_lst = list(source_set)
        item_iter = 0
        for item in source_lst:
            retval = {}
            item_iter += 1
            left = item
            left_cgi = Utility.cgi_from_ocid_row(left)
            retval[left_cgi] = {}
            if debug is True:
                of_str = "(%s of %s)" % (str(item_iter), str(source_len))
                print("Creating list of all neighbors for %s %s" % (left_cgi,
                                                                    of_str))
            for right in source_set:
                try:
                    right_cgi = Utility.cgi_from_ocid_row(right)
                    distance = dist_calc(left["lon"], left["lat"],
                                         right["lon"], right["lat"])
                    retval[left_cgi][right_cgi] = distance
                except ValueError as e:
                    message = "Trouble processing %s. Error: %s" % (str(right),
                                                                    e)
                    print(message)
            yield retval
            del retval

    @classmethod
    def build_nearest_neighbors_struct(cls, file_iter, debug):
        final = {}
        full_set = [x for x in file_iter]
        for item in Utility.create_preliminary_neighbors_struct(full_set,
                                                                debug):
            val = Utility.transform_prelim_into_final(item, debug)
            k, v = val.items()[0]
            final[k] = val[k]
        return final

    @classmethod
    def transform_prelim_into_final(cls, prelim, debug):
        final = {}
        target_cgi, neighs = prelim.items()[0]
        if debug:
            print("Getting nearest neighbor for %s" % target_cgi)
        neigh = neighs.items()
        best_distance, closest_cgi = Utility.find_nearest_cgi(neigh, debug)
        final[target_cgi] = {'distance': best_distance,
                             'nearest': closest_cgi}
        return final

    @classmethod
    def find_nearest_cgi(cls, neighbors, debug):
        best_distance = 0.0
        closest_cgi = ""
        neighbs_by_dist = sorted(neighbors, key=operator.itemgetter(1))
        if neighbs_by_dist[0][1] == 0.0:
            try:
                closest_cgi = neighbs_by_dist[1][0]
                best_distance = neighbs_by_dist[1][1]
            except IndexError:
                print("Unable to find neighbor!")
        return(best_distance, closest_cgi)

    @classmethod
    def create_lai_report(cls, in_file, carrier, debug=False):
        mcc, mnc, lac = Utility.mcc_mnc_lac_from_filename(in_file)
        file_iter = OcidCsv(in_file)
        return Utility.build_nearest_neighbors_struct(file_iter, debug)
