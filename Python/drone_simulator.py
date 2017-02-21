## Author: Rodrigo H. Ordonez-Hurtado
## Date: February 17th, 2017.

import pylab
from pylab import *
import cmath
import math
import random

noisePower = 0.1

flagVerbose = True
flagDummy = False
maxHorSpeed = 500 # mm/s
maxYawSpeed = 45 # deg/s

dTime = 0.5

xAchse = 50
yAchse = 50

fig = pylab.figure(1)
ax = fig.add_subplot(111)
ax.grid(True)
ax.set_title("Realtime Plot (drone's position)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.axis([0,4000,0,4000])
line1=ax.plot(xAchse,yAchse,'o')

manager = pylab.get_current_fig_manager()

values=(0,0)

curXpos = 2000
curYpos = 2000
RefYaw = 0
curYawAng = 45

## Set point coordinates
spXpos = [500,3500]
spYpos = [3500,500]


ControlReadings_file = "ControlData.txt"

xMin = 0
xMax = 4000.0
yMin = 0
yMax = 4000.0

i = complex(0,1)

def SinwaveformGenerator(arg):
  global values, curXpos, curYpos, curYawAng, spXpos, spYpos

  if flagDummy:
    try:
        f = open(ControlReadings_file,"w")
        xPos = 1*random()
        yPos = 1*random()
        if random()>0.5:
            Ang = 20*random()
        else:
            Ang = -20*random()
        
        f.write("%f %f %f" %(xPos,yPos,Ang))
        f.close()
    except:
        pass
  
  try:
      f = open(ControlReadings_file,"r")
      f_data = f.read()
      f.close()
      curData = f_data.split(" ")
      yawNoise = noisePower*random.gauss(0, 1)  
      curYawAng += -(float(curData[2]) + yawNoise)*maxYawSpeed*dTime 
        
      dX = float(curData[0])*maxHorSpeed*dTime
      dY = -float(curData[1])*maxHorSpeed*dTime
      
      dXY = complex(dX,dY)
      dXYRot = dXY*exp(i*math.radians(curYawAng-RefYaw))
      
      curXpos += dXYRot.real
      curYpos += dXYRot.imag

      if flagVerbose:
        print("CONTROL (x,y,yaw): ", curData)
        print("POSITION (x,y,yaw): {},{},{}".format(curXpos,curYpos,curYawAng))
      
  except:
      pass
      
  plotX = [curXpos] + spXpos
  plotY = [curYpos] + spYpos
  values = (plotX,plotY)

  PositionFile = "PositionData.txt"
  filePosition_data = open(PositionFile,"w")
  filePosition_data.write("{} {} {}".format(curXpos,curYpos,curYawAng))
  
def RealtimePloter(arg):
  global values
  CurrentXAxis=values[0]
  CurrentYAxis=values[1]
  line1[0].set_data(CurrentXAxis,CurrentYAxis)
  ax.axis([xMin,xMax,yMin,yMax])
  manager.canvas.draw()
  #manager.show()

timer = fig.canvas.new_timer(interval=200)
timer.add_callback(RealtimePloter, ())
timer2 = fig.canvas.new_timer(interval=200)
timer2.add_callback(SinwaveformGenerator, ())
timer.start()
timer2.start()

pylab.show()

