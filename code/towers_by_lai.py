import gzip
import laiutils
import os
import shutil
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

target_mcc_list = ["310", "311"]

here_dir = os.path.dirname(os.path.abspath(__file__))
source_data_dir = os.path.join(here_dir, '../data/source/')
derived_data_dir = os.path.join(here_dir, '../data/derived/')
kml_data_dir = os.path.join(derived_data_dir, 'kml/CGI_by_LAI/')
kml_md_web_base = "https://github.com/sitch-io/lai-reports/blob/master/outliers/md/"  # NOQA
lai_data_dir = os.path.join(derived_data_dir, 'lai/')
ocid_file = os.path.join(source_data_dir, "cell_towers.csv.gz")
outfile_columns = ["radio", "mcc", "net", "area", "cell", "unit", "lon", "lat",
                   "range", "samples", "changeable", "created", "updated",
                   "averageSignal"]

ocid_feed_object = laiutils.OcidCsv(ocid_file)
twilio_object = laiutils.TwilioCarriers(os.getenv("TWILIO_SID"),
                                        os.getenv("TWILIO_TOKEN"))
outfile_handler = laiutils.OutfileHandler(lai_data_dir, outfile_columns)
mcc_mnc_carrier_reference = twilio_object.get_providers_for_country("US")

laiutils.OutfileHandler.ensure_path_exists(lai_data_dir)
laiutils.OutfileHandler.ensure_path_exists(kml_data_dir)


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


def build_placemark_desc(mcc, mnc, lac):
    f_name = "%s-%s-%s-neighbors.md" % (mcc, mnc, lac)
    retval = "Outliers from this LAI: %s%s" % (kml_md_web_base, f_name)
    return retval


def dump_to_kml(lai_file):
    lai_obj = laiutils.OcidCsv(lai_file)
    kml_file = "%s.kml" % lai_file.replace('.csv.gz', '').replace("/lai/", "/kml/CGI_by_LAI/")  # NOQA
    kml_fld = KML.Folder()
    mcc, mnc, lac = mcc_mnc_lac_from_filename(lai_file)
    carrier_name = get_carrier_name(mcc, mnc)
    kml_fld.name = "%s-%s-%s__%s" % (mcc, mnc, lac, carrier_name)
    for tower in lai_obj:
        coords = ",".join([tower["lon"], tower["lat"]])
        kml_fld.append(KML.Placemark(KML.name(cgi_from_ocid_row(tower)),
                                     KML.Point(KML.coordinates(coords)),
                                     KML.description(build_placemark_desc(mcc, mnc, lac))))  # NOQA
    with open(kml_file, 'w') as out_file:
        out_file.write(etree.tostring(kml_fld))


def main():
    for row in ocid_feed_object:
        if row["mcc"] in target_mcc_list:
            outfile_handler.write_ocid_record(row)
    compress_and_remove_original(outfile_handler.feed_files)
    for lai_file in outfile_handler.feed_files:
        lai_file_compressed = "%s.gz" % lai_file
        dump_to_kml(lai_file_compressed)
    print("Done!")


if __name__ == "__main__":
    main()
