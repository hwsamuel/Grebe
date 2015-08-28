import math
import unittest

class PIPSolver(unittest.TestCase):
    def setPolygonLatitudes(self, polygonLatitudes):
        self.polygonLatitudes = polygonLatitudes

    def setPolygonLongitudes(self, polygonLongitudes):
        self.polygonLongitudes = polygonLongitudes
    
    def isWithinPolygon(self, latitude, longitude):
        numLatitudes = len(self.polygonLatitudes)
        angle = 0
        
        for i in range (0, numLatitudes):
            pointALatitude = self.polygonLatitudes[i] - latitude
            pointALongitude = self.polygonLongitudes[i] - longitude
            pointBLatitude = self.polygonLatitudes[(i+1) % numLatitudes] - latitude;
            pointBLongitude = self.polygonLongitudes[(i+1) % numLatitudes] - longitude
            angle += self.angle2D(pointALatitude, pointALongitude, pointBLatitude, pointBLongitude)
       
        if abs(angle) < math.pi:
            return 0
        else:
            return 1

    def angle2D(self, y1, x1, y2, x2):
        theta1 = math.atan2(y1,x1);
        theta2 = math.atan2(y2,x2);
        dtheta = theta2 - theta1;
       
        while dtheta > math.pi:
            dtheta -= 2*math.pi;
       
        while (dtheta < -math.pi):
            dtheta += 2*math.pi;
       
        return(dtheta)
    
    def setUp(self):
        self.setPolygonLatitudes([59.955010, 59.955010, 48.994636, 48.994636, 53.800651, 59.955010])
        self.setPolygonLongitudes([-119.970703, -109.951172, -109.951172, -114.038086, -119.970703, -119.970703])
        
    def testIsWithinPolygon(self):
        self.assertTrue(self.isWithinPolygon(53.514185, -113.378906))
        self.assertFalse(self.isWithinPolygon(25.831538,-1.069338))

if __name__ == '__main__':
    unittest.main()
