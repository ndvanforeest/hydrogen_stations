import sqlite3
import folium

import stations.constants as constants
from stations.classes import Point


def get_points(con):
    """Return node coordinates of nodes in NODE_IDS."""
    points = set()
    sql = f"SELECT node_id, latitude, longitude, station_type FROM stations;"
    for node_id, latitude, longitude, station_type in (
        con.cursor().execute(sql).fetchall()
    ):
        points.add(
            Point(
                node_id=node_id,
                latitude=latitude,
                longitude=longitude,
                station_type=station_type,
            )
        )
    return points


def main():
    con = sqlite3.connect(constants.database)
    points = get_points(con)

    color = ["red", "blue", "green"]
    fieten_beilen = [52.85905, 6.49525]
    map = folium.Map(location=fieten_beilen, zoom_start=10)
    for point in points:
        folium.CircleMarker(
            location=point.to_gps(), radius=4, color=color[point.station_type]
        ).add_to(map)
    map.save("./stations.html")


if __name__ == '__main__':
    main()
