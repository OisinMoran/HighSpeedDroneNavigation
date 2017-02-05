import serial
import time
ser1 = serial.Serial('COM6', 115200, timeout=0)
 
while 1:
    try:
        time.sleep(0.1)
        line = ser1.readline().decode("utf-8")
        #print(line)
        if "POS," in line:
            newline = line.split(",")
            print(newline[2:5])
            try:
                
                text_file = open("PozyxData.txt","w")
                text_file.write("%d %d %d" % (int(newline[2]),int(newline[3]),int(newline[4])))
                text_file.close()
            except:
                pass
            
            
        
    except ser1.SerialTimeoutException:
        print('Data could not be read')
        ##time.sleep(0.5)
