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
waypointList = [[2500,3200,1000],[4000,2200,1000]]
numWaypoints = len(waypointList)
# How close in mm do we need to get to the waypoint
waypoint_tolerance = 150

curPos = (0,0,0)

realFlag = True
finishedFlag = False

# Define Proportional Gains
KPyaw = (-1)/(math.pi)
KPphi = 0.0002
KPtheta = (-1.2)*KPphi
KPgaz = 0.001

# SETUP
# Ensure drone is flat on ground
util.flatTrim()
# Ensure drone is aligned with y-axis facing in the increasing y direction
refYaw = sensors.getOrientation("YAW")
 
if realFlag:
	control.takeOff()
	util.calibrateMagnetometer()
	time.sleep(10)

# First waypoint (waypoint counter)
n = 0

counter = 0
while not finishedFlag and counter < 2000: # This condition will become the Waypoint Reached condition
	time.sleep(0.01)
	print(counter)
	# SENSOR READING
	# Read current location
	with open("C:\Python34\PozyxData.txt","r") as f:
		f_data = f.read()
	# Read current yaw
	curYaw = sensors.getOrientation("YAW")
	# Read current height
	curAlt = 1000*sensors.getAltitude()
	try:
		curPos = tuple([float(i) for i in f_data.split(" ")])
	except:
		print("READING ERROR")
	print("Current position:\t {},{},{}".format(curPos[0], curPos[1], curAlt))
	print("Waypoint:\t\t {}".format(waypointList[n]))

	# Calculate error between drones current position and current waypoint
	errPos = tuple([i - j for i, j in zip(waypointList[n], curPos)])
	errYaw = math.radians(refYaw - curYaw)
	errAlt = waypointList[n][2]-curAlt
	print("Error:\t\t {},{},{}".format(errPos[0], errPos[1], errAlt))

	# CONTROL
	# If waypoint is reached
	# Currently just 2D error, 3D would be: (maybe abstract to function for readability)
	# if math.hypot(math.hypot(errPos[0], errPos[1]), errAlt) < waypoint_tolerance:
	if math.hypot(errPos[0], errPos[1]) < waypoint_tolerance:
		control.hover()
		time.sleep(5)
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
		if abs(yaw) < 0.2:
			yaw = 0
		print("Counterclockwise" if yaw < 0 else "Clockwise")

		# Roll
		phi = limit(KPphi*errPos[0])
		print("Left" if phi < 0 else "Right")

		# Pitch
		theta = limit(KPtheta*errPos[1])
		print("Forward" if theta < 0 else "Backward")

		# Vertical Speed
		gaz = limit(KPgaz*errAlt)
		print("Down" if gaz < 0 else "Up")

		if realFlag:
			control.move(phi, theta, gaz, yaw)

	counter +=1

print ("Journey Complete!" if finishedFlag else "Time Up!")
if realFlag:
	control.land()
