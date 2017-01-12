import imp
import os

modulename = 'laiutils'
here_dir = os.path.dirname(os.path.abspath(__file__))
modulepath = os.path.join(here_dir, "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
laiutils = imp.load_module(modulename, file, pathname, description)

# Almost 11k entries in this one
test_file = os.path.join(here_dir, "../fixture/310-410-65534.csv.gz")

carrier_name = "56k v.92 modemzzz"
lai_report = laiutils.Utility.create_lai_report(test_file, carrier_name)
