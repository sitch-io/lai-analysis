import csv
import glob
import gzip
import laiutils
import os
import shutil
from multiprocessing.dummy import Pool as ThreadPool

target_mcc_list = ["310", "311"]
thread_pool_size = 6

here_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(here_dir, '../data/derived/lai/')
reports_dir = os.path.join(here_dir, '../reports/')
csv_out_dir = os.path.join(reports_dir, 'outliers/csv/')
md_out_dir = os.path.join(reports_dir, 'outliers/md/')
infile_columns = ["radio", "mcc", "net", "area", "cell", "unit", "lon", "lat",
                  "range", "samples", "changeable", "created", "updated",
                  "averageSignal"]

outfile_columns = ["subject_CGI", "distance", "nearest_CGI"]

twilio_object = laiutils.TwilioCarriers(os.getenv("TWILIO_SID"),
                                        os.getenv("TWILIO_TOKEN"))

mcc_mnc_carrier_reference = twilio_object.get_providers_for_country("US")

distance_threshold = 30000

laiutils.OutfileHandler.ensure_path_exists(md_out_dir)
laiutils.OutfileHandler.ensure_path_exists(csv_out_dir)
dist_calc = laiutils.GeoUtil.calculate_distance

def get_carrier_name(mcc, mnc):
    carrier = "Unrecognized Carrier"
    for ref_row in mcc_mnc_carrier_reference:
        if mcc == ref_row["mcc"] and mnc == ref_row["mnc"]:
            carrier = ref_row["carrier"]
            break
    return carrier

def compress_and_remove_original(infiles):
    for uncompressed in infiles:
        infile = uncompressed
        outfile = "%s.gz" % infile
        with open(infile, 'rb') as f_in, gzip.open(outfile, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        print "Written: %s" % outfile
        os.remove(infile)
        print "Removed: %s" % infile

def cgi_from_ocid_row(row):
    return "%s-%s-%s-%s" % (row["mcc"], row["net"], row["area"], row["cell"])

def mcc_mnc_lac_from_filename(filename):
    basename = os.path.basename(filename).split(".")[0]
    mcc = basename.split("-")[0]
    mnc = basename.split("-")[1]
    lac = basename.split("-")[2]
    return(mcc, mnc, lac)

def build_report_file_name(mcc, mnc, lac):
    filename = "%s-%s-%s-neighbors.csv" % (mcc, mnc, lac)
    return os.path.join(csv_out_dir, filename)

def get_source_files_from_dir(directory):
    files = glob.glob(str(directory + "/*gz"))
    return files

def create_lai_report(in_file, carrier):
    mcc, mnc, lac = mcc_mnc_lac_from_filename(in_file)
    file_iter = laiutils.OcidCsv(in_file)
    return build_nearest_neighbors_struct(file_iter)

def build_nearest_neighbors_struct(file_iter):
    # prelim = [('cgi_1', 'cgi_2', '3000'),]
    prelim = []
    # final = {'cgi_1': {'distance': 3000, 'nearest': 'cgi_2'},}
    final = {}
    full_set = [x for x in file_iter]
    prelim = create_preliminaty_neighbors_struct(full_set)
    final = transform_prelim_into_final(prelim)
    return final

def transform_prelim_into_final(prelim):
    final = {}
    prelim_original = list(prelim)
    while prelim:
        x = prelim.pop()
        target_cgi = x[0]
        if target_cgi in final:
            continue
        best_distance, closest_cgi = find_nearest_cgi(target_cgi, prelim_original)
        final[target_cgi] = {'distance': best_distance,
                             'nearest': closest_cgi}
    return final

def find_nearest_cgi(target_cgi, prelim_original):
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

def create_preliminaty_neighbors_struct(source_set):
    print("\tProcessing %s rows, starting %s" % (str(len(source_set)),
                                                 cgi_from_ocid_row(source_set[0])))
    prelim = []
    while source_set:
        left = source_set.pop()
        left_cgi = cgi_from_ocid_row(left)
        for right in source_set:
            try:
                right_cgi = cgi_from_ocid_row(right)
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

def write_lai_report_md(report, report_file_name):
    mcc, mnc, lac = mcc_mnc_lac_from_filename(report_file_name)
    lai_report = "# %s-%s-%s\n## %s\n\n\n" % (mcc, mnc, lac,
                                              get_carrier_name(mcc, mnc))
    lai_report += "| CGI | Nearest CGI | Distance |\n"
    lai_report += "|-----|-------------|----------|\n"
    for cgi, relations in report.items():
        if relations['distance'] >= distance_threshold:
            lai_report += "| **%s** | **%s** | **%s** |\n" % (cgi,
                                                              relations['nearest'],
                                                              relations['distance'])
        else:
            lai_report += "| %s | %s | %s |\n" % (cgi, relations['nearest'],
                                                     relations['distance'])

    with open(report_file_name.replace("csv", "md"), 'w') as markdown_file:
        markdown_file.write(lai_report)


def write_lai_report(report, report_file_name):
    mcc, mnc, lac = mcc_mnc_lac_from_filename(report_file_name)
    columns = ["cgi", "nearest", "distance"]
    with open(report_file_name, 'w') as outfile:
        producer = csv.DictWriter(outfile, fieldnames=columns)
        producer.writeheader()
        for cgi, relations in report.items():
            producer.writerow({'cgi': cgi, 'nearest': relations['nearest'],
                               'distance': relations['distance']})

# CGI with nearest in-LAC CGI
# CGIs that don't have another CGI in-LAC within 30km

def process_source_file(in_file):
    print("Processing %s" % in_file)
    mcc, mnc, lac = mcc_mnc_lac_from_filename(in_file)
    carrier = get_carrier_name(mcc, mnc)
    report_file_name = build_report_file_name(mcc, mnc, lac)
    report = create_lai_report(in_file, carrier)
    write_lai_report(report, report_file_name)
    write_lai_report_md(report, report_file_name)
    print("Finished processing %s" % in_file)

def main():
    file_list = [in_file for in_file in get_source_files_from_dir(source_dir)]
    pool = ThreadPool(thread_pool_size)
    pool.map(process_source_file, file_list)
    pool.close()
    pool.join()
    print("Done!")

if __name__ == "__main__":
    main()
