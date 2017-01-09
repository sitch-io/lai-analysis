from haversine import haversine


class GeoUtil(object):
    @classmethod
    def get_distance_between_points(cls, point_1, point_2):
        """ Forces type to float if it isn't already """
        if None in [point_1, point_2]:
            print("LocationTool: Invalid geo value. Returning 0 for distance.")
            distance = 0
        else:
            point_1 = (float(point_1[0]), float(point_1[1]))
            point_2 = (float(point_2[0]), float(point_2[1]))
            distance = haversine(point_1, point_2)
        return distance

    @classmethod
    def calculate_distance(cls, lon_1, lat_1, lon_2, lat_2):
        if None in [lon_1, lat_1, lon_2, lat_2]:
            print("Utility: Geo coordinate is zero, not resolving distance.")
            return 0
        pos_1 = (lon_1, lat_1)
        pos_2 = (lon_2, lat_2)
        dist_in_km = GeoUtil.get_distance_between_points(pos_1, pos_2)
        dist_in_m = dist_in_km * 1000
        return dist_in_m
