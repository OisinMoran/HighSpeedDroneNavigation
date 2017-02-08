import serial
import time
import winsound
Freq = 1000
Dur = 100

ser1 = serial.Serial('COM6', 115200, timeout=0)

data_hist = []
N = 3

while 1:
    try:
        time.sleep(0.15)
        line = ser1.readline().decode("utf-8")
        #print(line)
        if "POS," in line:
            newline = line.split(",")
            x = int(newline[2])
            y = int(newline[3])
            z = int(newline[4])

            data_hist.append([x,y,z])
            
            if len(data_hist)>N:

                data_hist.pop(0)
                xAV = sum(list(zip(*data_hist))[0])/(1.0*N)
                yAV = sum(list(zip(*data_hist))[1])/(1.0*N)
                zAV = sum(list(zip(*data_hist))[2])/(1.0*N)
                
                # print("%f %f %f" % (xAV,yAV,zAV))
                try:
                    text_file = open("PozyxData.txt","w")
                    text_file.write("%f %f %f" % (xAV,yAV,zAV))
                    text_file.close()
                except:
                    winsound.Beep(2000,Dur)
                    print(newline)
        else:
            winsound.Beep(1000,Dur)
            print("Error not POS")
            print(line)
            
            
        
    except ser1.SerialTimeoutException:
        print('Data could not be read.')
        ##time.sleep(0.5)
