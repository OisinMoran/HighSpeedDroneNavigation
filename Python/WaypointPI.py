## =========================== ##
##      Waypoint Tracking      ##
## =========================== ##

import math, cmath
import time
import random

# define complex number i
i = complex(0,1)

# Function to limit arguments to the move command to the range [-1,1]
def limit(x):
	if abs(x) <= 1:
		return x
	else:
		import math
		return math.copysign(1, x)

# List of x,y,z tuples representing waypoints
waypointList = [[2000,1500,1000],[3750,2000,1000],[2500,3500,1000]]
random.shuffle(waypointList)

numWaypoints = len(waypointList)
# How close in mm do we need to get to the waypoint
waypoint_tolerance = 250

curPos = (0,0,0)

realFlag = True
finishedFlag = False
flagYawFail = False

# Define Proportional Gains
KPphi = 0.0002
KPtheta = (-1.0)*KPphi
KPgaz = 0.001
# Define Integral Gains
KIphi = 0.00000005
KItheta = (-1.0)*KIphi
KIgaz = 0

# SETUP
# Ensure drone is flat on ground
util.flatTrim()
# Ensure drone is aligned with y-axis facing in the increasing y direction
refYaw = sensors.getOrientation("YAW")
time.sleep(2)
 
if realFlag:
	control.takeOff()
	util.calibrateMagnetometer()
	time.sleep(10)
	curYaw = sensors.getOrientation("YAW")
	errYaw = math.radians(refYaw - curYaw)
	if abs(errYaw) > 0.2:
		#control.land()
		#print("YAW FAIL")
		#flagYawFail = True
                time.sleep(5)
                refYaw = sensors.getOrientation("YAW")
                util.calibrateMagnetometer()
                time.sleep(10)
                curYaw = sensors.getOrientation("YAW")
                errYaw = math.radians(refYaw - curYaw)
                if abs(errYaw) > 0.2:
                    control.land()
                    print("YAW FAIL")
                    flagYawFail = True
                

# Initialise error integrals
errX_integ = 0
errY_integ = 0
errAlt_integ = 0
# Initialise error
errPos = [0,0,0]
# First waypoint (waypoint counter)
n = 0
t = time.time()
# Time limit for testing
counter = 0
while not finishedFlag and counter < 3000 and not flagYawFail: # This condition will become the Waypoint Reached condition
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
	ts = time.time() - t
	t = time.time()
	print("ts: {}".format(ts))
	print("Current position:\t {},{},{}".format(curPos[0], curPos[1], curAlt))
	print("Waypoint:\t\t {}".format(waypointList[n]))

	prev_errPos = errPos
	# Calculate error between drones current position and current waypoint
	errPos = [i - j for i, j in zip(waypointList[n], curPos)]
	errYaw = math.radians(refYaw - curYaw)
	errAlt = waypointList[n][2]-curAlt
	print("Error:\t\t {},{},{}".format(errPos[0], errPos[1], errAlt))

	# Current position on complex plane
	W_o = complex(errPos[0], errPos[1])
	print("errYaw: \t\t{:.2f}".format(errYaw))
	#print("W_o: \t\t{:.2f} {:.2f}".format(P.real, P.imag))

	# New imagined waypoint position P_prime found by rotation
	W_prime = W_o*cmath.exp(i*errYaw)
	#print("W_prime: \t{:.2f} {:.2f}".format(W_prime.real, W_prime.imag))

	# Calculate error between drones current position and current rotated waypoint
	errPos = [W_prime.real, W_prime.imag]
	#errAlt = waypointList[n][2]-curAlt
	print("Error:\t\t {},{},{}".format(errPos[0], errPos[1], errYaw))

	# Upate integral of errors
	errX_integ += ts*(errPos[0] - prev_errPos[0])/2.0
	errY_integ += ts*(errPos[1] - prev_errPos[1])/2.0
	errAlt_integ += errAlt

	# CONTROL
	# If waypoint is reached
	# Currently just 2D error, 3D would be: (maybe abstract to function for readability)
	# if math.hypot(math.hypot(errPos[0], errPos[1]), errAlt) < waypoint_tolerance:
	if math.hypot(errPos[0], errPos[1]) < waypoint_tolerance:
		control.hover()
		# Wait for 3 seconds at the waypoint
		time.sleep(3)
		# If there are no more waypoints we are finished
		if n+1 >= numWaypoints:
			finishedFlag = True
		# Otherwise advance to the next waypoint
		else:
			print("Next Waypoint")
			# Reset error integrals
			errX_integ = 0
			errY_integ = 0
			errAlt_integ = 0
			# Update waypoint counter
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
