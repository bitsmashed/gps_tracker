#
#	Python GPS Tracking Example
#	SparkFun Electronics, A.Weiss
#	Beerware: if you use this and meet me, you must buy me a beer
#	
#	Function:
#	Takes GPS position and altitude data and plots it on a scaled map image of your
#	choice. Altitude can also be displayed in a separate graph. 
#	
#	The program has a console menu that allows you to configure your connection. 
#	The program will run with either a GPS moudle connected or no moudle connected.
#	If a GPS is connected, the position and altitude data is automatically saved
#	to a file called nmea.txt. If no GPS is connected, you must create your own
#	nmea.txt and fill it with GPGGA NMEA sentences. 
#	A map needs to be created and saved as a file called map.png. When you create
#	your map, note the lat and long of the bottom left and top right corner, in decimal 
#	degrees. Then enter this information into the global variables below. This way, 
#	your the border of your map image can be used as the graph mins and maxs.
#	Once you have a map loaded and a GPS connected, you can run the program and select
#	either your position to be displayed on your map, or display altitude on a separate
#	graph. The maps are not updated in realtime, so you must close the map and run 
#	the map command again in order to read new data. 

from pynmea import nmea
import matplotlib.pyplot as plt
import serial, time, sys, threading, datetime, shutil

######Global Variables#####################################################
# you must declare the variables as 'global' in the fxn before using#
ser = 0
lat = 0
long = 0
pos_x = 0
pos_y = 0
alt = 0
i = 0 #x units for altitude measurment

#adjust these values based on your location and map, lat and long are in decimal degrees
TRX = -105.1621          #top right longitude
TRY = 40.0868            #top right latitude
BLX = -105.2898          #bottom left longitude
BLY = 40.001             #bottom left latitude
BAUDRATE = 4800
lat_input = 0            #latitude of home marker
long_input = 0           #longitude of home marker

######FUNCTIONS############################################################ 
def altitude():
	global alt, i
	
	#we want to create temporary file to parse, so that we don't mess with the nmea.txt file
	f1 = open('temp.txt', 'w') #creates and opens a writable txt file
	f1.truncate() #erase contents of file
	shutil.copyfile('nmea.txt', 'temp.txt') #copy nmea.txt to temp.txt
	f1.close() #close writable file
	
	f1 = open('temp.txt', 'r') #open and read only
	try: #best to use try/finally so that the file opens and closes correctly
		for line in f1: #read each line in temp.txt
			if(line[4] == 'G'): # fifth character in $GPGGA
				if(len(line) > 50): # when there is a lock, the sentence gets filled with data
					#print line
					gpgga = nmea.GPGGA()
					gpgga.parse(line)
					alt = gpgga.antenna_altitude
					i +=1 #increment the counter
					print i
					print alt
					plt.scatter(x=[i], y=[float(alt)], s = 1, c='r') #plot each point
	finally:
		f1.close()
	i=0
	
	#axis is autoscaled
	plt.ylabel('meters')
	plt.xlabel('counts')
	plt.title('ALTITUDE')
	plt.show()

def check_serial():
	print 'Do you have a GPS connected to the serial port? hit y or n, then enter'
	temp = raw_input()
	if temp == 'y':
		init_serial()
	if temp == 'n':
		print 'You can enter your own NMEA sentences into a file named nmea.txt'
	
def init_serial():
	#opens the serial port based on the COM number you choose
	print "Found Ports:"
	for n,s in scan():
		print "%s" % s
	print " "

	#enter your COM port number
	print "Choose a COM port #. Enter # only, then enter"
	temp = raw_input() #waits here for keyboard input
	if temp == 'e':
		sys.exit()
	comnum = 'COM' + temp #concatenate COM and the port number to define serial port

	# configure the serial connections 
	global ser, BAUDRATE
	ser = serial.Serial()
	ser.baudrate = BAUDRATE
	ser.port = comnum
	ser.timeout = 1
	ser.open()
	ser.isOpen()
	
	#Prints menu and asks for input
	global lat_input, long_input

	print 'OPEN: '+ ser.name
	print ''
	
	#can be used to enter positions through the user interface
	#print 'enter your home position'
	#print '4001.54351'
	#print 'Lat<' 
	#plat = raw_input()
	#lat_input = float(plat)
	#print '-10517.3005'
	#print 'Long<' 
	#plong = raw_input()
	#long_input = float(plong)
	
	thread()

def position():
	#opens a the saved txt file, parses for lat and long, displays on map
	global lat, long, lat_input, long_input, pos_x, pos_y, altitude
	global BLX, BLY, TRX, TRY
	
	#same process here as in altitude
	f1 = open('temp.txt', 'w')
	f1.truncate() 
	shutil.copyfile('nmea.txt', 'temp.txt')
	f1.close()
	
	f1 = open('temp.txt', 'r') #open and read only
	try:
		for line in f1:
			if(line[4] == 'G'): # $GPGGA
				if(len(line) > 50):
					#print line
					gpgga = nmea.GPGGA()
					gpgga.parse(line)
					lats = gpgga.latitude
					longs = gpgga.longitude
					
					#convert degrees,decimal minutes to decimal degrees 
					lat1 = (float(lats[2]+lats[3]+lats[4]+lats[5]+lats[6]+lats[7]+lats[8]))/60
					lat = (float(lats[0]+lats[1])+lat1)
					long1 = (float(longs[3]+longs[4]+longs[5]+longs[6]+longs[7]+longs[8]+longs[9]))/60
					long = (float(longs[0]+longs[1]+longs[2])+long1)
					
					#calc position
					pos_y = lat
					pos_x = -long #longitude is negaitve
					
					#plot the x and y positions
					plt.scatter(x=[pos_x], y=[pos_y], s = 5, c='r')

					#shows that we are reading through this loop
					print pos_x
					print pos_y
	finally:
		f1.close()
		
	#now plot the data on a graph
	#plt.scatter(x=[long_input], y=[lat_input], s = 45, c='b') #sets your home position
	plt.xlabel('Longitude')
	plt.ylabel('Latitude')
	plt.title('POSITION (in Decimal Degrees)')
	
	#lay the image under the graph
	#read a png file to map on
	im = plt.imread('map.png')
	implot = plt.imshow(im,extent=[BLX, TRX, BLY, TRY])
	
	plt.show()

def save_raw():
	#this fxn creates a txt file and saves only GPGGA sentences
	while 1:
		line = ser.readline()
		line_str = str(line)
		if(line_str[4] == 'G'): # $GPGGA
			if(len(line_str) > 50): 
				# open txt file and log data
				f = open('nmea.txt', 'a')
				try:
					f.write('{0:}'.format(line_str))
				finally:
					f.close()
			else:
				stream_serial()

def scan():
    #scan for available ports. return a list of tuples (num, name)
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.name))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available  

def stream_serial():
    #stream data directly from the serial port
    line = ser.readline()
    line_str = str(line)    
    print line_str

def thread():
	#threads - run idependent of main loop
	thread1 = threading.Thread(target = save_raw) #saves the raw GPS data over serial while the main program runs
	#thread2 = threading.Thread(target = user_input) #optional second thread
	thread1.start()
	#thread2.start()

def user_input():
	#runs in main loop looking for user commands
	print 'hit a for altitude map'
	print 'hit p for position map'
	print 'hit e to exit'
	tester = raw_input()
	if tester == 'a':
		altitude()
	if tester == 'p':
		position()
	if tester == 'e':
		sys.exit()
		
########START#####################################################################################
check_serial()

#main program loop
while 1:
	user_input() # the main program waits for user input the entire time
ser.close()
#sys.exit()
