## =========================== ##
##      Waypoint Tracking      ##
## =========================== ##

import math, time

# Function to limit arguments to the move command to the range [-1,1]
def limit(x):
	if abs(x) <= 1:
		return x
	else:
		return math.copysign(1, x)

# List of x,y,z tuples representing waypoints
waypointList = [(1000,1000,1000), (1000,1000,2000)]
curPos = (0,0,0)

# Define Proportional Gains
KPyaw = (-1)/(math.pi)
KPphi = 0.001
KPtheta = (-1)*KPphi
KPgaz = 0.001

# SETUP
# Ensure drone is flat on ground
util.flatTrim()
# Ensure drone is aligned with y-axis facing in the increasing y direction
refYaw = sensors.getOrientation("YAW")

control.takeOff()
# time.sleep(5)

# First waypoint
n = 0

counter = 0
while counter < 100: # This condition will become the Waypoint Reached condition
	print(counter)
	# SENSOR READING
	# Read current location
	with open("C:\Python34\PozyxData.txt","r") as f:
		f_data = f.read()
	# Read current yaw
	curYaw = sensors.getOrientation("YAW")
	curPos = tuple([float(i) for i in f_data.split(" ")])
	print("Current position:\t {}".format(curPos))
	print("Waypoint:\t\t {}".format(waypointList[n]))

	# Calculate error between drones current position and current waypoint
	errPos = tuple([i - j for i, j in zip(waypointList[n], curPos)])
	errYaw = math.radians(refYaw - curYaw)
	print("Error:\t\t {}".format(errPos))

	# CONTROL
	# Yaw
	yaw = KPyaw*(math.atan2(math.sin(errYaw), math.cos(errYaw)))
	print("Counterclockwise" if yaw < 0 else "Clockwise")

	# Roll
	phi = limit(KPphi*errPos[0])
	print("Left" if phi < 0 else "Right")

	# Pitch
	theta = limit(KPtheta*errPos[1])
	print("Forward" if theta < 0 else "Backward")

	# Vertical Speed
	gaz = limit(KPgaz*errPos[2])
	print("Down" if gaz < 0 else "Up")

	control.move(phi, theta, gaz, yaw)
	counter +=1

control.land()
