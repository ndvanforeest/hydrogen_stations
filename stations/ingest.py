import sqlite3
import pickle

import osmium
import numpy as np
from sklearn.neighbors import KDTree

from stations.classes import Point
from stations.enums import StationType
import stations.constants as constants


pbf_file = "/home/nicky/tmp/pbf/drenthe-latest.osm.pbf"

fuel_stations_tmp = constants.data_dir + "all_fuel_stations.pickle"
charging_stations_tmp = constants.data_dir + "all_charging_stations.pickle"
trunk_points_tmp = constants.data_dir + "trunk_points.pickle"

station_type_str = ["fuel", "charging_station"]


class HandleNodes(osmium.SimpleHandler):
    """Read the coordinates (lat, lon) for each node id in  node_ids."""

    def __init__(self, node_ids: set):
        osmium.SimpleHandler.__init__(self)
        self.node_ids = node_ids
        self.points = set()

    def node(self, n):
        if n.id in self.node_ids:
            self.points.add(Point(n.id, n.location.lat, n.location.lon))


class HandleStations(osmium.SimpleHandler):
    """Read the nodes ids, and gps coordinates of electric charging stations."""

    def __init__(self, station_type: int):
        osmium.SimpleHandler.__init__(self)
        self.station_type = station_type
        self.station_type_str = station_type_str[station_type]
        self.nodes = set()

    def node(self, n):
        if 'amenity' in n.tags and n.tags['amenity'] == self.station_type_str:
            self.nodes.add(n.id)

    def way(self, w):
        if 'amenity' in w.tags and w.tags['amenity'] == self.station_type_str:
            node = w.nodes[0]
            self.nodes.add(node.ref)


class HandleTrunks(osmium.SimpleHandler):
    """Read the node ids of all trunks."""

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.nodes = set()

    def way(self, w):
        if 'highway' in w.tags and w.tags['highway'] in ['trunk', 'motorway']:
            self.nodes.update(set(n.ref for n in w.nodes))


def extract_station_points(station_type, fname):
    handler = HandleStations(station_type)
    handler.apply_file(pbf_file)
    handler = HandleNodes(handler.nodes)
    handler.apply_file(pbf_file)
    for point in handler.points:
        point.station_type = station_type
    with open(fname, "wb") as fp:
        pickle.dump(handler.points, fp)


def extract_trunk_points():
    handler = HandleTrunks()
    handler.apply_file(pbf_file)
    handler = HandleNodes(handler.nodes)
    handler.apply_file(pbf_file)
    with open(trunk_points_tmp, "wb") as fp:
        pickle.dump(handler.points, fp)


def extract_data_to_tmp_files():
    """Read the data for the charging stations and trunks and write to tmp files."""
    extract_station_points(StationType.FUEL, fuel_stations_tmp)
    extract_station_points(StationType.CHARGING, charging_stations_tmp)
    extract_trunk_points()


def make_tables(con: sqlite3.Connection):
    sql = """-- sql
        DROP TABLE stations;
    """
    con.executescript(sql)
    sql = """-- sql
        CREATE TABLE stations (
          id INTEGER PRIMARY KEY,
          node_id INTEGER,
          latitude  FLOAT,
          longitude FLOAT,
          station_type int
    );
    """
    con.executescript(sql)


def insert_stations(con: sqlite3.Connection, stations: set()):
    stations = list(stations)
    ids = [p.node_id for p in stations]
    lats = [p.latitude for p in stations]
    lons = [p.longitude for p in stations]
    types = [p.station_type for p in stations]
    sql = (
        "INSERT OR IGNORE INTO stations(node_id, latitude, longitude, station_type)"
        " VALUES (?, ?, ?, ?);"
    )
    con.cursor().executemany(sql, zip(ids, lats, lons, types))
    con.commit()


def stations_near_trunks(con):
    with open(trunk_points_tmp, 'rb') as fp:
        trunk_points = pickle.load(fp)
    X = np.array([[p.latitude, p.longitude] for p in trunk_points])
    tree = KDTree(X)

    eps = constants.max_dist_to_trunk * 1e-5

    def handle_stattion_type(fname):
        with open(fname, 'rb') as fp:
            station_points = pickle.load(fp)
        Y = np.array([[p.node_id, p.latitude, p.longitude] for p in station_points])
        hits = tree.query_radius(Y[:, [1, 2]], r=eps, count_only=True)
        near_to_trunk = set(Y[hits > 0][:, 0].astype(int))
        points = {p for p in station_points if p.node_id in near_to_trunk}
        insert_stations(con, points)

    handle_stattion_type(fuel_stations_tmp)
    handle_stattion_type(charging_stations_tmp)


def main():
    extract_data_to_tmp_files()
    con = sqlite3.connect(constants.database)
    make_tables(con)
    stations_near_trunks(con)


if __name__ == '__main__':
    main()
