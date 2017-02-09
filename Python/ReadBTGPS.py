
import bluetooth
# bluetooth address of the GPS device.
addr = "00:1C:88:22:32:2E"
# port to use.
port = 1
# create a socket and connect to it.
socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
socket.connect((addr, port))

data = ""
olddata = ""

while True:
    print("================================================")
    data = socket.recv(1024)
    #print(data)

    # make sure we actually have some data.
    if len(data) > 0:
        # append the old data to the front of data.
        data = data.decode()
        data = str(olddata) + str(data)

        # split the data into a list of lines, but make
        # sure we preserve the end of line information.
        lines = data.splitlines(1)

        # iterate over each line
        for line in lines:
            # if the line has a carriage return and a
            # linefeed, we know we have a complete line so

            # we can remove those characters and print it.
            if line.find("\\r\\n") != -1:
                line = line.strip()
                print(line.decode())

                # empty the olddata variable now we have
                # used the data.
                olddata = ""
                # else we need to keep the line to add to data
            else:
                olddata = line

            gpsstring = line.split(',')
            if gpsstring[0] == '$GPRMC':
                try:
                    print("Lat: " + gpsstring[3] + gpsstring[4])
                    print("Lon: " + gpsstring[5] + gpsstring[6])
                except:
                    pass
