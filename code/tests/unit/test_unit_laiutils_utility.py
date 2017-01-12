import imp
import os

modulename = 'laiutils'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
laiutils = imp.load_module(modulename, file, pathname, description)


class TestUtility:
    def test_utility_mcc_mnc_lac_from_filename(self):
        sample = "/etc/whatever/nothing/310-411-266-42302.csv.gz"
        expected = ("310", "411", "266")
        assert expected == laiutils.Utility.mcc_mnc_lac_from_filename(sample)

    def test_utility_cgi_from_ocid_row(self):
        sample = {"mcc": "310", "net": "411", "area": "266", "cell": "42302"}
        expected = "310-411-266-42302"
        assert expected == laiutils.Utility.cgi_from_ocid_row(sample)
