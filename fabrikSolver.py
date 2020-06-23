import numpy as np
import math
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
from mpl_toolkits.mplot3d import axes3d

def unitVector(vector):
    """ Returns the unit vector of a given vector. """

    # Divide the input vector by its magnitude.
    return vector / np.linalg.norm(vector)

class Segment2D:

    """ 
        A part of the FabrikSolver2D to store a part of an inverse kinematics chain.
    """

    def __init__(self, referenceX, referenceY, length, angle):

        self.angle = angle

        # Store the length of the segment.
        self.length = length

        # Calculate new coördinates.
        deltaX = math.cos(math.radians(angle)) * length
        deltaY = math.sin(math.radians(angle)) * length

        # Calculate new coördinates with respect to reference.
        newX = referenceX + deltaX
        newY = referenceY + deltaY

        # Store new coördinates.
        self.point = np.array([newX, newY])

    def setPoint(self, a, b, reference):
        # TODO: add high level function for updating point.
        pass

class FabrikSolver2D:
    """ 
        An inverse kinematics solver in 2D. Uses the Fabrik Algorithm.
    """
    def __init__(self, baseX=0, baseY=0, marginOfError=0.01):
        """ 
            marginOfError -> the margin of error for the algorithm.

            baseX -> x component of the base.

            baseY -> y coördinate of the base.

            Create the base of the chain.
            Initialize empty segment array -> [].
            Initialize length of the chain -> 0.
        """

        self.basePoint = np.array([baseX, baseY])
        self.segments = []
        self.armLength = 0
        self.marginOfError = marginOfError

    def addSegment(self, length, angle):
        
        if len(self.segments) > 0:

            segment = Segment2D(self.segments[-1].point[0], self.segments[-1].point[1], length, angle + self.segments[-1].angle)
        else:
            # Maak een segment van de vector beginpoint, lengte en hoek.
            segment = Segment2D(self.basePoint[0], self.basePoint[1], length, angle)

        # Voeg lengte toe aan de totale armlengte.
        self.armLength += segment.length

        # Voeg de nieuwe segment toe aan de list.
        self.segments.append(segment)

    def isReachable(self, targetX, targetY):

        """
            Check if a target endpoint is reachable by the end effector. 
        """

        if np.linalg.norm(self.basePoint - np.array([targetX, targetY])) < self.armLength:
            return True
        return False
    
    def inMarginOfError(self, targetX, targetY):
        if np.linalg.norm(self.segments[-1].point - np.array([targetX, targetY])) < self.marginOfError:
            return True
        return False

    def iterate(self, targetX, targetY):
        """ 
            targetX -> the target x coördinate to move to.
            
            targetY -> the target x coördinate to move to.

            Do one iteration of the fabrik algorithm. Used in the compute function. 
            Use in simulations or other systems who require motion that converges over time.  
        """
        
        target = np.array([targetX, targetY])

        # Backwards.
        for i in range(len(self.segments) - 1, 0, -1):

            # Op het uiteinde moeten we eerst het eindpunt gebruiken om de formule te kunnen toepassen.

            # Kijk of de waarde van i gelijk is aan de index van de laatse vector aan de arm.
            if i == len(self.segments) - 1:
                # Ga nog een index lager naar de een na laatse vector in de list. Gebruik dan de formule met de eindvector en vermenigvuldig met de lengte van de vector met de laatste index.

                # Vervang oude vector met nieuwe vector.
                self.segments[i-1].point = (unitVector(self.segments[i-1].point - target) * self.segments[i].length) + target

            else:
                self.segments[i-1].point = (unitVector(self.segments[i-1].point - self.segments[i].point) * self.segments[i].length) + self.segments[i].point

         # Forwards.
        for i in range(len(self.segments)):
            if i == 0:
                self.segments[i].point = (unitVector(self.segments[i].point - self.basePoint) * self.segments[i].length) + self.basePoint

            elif i == len(self.segments) - 1:
                self.segments[i].point = (unitVector(self.segments[i-1].point - target) * self.segments[i].length * -1) + self.segments[i-1].point

            else:
                self.segments[i].point = (unitVector(self.segments[i].point - self.segments[i-1].point) * self.segments[i].length) + self.segments[i-1].point

    def compute(self, targetX, targetY):
        """  
            Iterate the fabrik algoritm until the distance to the target is within the margin of error. 
        """

        if self.isReachable(targetX, targetY):
            while not self.inMarginOfError(targetX, targetY):
                self.iterate(targetX, targetY)         
        else:
            print('Target not reachable.')

    
    def plot(self, save=False, name="graph", xMin=-300, xMax=300, yMin=-300, yMax=300):
        
        # Plot arm.
        for i in range(len(self.segments)):
            # Plot the coördinate of a segment point.
            plt.plot([self.segments[i].point[0]], [self.segments[i].point[1]], 'ro')

            # Display coördinates of the point.
            plt.text(self.segments[i].point[0], self.segments[i].point[1] + 1, '(x:{}, y:{})'.format(int(self.segments[i].point[0]), int(self.segments[i].point[1])))

        # Plot begin point
        plt.plot([self.basePoint[0]], [self.basePoint[1]], 'bo')
        plt.text(self.basePoint[0], self.basePoint[1], 'Base')

        plt.axis([xMin, xMax, yMin, yMax])
        plt.grid(True)

        if save == True:
            plt.savefig('{}.png'.format(name))

        plt.show(block=True)

class Segment3D:
    """ 
        A part of the FabrikSolver3D to store a part of an inverse kinematics chain.
    """

    def __init__(self, referenceX, referenceY, referenceZ, length, xAngle, yAngle):

        self.xAngle = xAngle
        self.yAngle = yAngle

        # Store the length of the segment.
        self.length = length

        # Calculate new coördinates.
        deltaX = math.cos(math.radians(xAngle)) * length
        deltaY = math.sin(math.radians(xAngle)) * length
        deltaZ = math.sin(math.radians(yAngle)) * length

        # Calculate new coördinates with respect to reference.
        newX = referenceX + deltaX
        newY = referenceY + deltaY
        newZ = referenceZ + deltaZ

        # Store new coördinates.
        self.point = np.array([newX, newY, newZ])

class FabrikSolver3D:
    """ 
        An inverse kinematics solver in 3D. Uses the Fabrik Algorithm.
    """
    def __init__(self, baseX=0, baseY=0, baseZ=0,  marginOfError=0.01):
        """ 
            marginOfError -> the margin of error for the algorithm.

            baseX -> x component of the base.

            baseY -> y coördinate of the base.

            Create the base of the chain.
            Initialize empty segment array -> [].
            Initialize length of the chain -> 0.
        """

        self.basePoint = np.array([baseX, baseY, baseZ])
        self.segments = []
        self.armLength = 0
        self.marginOfError = marginOfError

    # FIXME: change xAngle to zAngle.
    def addSegment(self, length, xAngle, yAngle):
        if len(self.segments) > 0:

            segment = Segment3D(self.segments[-1].point[0], self.segments[-1].point[1], self.segments[-1].point[2], length, xAngle + self.segments[-1].xAngle, self.segments[-1].yAngle + yAngle)
        else:
            # Maak een segment van de vector beginpoint, lengte en hoek.
            segment = Segment3D(self.basePoint[0], self.basePoint[1], self.basePoint[2], length, xAngle, yAngle)

        # Voeg lengte toe aan de totale armlengte.
        self.armLength += segment.length

        # Voeg de nieuwe segment toe aan de list.
        self.segments.append(segment)

    def isReachable(self, targetX, targetY, targetZ):
        """
            Check if a target endpoint is reachable by the end effector. 
        """

        if np.linalg.norm(self.basePoint - np.array([targetX, targetY, targetZ])) < self.armLength:
            return True
        return False

    def inMarginOfError(self, targetX, targetY, targetZ):
        if np.linalg.norm(self.segments[-1].point - np.array([targetX, targetY, targetZ])) < self.marginOfError:
            return True
        return False     

    def iterate(self, targetX, targetY, targetZ):
        """ 
            targetX -> the target x coördinate to move to.
            
            targetY -> the target x coördinate to move to.

            Do one iteration of the fabrik algorithm. Used in the compute function. 
            Use in simulations or other systems who require motion that converges over time.  
        """

        target = np.array([targetX, targetY, targetZ])

        # Backwards.
        for i in range(len(self.segments) - 1, 0, -1):

            # Op het uiteinde moeten we eerst het eindpunt gebruiken om de formule te kunnen toepassen.

            # Kijk of de waarde van i gelijk is aan de index van de laatse vector aan de arm.
            if i == len(self.segments) - 1:
                # Ga nog een index lager naar de een na laatse vector in de list. Gebruik dan de formule met de eindvector en vermenigvuldig met de lengte van de vector met de laatste index.

                # Vervang oude vector met nieuwe vector.
                self.segments[i-1].point = (unitVector(self.segments[i-1].point - target) * self.segments[i].length) + target

            else:
                self.segments[i-1].point = (unitVector(self.segments[i-1].point - self.segments[i].point) * self.segments[i].length) + self.segments[i].point

         # Forwards.
        for i in range(len(self.segments)):
            if i == 0:
                self.segments[i].point = (unitVector(self.segments[i].point - self.basePoint) * self.segments[i].length) + self.basePoint

            elif i == len(self.segments) - 1:
                self.segments[i].point = (unitVector(self.segments[i-1].point - target) * self.segments[i].length * -1) + self.segments[i-1].point

            else:
                self.segments[i].point = (unitVector(self.segments[i].point - self.segments[i-1].point) * self.segments[i].length) + self.segments[i-1].point

    def compute(self, targetX, targetY, targetZ):

        """  
            Iterate the fabrik algoritm until the distance to the target is within the margin of error. 
        """
        
        if self.isReachable(targetX, targetY, targetZ):
            while not self.inMarginOfError(targetX, targetY, targetZ):
                self.iterate(targetX, targetY, targetZ)         
        else:
            print('Target not reachable.')
            sys.exit()

    def plot(self, save=False, name="graph"):
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection="3d")

        # Plot arm.
        for segment in self.segments:
            ax1.scatter(segment.point[2], segment.point[0], segment.point[1], c='r')
            # plt.text(segment.v[0], segment.v[1] + 1, '(x:{}, y:{})'.format(int(segment.v[0]), int(segment.v[1])))

        # Startpunt
        ax1.scatter(self.basePoint[2], self.basePoint[0], self.basePoint[1])

        ax1.set_xlabel('z-axis')
        ax1.set_ylabel('x-axis')
        ax1.set_zlabel('y-axis')

        plt.show()