from hud import hudWindow
import tracker
import threading
from testing import testPlayersDb
from time import sleep
import pywinauto
import win32gui
import re
from datetime import datetime




threadInfo = []
threads = []
currentTables = []


def getTime():
    return str(datetime.now().strftime('%H:%M:%S'))

def worker(sn, x, y):
    ''' jokainen threadi päivittää t ajan välein sn avulla statsit '''

    # inits
    hud = hudWindow(sn)
    hud.wm_attributes("-topmost", 1)
    hud.configure(background='black')
    hud.geometry('65x30+'+str(x)+'+'+str(y))

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


def getWindowPos(tn):
    handle = pywinauto.findwindows.find_windows(title_re=tn)[0]
    rect = win32gui.GetWindowRect(handle)
    x = rect[0]
    y = rect[1]
    return (x, y)


def startHudThread(sn, tn):

    threadInfo.append((sn, tn))
    x, y = (0, 0)
    try:
        x, y = getWindowPos(tn)
    except Exception as e:
        print(e)
        print("startingHudThread get x,y error")
    # print(getTime()+ " starting a new thread for: ", sn, ", " + tn)
    t = threading.Thread(target=worker, args=(sn, x, y))
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
                    startHudThread(sn, table['name'])

            # if the table isnt new, check if players changed
            else:
                for i in range(len(currentTables)):
                    if (currentTables[i]['name'] == table['name']):
                        newPlayerSn = newPlayerJoined(currentTables[i], table)
                        if (newPlayerSn):
                            # spawn a hud
                            print(getTime() + " Old table new player.  SN: " + newPlayerSn + " TN: " + table['name'] )
                            startHudThread(newPlayerSn, table['name'])
                        currentTables[i] = table

                            

            # # update players in a table (only if table wasnt new and appended to currenttables ???)
            # for i in range(len(currentTables)):
            #     if (currentTables[i]["name"] == table['name']):
            #         del currentTables[i]
            #         break
            # currentTables.append(table)

        # newPlayers = ['dealo', 'gaiggibeliin', 'sarah1174']
        # for sn in newPlayers:
        #     if (sn not in currentPlayers):
        #         currentPlayers.append(sn)
        #         t = threading.Thread(target=worker, args=(sn,))
        #         threads.append(t)
        #         t.start()

        # if (newTables):
        #     print("new")
        #     print(str(newTables))
        #     print("\ncurrent")
        #     print(str(currentTables))
        #     print("------")
        # print(str(threadInfo))
        sleep(5)


if __name__ == '__main__':
    startHud()

    # startHudThread('teo96', 'Pertin Pelit IV')

    # pos = getWindowPos('Alkimos')
    # print(pos)

    