import requests
import json
import time
import os
import logging
import sqlite3

logging.basicConfig(filename='TriPi.log',level=logging.DEBUG)

#os.system("ping -c 10 -i 1 127.0.0.1")

def redLine():
	logging.debug('Red Line')

def blueLine():
	logging.debug('Blue Line')

def greenLine():
	logging.debug('Green Line')

def errorStatus():
	logging.debug('Network Error')

trainColor = {	90 : redLine,
		100 : blueLine,
		200 : greenLine,
}

def checkInternet():
	logging.debug('Check Internet')
	pingstatus = 1
	while pingstatus != 0:
		pingstatus = os.system("ping -c 1 -i 1 trimet.org")
		if pingstatus != 0:	
			errorStatus()

def loadStops():
        stopNumbers = []
        stopsFile = open("stopnumbers","r")
        for line in stopsFile:
            line = line[:-1]
            stopNumbers.append(line)
        return stopNumbers

def queryTrimet(logidsString):
        trimetReply = requests.get('https://developer.trimet.org/ws/v2/arrivals?appid=755E5C1798BEC31002A57468D&locids='+locidsString+'&arrivals=1&json=true')
        trimetJSON = json.loads(trimetReply.text)
        #print trimetJSON
        return trimetJSON   

def updateLEDTable(trimetJSON,ledTable,ledTableConnector):
    curTime = time.time()
    ledOnTime = curTime+120
    ledBlinkTime = curTime+240
    ledOffTime = curTime+300
    

    for train in trimetJSON['resultSet']['arrival']:
        if train['status'] == 'estimated':
            if(train['estimated']/1000 > ledOnTime):
                    ledStatus='on'
            elif(train['estimated']/1000 > ledBlinkTime):
                    ledStatus='blink'
            else:
                    ledStatus='off'
        else:
            if(train['scheduled']/1000 > ledOnTime):
                    ledStatus='on'
            elif(train['scheduled']/1000 > ledBlinkTime):
                    ledStatus='blink'
            else:
                    ledStatus='off'
        line = train['route']
        locid = train['locid']

        #if locid not in ledTable:
        #    ledTable[locid]={line:ledResult}
        #else:
        #    if line not in ledTable[locid]:
        #        ledTable[locid]={line:ledResult}
        print(line,locid)
                
def initializeDatabase():
    ledTable = sqlite3.connect(':memory:')
    return ledTable

def connectToDatabase(ledTable):    
    dbCursor = ledTable.cursor()
    dbCursor.execute('''CREATE TABLE ledTable(stop TEXT, line TEXT, ledState TEXT, time TEXT)''')
    ledTable.commit()

def newRecord(ledTable, ledTableConnector, ledStatus, line, locid, curTime):
    ledTableConnector.execute('''INSERT INTO ledTable(stop, line, ledState, time) VALUES(?,?,?,?)''', (locid, line, ledStatus, time))
    ledTable.commit()



apiCounter = 0
logging.debug('Starting Program')
#checkInternet()
stopNumbers = loadStops()
ledTable = initializeDatabase()
ledTableConnector = connectToDatabase(ledTable)

stopListPointer = 0
while 1:
    
    stopsToUpdate = stopNumbers[stopListPointer:stopListPointer+10]
    if len(stopNumbers) < stopListPointer:
        stopListPointer = 0
    else:
        stopListPointer += 10
        locidsString = ""
        for stop in stopsToUpdate:
            locidsString += stop +","
        locidsString = locidsString[:-1]
        updateLEDTable(queryTrimet(locidsString),ledTable,ledTableConnector)
        time.sleep(15)


if 1 == 0:
    while 1:


	if apiCounter == 0:
		
	
		#time.sleep(60)
		logging.debug('Getting Data from TriMet...')
		try:
			checkInternet()
			reply = requests.get('https://developer.trimet.org/ws/v2/arrivals?appid=755E5C1798BEC31002A57468D&locids=8375&arrivals=1&json=true')
			sched = json.loads(reply.text)
			currtime = time.time()
			tooearly = currtime+300
			toolate = currtime+600
			apiCounter = 60


			trainTable = []
			for train in sched['resultSet']['arrival']:
				if train['status'] == 'estimated':
					if (train['estimated']/1000) > tooearly and (train['estimated']/1000) < toolate:
						#trainColor[train['route']]()
						routenum = train['route']
						trainTable.append([routenum,'est','on'])
				else:
					if (train['scheduled']/1000) > tooearly and (train['scheduled']/1000) < toolate:
						routenum = train['route']
						trainTable.append([routenum,'sched','on'])
		
			for color in trainTable:
				if color[1] == 'est':
					trainColor[color[0]]()
				else:
					if color[2] == 'on':
						trainColor[color[0]]()
						color[2] = 'off'
					else:
						color[2] = 'on'
			#print 'Next: {table} - new data in {nextcall} second(s).'.format(table = trainTable, nextcall = apiCounter)
		except:
			checkInternet()

	apiCounter -= 1
	time.sleep(1)


#
#
#
#
#
#
#
#
#
#
#
#
#
#

