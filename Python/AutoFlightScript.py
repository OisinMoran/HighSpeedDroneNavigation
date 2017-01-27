import time

while True:
	try:
		f = open("C:\Python34\PozyxData.txt","r")
		print(f.read())
		time.sleep(0.5)
	except:
		pass