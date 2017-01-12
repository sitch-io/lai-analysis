import imp
import os

modulename = 'laiutils'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
laiutils = imp.load_module(modulename, file, pathname, description)


class TestGeoUtil:
    def test_geo_util_calculate_distance_far(self):
        madrid = (40.24, 3.41)
        chattanooga = (35.244, 85.1835)
        result = laiutils.GeoUtil.calculate_distance(madrid[0], madrid[1],
                                                     chattanooga[0],
                                                     chattanooga[1])
        assert int(result) == 6948027

    def test_geo_util_calculate_distance_near(self):
        work = (37.7793735, -122.3926168)
        beer = (37.775744, -122.3906212)
        result = laiutils.GeoUtil.calculate_distance(work[0], work[1],
                                                     beer[0],
                                                     beer[1])
        assert int(result) == 440
