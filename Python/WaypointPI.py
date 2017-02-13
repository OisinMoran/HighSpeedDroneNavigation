## =========================== ##
##      Waypoint Tracking      ##
## =========================== ##

import math
import cmath
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
KPphi = 0.0001
KPtheta = (-1.2)*KPphi
KPgaz = 0.001
# Define Integral Gains
KIphi = 0
KItheta = (-1.2)*KIphi
KIgaz = 0

# SETUP
# Ensure drone is flat on ground
util.flatTrim()
# Ensure drone is aligned with y-axis facing in the increasing y direction
refYaw = sensors.getOrientation("YAW")
 
if realFlag:
	control.takeOff()
	#util.calibrateMagnetometer()
	time.sleep(10)

# Initialise error integrals
errX_integ = 0
errY_integ = 0
errAlt_integ = 0
# First waypoint (waypoint counter)
n = 0
# Time limit for testing
counter = 0
while not finishedFlag and counter < 2000: # This condition will become the Waypoint Reached condition
	time.sleep(0.01)
	print(counter)
	# SENSOR READING
	# Read current yaw from drone
	curYaw = sensors.getOrientation("YAW")
	# Read current height from drone
	curAlt = 1000*sensors.getAltitude()
	# Read current location
	with open("C:\Python34\PozyxData.txt","r") as f:
		f_data = f.read()
	try:
		curPos = [float(i) for i in f_data.split(" ")]
	except:
		print("READING ERROR")
	print("Current position:\t {},{},{}".format(curPos[0], curPos[1], curAlt))
	print("Waypoint:\t\t {}".format(waypointList[n]))

	# Calculate the drone's offset angle from the reference
	errYaw = math.radians(refYaw - curYaw)

	# Define the complex number i
	i = complex(0,1)
	# Current waypoint position on complex plane
	P = complex(waypointList[n][0], waypointList[n][1])
	print("errYaw: \t\t{:.2f}".format(errYaw))
	print("WP: \t\t{:.2f} {:.2f}".format(P.real, P.imag))
	# New imagined waypoint position P_prime found by rotation
	P_prime = P*cmath.exp(i*errYaw)
	print("WP(rotated): \t{:.2f} {:.2f}".format(P_prime.real, P_prime.imag))
	x = P_prime.real
	y = P_prime.imag

	# Calculate error between drones current position and current rotated waypoint
	errPos = [x - curPos[0], y - curPos[1]]
	errAlt = waypointList[n][2]-curAlt
	print("Error:\t\t {},{},{}".format(errPos[0], errPos[1], errAlt))

	# Upate integral of errors
	errX_integ += errPos[0]
	errY_integ += errPos[1]
	errAlt_integ += errAlt

	# CONTROL
	# If waypoint is reached
	# Currently just 2D error, 3D would be: (maybe abstract to function for readability)
	# if math.hypot(math.hypot(errPos[0], errPos[1]), errAlt) < waypoint_tolerance:
	if math.hypot(errPos[0], errPos[1]) < waypoint_tolerance:
		control.hover()
		# Wait for 5 seconds at the waypoint
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
		# No Yaw control
		yaw = 0

		# Roll
		phi = limit(KPphi*errPos[0] + KIphi*errX_integ)
		print("Left" if phi < 0 else "Right")

		# Pitch
		theta = limit(KPtheta*errPos[1] + KItheta*errY_integ)
		print("Forward" if theta < 0 else "Backward")

		# Vertical Speed
		gaz = limit(KPgaz*errAlt + KIgaz*errAlt_integ)
		print("Down" if gaz < 0 else "Up")

		if realFlag:
			control.move(phi, theta, gaz, yaw)

	counter +=1

print ("Journey Complete!" if finishedFlag else "Time Up!")
if realFlag:
	control.land()