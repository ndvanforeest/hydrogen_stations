from dataclasses import dataclass, field

node_id = int


@dataclass(unsafe_hash=True)
class Point:
    node_id: int
    latitude: float = field(compare=False)
    longitude: float = field(compare=False)
    station_type: int = -1

    def to_gps(self):
        return [self.latitude, self.longitude]
