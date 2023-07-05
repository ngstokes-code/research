import csv
import math

LAMBDA = 0.15  # "wavelength in meters, realistic for LTE"
PI = math.pi


def free_space_path_loss(distance):
    numerator = 4*PI*distance
    fspl = math.pow(float(numerator/LAMBDA), 2)
    return fspl


# https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
def distance(origin, destination):
    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : tuple of float
        (lat, long)
    destination : tuple of float
        (lat, long)

    Returns
    -------
    distance_in_km : float

    Examples
    --------
    >>> origin = (48.1372, 11.5756)  # Munich
    >>> destination = (52.5186, 13.4083)  # Berlin
    >>> round(distance(origin, destination), 1)
    504.2
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


# https://stackoverflow.com/questions/33997361/how-to-convert-degree-minute-second-to-degree-decimal
def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    if direction == 'W' or direction == 'S':
        dd *= -1
    return dd


def convert_dms2dd(station):
    dms_lat = station['latitude']
    dms_long = station['longitude']

    # Montreal is latitude N, longitude W
    lat = dms2dd(dms_lat[0:2], dms_lat[2:4], dms_lat[4:6], 'N')
    long = dms2dd(dms_long[0:2], dms_long[2:4], dms_long[4:6], 'W')
    return (lat, long)


def csv_to_dict_list(filename):
    csvfile = open(filename, 'r')
    reader = csv.DictReader(csvfile)
    return [row for row in reader]

########## Business logic ##########
def montreal_stations(stations_dict):
    results = []
    for row in stations_dict:
        city = row['city'].strip()
        if city.lower() in {"montreal", "montréal"}:
            results.append(row)

    return results


if __name__ == "__main__":
    raw_t_lights = csv_to_dict_list('traffic lights.csv')
    stations = csv_to_dict_list('amstatio.csv')

    raw_montreal = montreal_stations(stations)  # len 26
    montreal = [
        {
            "name": s['call_sign'].strip(),
            "pos": convert_dms2dd(s)
        } for s in raw_montreal
    ]

    t_lights = [
        {
            "name": s['INT_NO'].strip(),
            "pos": (float(s['Latitude']), float(s['Longitude']))
        } for s in raw_t_lights
    ]

    for tl in t_lights:
        # closest = None
        closest_ct = min(montreal, key=lambda s: distance(tl['pos'], s['pos']))
        closest_ct_dist = distance(tl['pos'], closest_ct['pos'])  * 1000 # km * 1000 == m
        tl['closest_ct_dist'] = closest_ct_dist
        tl['fspl'] = free_space_path_loss(closest_ct_dist)

        """
        # Above is equivalent to...
        for ct in montreal:
            dist = distance(tl['pos'], ct['pos'])
            if not closest or dist < closest:
                closest = dist
                tl['closest_celltower'] = ct
                tl['closest_celltower']['distance'] = dist * 1000  # dist = km => want m

        tl['fspl'] = free_space_path_loss(tl['closest_celltower']['distance'])
        """

    breakpoint()  # view results


###################################################
"""
Montreal keys
['province', 'city', 'call_sign', 'frequency', 'class', 'latitude', 'longitude',
'banner', 'status1', 'status2', 'latitude2', 'longitude2', 'brdr_lat', 'brdr_long',
'border', 'can_land', 'usa_land', 'fre_land', 'st_creat', 'st_mod', 'ok_dump', 'doc_file',
'dec_number', 'ifrbn_d', 'ifrbn_n', 'clist1', 'clist2', 'clist3', 'clist4', 'clist5', 'clist6',
'clist7', 'clist8', 'clist9', 'clist10', 'network', 'cert_numb', 'bc_mode', 'unattended',
'auto_prog', 'euvalu', 'powerday', 'par_rms_d', 'q_day', 'powernight', 'par_rms_n', 'q_night',
'powercrit', 'par_rms_c', 'q_crit', 'channel'])

Traffic-light keys
['INT_NO', 'RUE_1', 'RUE_2', 'BOROUGH_NUM', 'BOROUGH',
'PERMANENT_OR_TEMPORARY', 'LOC_X', 'LOC_Y', 'Longitude', 'Latitude']
"""
