from skyfield.api import EarthSatellite, load, wgs84, Topos
from datetime import datetime
from django.utils import timezone

def convert_to_datetime_field(time_windows):
    """
    Converts a list of time windows with string datetime to Django DateTimeField-compatible objects.
    """
    converted_time_windows = []
    for window in time_windows:
        start_str, end_str = window  # Extract start and end time strings

        # Convert string to datetime object
        start_datetime = datetime.strptime(start_str, '%Y %b %d %H:%M:%S')
        end_datetime = datetime.strptime(end_str, '%Y %b %d %H:%M:%S')

        # Make datetime timezone-aware (assuming UTC)
        start_datetime_aware = timezone.make_aware(start_datetime, timezone.utc)
        end_datetime_aware = timezone.make_aware(end_datetime, timezone.utc)

        converted_time_windows.append([start_datetime_aware, end_datetime_aware])

    return converted_time_windows

def define_groundstation(latitude_degree, longitude_degree, elevation):
    """
    This method defines a groundstation based on the latitdue, longitude and elevation provided

    @param latitude_degree: a float number indicates the latitude
    @param longitude_degree: a float number indicates the longitude
    @param elevation: a float number indicates the elevation
    @return: return the ground station
    """
    ground_station_location = Topos(latitude_degrees=latitude_degree, longitude_degrees=longitude_degree,
                                    elevation_m=elevation)
    return ground_station_location


def define_satellite(TLE):
    """
    This method defines a satellite based on the TLE provided

    @param TLE: two lines element, here is an example: ['SOSO-1', '1 00001U 3274.66666667 .00000000 00000-0 00000-0 0
    00001', '2 00001 097.3597 167.6789 0009456 299.5645 340.3650 15.25701051000010'] @return: return the satellite
    """
    satellite = EarthSatellite(TLE[1], TLE[2], TLE[0])
    return satellite


def get_time_window(satellite, groundstation, start_time, end_time, altitude_degree):
    """
    This method returns a list of time windows where each time windows includes time for : [acquisition of signal,
    loss of signal]

    @param satellite: a satellite created using define_satelite(TLE)
    @param groundstation: a ground station created using define_groundstation
    @param start_time: start time using load.timescale().utc()
    @param end_time: end time using load.timescale().utc()
    @param altitude_degree: a float number indicates the altitude degree
    @return: a list of time windows(list)
    """
    time_windows = []
    time, events = satellite.find_events(groundstation, start_time, end_time, altitude_degrees=altitude_degree)#try 5 as input
    index = 0
    window = [None] * 2
    for t, e in zip(time, events):
        if index == 0:
            if e != 0:
                window[0] = start_time.utc_strftime('%Y %b %d %H:%M:%S')
            if e == 2:
                window[1] = t.utc_strftime('%Y %b %d %H:%M:%S')
                time_windows.append(list(window))
        elif index == len(time):
            if e != 2:
                window[1] = end_time.utc_strftime('%Y %b %d %H:%M:%S')
                time_windows.append(list(window))
        else:
            if e == 0:
                window[0] = t.utc_strftime('%Y %b %d %H:%M:%S')
            elif e == 2:
                window[1] = t.utc_strftime('%Y %b %d %H:%M:%S')
                time_windows.append(list(window))
        index += 1
    return convert_to_datetime_field(time_windows)
