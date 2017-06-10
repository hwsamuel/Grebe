from enum import Enum

class Province():
    def __init__(self,id,name,geofence):
        self.id = id
        self.name = name
        self.geofence = geofence # Bounding box http://boundingbox.klokantech.com/

class Provinces(Enum):
    ON = Province('89b2eb8b2b9847f7','Ontario',[])
    AB = Province('96afdcaea18d3386','Alberta',[-120.0,49.0,-110.0,60.0])
    BC = Province('3e71718681740cba','British Columbia',[-139.05,48.22,-114.05,60.0])
    MB = Province('d3f39888bb7ef409','Manitoba',[])
    NS = Province('94965b2c45386f87','Nova Scotia',[])
    NB = Province('27485069891a7938','New Brunswick',[])
    NL = Province('e86f7b3223904650','Newfoundland and Labrador',[])
    PE = Province('d5cd04f09ef6e7c5','Prince Edward Island',[])
    QC = Province('e656cab40c80b32a','Quebec',[])
    SK = Province('aaf47682e345b807','Saskatchewan',[-110.01,49.0,-101.36,60.0])