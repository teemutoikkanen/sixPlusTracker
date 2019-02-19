from hud import hudWindow
import tracker
import threading
from testing import testPlayersDb
from time import sleep
import re
from datetime import datetime




threadInfo = []
threads = []
currentTables = []


def getTime():
    return str(datetime.now().strftime('%H:%M:%S'))

def worker(sn,table):
    ''' jokainen threadi päivittää t ajan välein sn avulla statsit '''

    # initsc:\Users\Teemu\Desktop\pythonScripts\sixPlusTracker\hud.py
    hud = hudWindow(sn,table)
    hud.wm_attributes("-topmost", 1)
    hud.attributes('-alpha', 0.7)
    hud.configure(background='black')
    hud.after(500, hud.updateData)
    hud.mainloop()
    # todo after() metodilla päivitys
    return

def newTable(table, currentTables):
    for currentTable in currentTables:
        if (currentTable['name'] == table['name']):
            return False
    return True


def newPlayerJoined(oldTable, table):
    for sn in table['screenNames']:
        if (sn not in oldTable['screenNames']):
            return sn


def startHudThread(sn, table):


    threadInfo.append((sn, table["name"]))

    # print(getTime()+ " starting a new thread for: ", sn, ", " + tn)
    t = threading.Thread(target=worker, args=(sn,table))
    threads.append(t)
    t.start()


def startHud(testing = None):
    ''' keep track of current players -- if new, spawn a hud '''

    while(True):

        newTables = tracker.importNewHands()
        for table in newTables:
            # if the table is new, spawn all huds
            if (newTable(table, currentTables)):
                currentTables.append(table)

                for sn in table['screenNames']:
                    print(getTime() + " New Table, spawning all HUDS.  SN: " + sn + " TN: " + table['name'] )
                    startHudThread(sn, table)

            # if the table isnt new, check if players changed
            else:
                for i in range(len(currentTables)):
                    if (currentTables[i]['name'] == table['name']):
                        newPlayerSn = newPlayerJoined(currentTables[i], table)
                        if (newPlayerSn):
                            # spawn a hud

                            #cmdlog
                            print(getTime() + " Old table, new player.  SN: " + newPlayerSn + " TN: " + table['name'] )
                            startHudThread(newPlayerSn, table)
                        currentTables[i] = table
        # sleep(5)


if __name__ == '__main__':
    startHud()

    
    # topregs = ['Zapahzamazki', 'teo96', 'Zihuatanejo3', 'DEDTAWIWASA', 'gaiggibeliin']
    # table = {
    #     'name' : 'Pertin Pelit IV',
    #     'screenNames' : ['Zapahzamazki', 'teo96', 'Zihuatanejo3', 'DEDTAWIWASA', 'gaiggibeliin'],
    #     'seatNumbers' : [1,3,4,5,6]
    # }

    

    # for sn in topregs:
    #     startHudThread(sn, table)


    