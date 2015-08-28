from pipsolver import PIPSolver

class AlbertaPIPSolver(PIPSolver):
    def __init__(self):
        self.setPolygonLatitudes([59.955010, 59.955010, 48.994636, 48.994636, 53.800651, 59.955010])
        self.setPolygonLongitudes([-119.970703, -109.951172, -109.951172, -114.038086, -119.970703, -119.970703])
    
    def isWithinAlberta(self, latitude, longitude):
        return self.isWithinPolygon(latitude, longitude)
