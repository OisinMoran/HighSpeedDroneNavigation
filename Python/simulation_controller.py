## =========================== ##
##      Waypoint Tracking      ##
## =========================== ##

import math
import time

# Function to limit arguments to the move command to the range [-1,1]
def limit(x):
    if abs(x) <= 1:
        return x
    else:
        import math
        return math.copysign(1, x)

# List of x,y,z tuples representing waypoints
waypointList = [[500,3500,1000],[3500,500,1000]]
numWaypoints = len(waypointList)
# How close in mm do we need to get to the waypoint
waypoint_tolerance = 150

curPos = (0,0,0)

realFlag = True
finishedFlag = False

# Define Proportional Gains
KPyaw = (-1)/(math.pi)
KPphi = 0.0002
KPtheta = (-1)*KPphi
KPgaz = 0.001

# SETUP
# Ensure drone is aligned with y-axis facing in the increasing y direction
refYaw = 0

# First waypoint (waypoint counter)
n = 0

counter = 0
while not finishedFlag and counter < 2000: # This condition will become the Waypoint Reached condition
    time.sleep(0.1)
    print(counter)
    # SENSOR READING
    # Read current location
    # xpos,ypos,yaw
    with open("C:\Python34\PositionData.txt","r") as f:
        f_data = f.read()

    try:
        curPos = tuple([float(i) for i in f_data.split(" ")])
    except:
        print("READING ERROR")

    curYaw = curPos[2]
    print("Current position:\t {},{},{}".format(curPos[0], curPos[1], curYaw))
    print("Waypoint:\t\t {}".format(waypointList[n]))

    # Calculate error between drones current position and current waypoint
    errPos = tuple([i - j for i, j in zip(waypointList[n], curPos)])
    errYaw = math.radians(refYaw - curYaw)
    #errAlt = waypointList[n][2]-curAlt
    print("Error:\t\t {},{},{}".format(errPos[0], errPos[1], errYaw))

    # CONTROL
    # If waypoint is reached
    if math.hypot(errPos[0], errPos[1]) < waypoint_tolerance:
        time.sleep(3)
        # If there are no more waypoints we are finished
        if n+1 >= numWaypoints:
            finishedFlag = True
        # Otherwise advance to the next waypoint
        else:
            print("Next Waypoint")
            n += 1
    else:
        # Yaw
        yaw = KPyaw*(math.atan2(math.sin(errYaw), math.cos(errYaw)))
        #if abs(yaw) < 0.2:
            #yaw = 0
        print("Counterclockwise" if yaw < 0 else "Clockwise")

        # Roll
        phi = limit(KPphi*errPos[0])
        print("Left" if phi < 0 else "Right")

        # Pitch
        theta = limit(KPtheta*errPos[1])
        print("Forward" if theta < 0 else "Backward")

        # Vertical Speed
        #gaz = limit(KPgaz*errAlt)
        #print("Down" if gaz < 0 else "Up")

        #control.move(phi, theta, gaz, yaw)
        try:
                fileControl_data = open("C:\Python34\ControlData.txt","w")
                fileControl_data.write("{} {} {}".format(phi, theta, yaw))
                fileControl_data.close()
        except:
                pass

    counter +=1

print ("Journey Complete!" if finishedFlag else "Time Up!")
phi = theta = yaw = 0
fileControl_data = open("C:\Python34\ControlData.txt","w")
fileControl_data.write("{} {} {}".format(phi, theta, yaw))
fileControl_data.close()
