#!/usr/bin/env python
import time
import json
from urllib2 import urlopen
import RPi.GPIO as GPIO

#Set up GPIO 
GPIO.setmode(GPIO.BCM)
REDT = 2
GREENT = 3
YELLOWT = 4
REDP = 5
GREENP = 6
YELLOWP = 17
GPIO.setup(GREENT, GPIO.OUT)
GPIO.setup(YELLOWT, GPIO.OUT)
GPIO.setup(REDT, GPIO.OUT)
GPIO.setup(GREENP, GPIO.OUT)
GPIO.setup(YELLOWP, GPIO.OUT)
GPIO.setup(REDP, GPIO.OUT)
GPIO.output(GREENT, False)
GPIO.output(YELLOWT, False)
GPIO.output(REDT, False)
GPIO.output(GREENP, False)
GPIO.output(YELLOWP, False)
GPIO.output(REDP, False)


# other constants
OBJMAX = 3                         	# set max hours/pop to average
TIME_BETWEEN_CALLS = 900            	# seconds between calls to the weather api
TIME_BETWEEN_FAILED = 300           	# seconds between failed calls to the weather api
MAX_FAIL_LOOP_COUNT = 15            	# maximum number of attempts from API before program terminates
API = 					#Weather Underground api key (obtain from weather underground)
STATE = "CO//Denver"			#State Params 
MAXLOOP = 450				#max loop for flashing lights 

def parseWeatherData(obj):
    # parse data obtained from the weather api
    temp = [None]*OBJMAX
    pop = [None]*OBJMAX
    counterT =0      			# counter for temp
    counterP =0      			# coutner for pop
    
    for i in range(OBJMAX):
        temp[i] = int(obj["hourly_forecast"][i]["temp"]["english"])
        pop[i] = int(obj["hourly_forecast"][i]["pop"])
        counterT +=temp[i]
        counterP +=pop[i]
	print temp[i] 
	print pop[i] 
	#calculate average
    averageT=counterT / OBJMAX
    averageP=counterP / OBJMAX
    obj = lightcolortemp(averageT)
    obj = lightcolorpop(averageT)  

    print ("average temp " , averageT)
    print ("average pop " , averageP) 

    return temp, pop

def lightcolortemp(averageT):
    print averageT
    if averageT > 50:
        GPIO.output(GREENT, True)
        print "Weather is Green"
    elif 33 <= averageT <= 50: 
        GPIO.output(YELLOWT, True)
        print "Weather is Yellow"
    elif averageT < 32:
        GPIO.output(REDT, True)
        print "Weather is Red"

def lightcolorpop(averageP):
    print averageP
    if averageP < 40:
		for i in range(MAXLOOP):
			GPIO.output(GREENP, True)
			time.sleep(1)
			GPIO.output(GREENP, False)
			time.sleep(1)
			print "POP is Green"
    elif 40 <= averageP <= 75: 
		for i in range(MAXLOOP):
			GPIO.output(YELLOWP, True)
			time.sleep(1)
			GPIO.output(YELLOWP, False)
			time.sleep(1)
			print "POP is Yellow"
    elif averageP > 75:
		for i in range(MAXLOOP):
			GPIO.output(REDP, True)
			time.sleep(1)
			GPIO.output(REDP, False)
			time.sleep(1)
			print "POP is Red"
    
def fetchWeatherData():
    success = False
    failedLoopCount = 0
    error = 'foo'
	#http://api.wunderground.com/api/d07b0d9e76f1bcfc/hourly/q/CO//Denver.json
    apiUrl = "http://api.wunderground.com/api/" + API + "/hourly/q/" + STATE + ".json"
    
    try:
        # attempt to fetch weather data
        response = urlopen(apiUrl).read().decode('utf8')
        obj = json.loads(response)
        success = True
    except:
        # utilize yellow color wipe to signal error and increment failed loop count
        success = False
        failedLoopCount += 1
        print('\n\nFailed to connect to API after attempt ' + str(failedLoopCount) + '.', 'a')
        print('\nProgram will terminate after ' + str(MAX_FAIL_LOOP_COUNT) + ' consecutive attempts.', 'a')
        print('\nTrying again in ' + str(TIME_BETWEEN_FAILED) + ' seconds.', 'a')
           

    if success == True:
        try:
            # verify that API returned no errors    
            error = str(obj["response"]["error"]["type"])
        except:
            success = True
        else:
            print('\n\nReceived an error response from the API: ' + error + '. Terminating program.','a')
            raise SystemExit('some error from api')
              

        if failedLoopCount > MAX_FAIL_LOOP_COUNT:
            print('\n\nTerminating program after ' + str(MAX_FAIL_LOOP_COUNT) + ' attempts to retrieve data from API.','a')
            raise SystemExit('failed to retrieve data after multiple attempts')
            
        if success == False:
            time.sleep(TIME_BETWEEN_FAILED)
            
    return(obj)

def main():
    isOn=True
    print('-----Demonstrate Stop Light-----')

    while isOn:
        try:
            print('-----Attempting to Fetch Data-----')
            obj = fetchWeatherData()
            print('\n\n' + str(obj),'a')
            
            # call function to parse weather data
            print('\n\n-----Parsing-----', 'a')
            tempData = parseWeatherData(obj)

          
            # display weather data
            print('\n\n-----Results-----', 'a')
            print('\n\nTemperature Data: ' +  str(tempData) + '\nTemperature Color: ' + 'a')
         
            # use the sleep function as a delay to save cpu cycles when counting elapsed time 
            time.sleep(TIME_BETWEEN_CALLS)
        except KeyboardInterrupt:
                GPIO.cleanup()

main()
