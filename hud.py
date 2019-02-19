import tkinter
from tkinter import messagebox
import tracker
import threading
import pywinauto
import win32gui
# from spawnThreadedHuds import startHudThread


# dragable boarderless window
# ref. https://stackoverflow.com/questions/29641616/drag-window-when-using-overrideredirect
class hudWindow(tkinter.Tk):

    def __init__(self, sn, table, master=None):
        tkinter.Tk.__init__(self, master)
        self.overrideredirect(True)
        self._offsetx = 0
        self._offsety = 0
        self.bind('<Button-3>', self.clickwin)
        self.bind('<B3-Motion>', self.dragwin)

        #pop up
        self.bind('<Button-1>', self.getHoleCardLines)
        self.holeCardLines = []

        # hud data
        self.sn = sn
        self.table = table

        # right click close
        self.bind("<Button-2>", self.quit)

        #stop auto moving if rightclicked/draged
        self.autoMove = True

    def dataToStr(self, data):
        # return data['sn'][:5] + "("+ str(data['nHands']) + ")\n ol: " + data['openLimp'] + " r: " + data['rfi']
        # return data['sn'][:5] + "("+ str(data['nHands']) + ")\n" + str(data['vpip']) + " | " + data['openLimp'] + "/" + data['rfi']
        return data['sn'][:3] + "("+ str(data['nHands']) + ")\n" + "VPIP "+ str(data['vpip']) + "\nOL " + data['openLimp'] + " R " + data['rfi']

    def quit(self, n):
        self.destroy()

    def dragwin(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry('+{x}+{y}'.format(x=x, y=y))

    def clickwin(self, event):
        self._offsetx = event.x
        self._offsety = event.y

        if (self.autoMove == True):
            self.autoMove = False

    def getHoleCardLines(self, event):
        
        '''
        data = {
            'preflopLine' : preflopLine
            'pos' : pos
            'holeCards' : holeCards }  
        '''
        
        # init TopLevel & Listbox secondary windows
        t = tkinter.Toplevel(self)
        t.wm_title('Holecards & preflop lines')
        listBox = tkinter.Listbox(t, height = 50, width = 30)
        listBox.pack()
        
        posList = ['BTN', 'CO', 'HJ', 'LJ', 'MP', 'UG']
        cardRanks = ['A','K','Q','J','T','9','8','7','6','5','4','3','2']
        sortOrder = {}
        for i in range(len(cardRanks)):
            sortOrder[cardRanks[i]] = i
        str1 = ''
        # holeCardLinesSortedByHands = sorted(self.holeCardLines, key=lambda k: k['holeCards'])
        holeCardLinesSortedByHands = sorted(self.holeCardLines, key=lambda i:sortOrder[i['holeCards'][1]])
        holeCardLinesSortedByHands = sorted(holeCardLinesSortedByHands, key=lambda i:sortOrder[i['holeCards'][0]])
        if (len(self.holeCardLines) > 0):
            # for data in sorted(holeCardLinesSortedByHands, key=lambda i:sortOrder[i['pos']]):
            for data in holeCardLinesSortedByHands:
                # str1 += "  [" + line + "]"
                str2 = data['holeCards'] + ": " + data['preflopLine'] + " [" + data['pos'] + "]" "\n"
                str1 += str2

                #append data to tkinter-listbox object
                listBox.insert(tkinter.END, str2)
        
        # messagebox.showinfo("lines", str1)

        

        


        
        # l = tkinter.Label(t, text=str1)
        # l.pack(side="top", fill="both", expand=True, padx=100, pady=100)




    def getWindowPos(self, tn):
        handle = pywinauto.findwindows.find_windows(title_re=tn)[0]
        rect = win32gui.GetWindowRect(handle)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        
        return (x, y, w, h)

    def getRelativeSeat(self, sn, table):
        hero = 'gaiggibeliin'
        #hero (alin) RELATIVE SEAT olis 1. Myötäpäivään siitä 2,3,4,5,6

        if (sn == hero):
            return 1

        heroSeat = -1
        snSeat = -1

        for i in range(len(table['screenNames'])):
            # get hero seat
            if (table['screenNames'][i] == hero):
                heroSeat = table['seatNumbers'][i]
            # get sn (hud-box) seat
            if (table['screenNames'][i] == sn):
                snSeat = table['seatNumbers'][i]

        
        result = (snSeat-heroSeat) % 6 + 1
        # print("SN & relative seat: ", sn, result)
        return result
            

    def getPositionalCoords(self, seat,x,y,w,h):

        #
        w = 530
        h = 720
        x1 = 200/w
        y1 = 453/h
        x2 = 35/w
        y2 = 330/h
        x3=x2
        y3=180/h
        x4=215/w
        y4=60/h
        x5=620/w
        y5=y3
        x6=x5
        y6=y2

        if (seat == 1):
            x += x1*w
            y += y1*h
            return int(x),int(y)
        if (seat == 2):
            x += x2*w
            y += y2*h
            return int(x),int(y)
        if (seat == 3):
            x += x3*w
            y += y3*h
            return int(x),int(y)
        if (seat == 4):
            x += x4*w
            y += y4*h
            return int(x),int(y)
        if (seat == 5):
            x += x5*w
            y += y5*h
            return int(x),int(y)
        if (seat == 6):
            x += x6*w
            y += y6*h
            return int(x),int(y)

        print("getPositionalCoords seat number ???: ", seat)
        return x,y
    
    def updateData(self):
        # get data
        db = tracker.getDb()
        cursor = db.players.find({'screenName': self.sn})

        hudData = {}

        for playerData in cursor:

            vpip = str(int(playerData['vpipTrue'] / playerData['nHands'] * 100))

            rfi = ''
            try:
                rfi = playerData['rfiTrue'] / \
                    (playerData['rfiTrue'] + playerData['rfiFalse'])
                rfi = str(int(rfi*100))
            except Exception as e:
                # print("hud updadeData rfi error")
                # print(e)
                pass

            openLimp = ''
            try:
                openLimp = playerData['openLimpTrue'] / \
                    (playerData['openLimpTrue'] + playerData['openLimpFalse'])
                openLimp = str(int(openLimp*100))
            except Exception as e:
                # print("hud updadeData openlimp error")
                # print(e)
                pass

            limp = ''
            try:
                limp = playerData['limpTrue'] / \
                    (playerData['limpTrue'] + playerData['limpFalse'])
                limp = str(int(limp*100))
            except Exception as e:
                # print("hud updadeData limp error")
                # print(e)
                pass

            holeCardLines = playerData['holeCardLines']

            hudData = {
                "sn": self.sn,
                "rfi": rfi,
                "limp": limp,
                "openLimp": openLimp,
                "nHands": playerData['nHands'],
                "vpip": vpip,
                "holeCardLines": holeCardLines
            }
            #post hudData to hud
            parsedData = 'error with hud.py parsedData'
            # print("printdata: " + str(data))
            try:
                parsedData = self.dataToStr(hudData)
            except Exception as e:
                print("hud updadeData dataToStr error")
                print(e)
            lbl = tkinter.Label(self, text=parsedData, justify='left',fg="white", bg="black")#.pack(fill='both')
            lbl.grid(column=0, row=0)

            # update holeCardLines
            self.holeCardLines = holeCardLines

            #position
            if (self.autoMove):
                x, y, w, h = (0, 0, 0, 0)
                try:
                    x, y, w, h = self.getWindowPos(self.table['name'])
                except Exception as e:
                    continue
                    # print(e)
                    # print("startingHudThread get x,y error")
                #get relative seat
                relativeSeat = self.getRelativeSeat(self.sn, self.table)
                #calc new coords
                # print(self.sn)
                # print("x,y,w,h", x,y,w,h)
                x,y = self.getPositionalCoords(relativeSeat, x,y,w,h)
                # print("new x,y", x,y)
                try:
                    self.geometry('66x50+'+str(x)+'+'+str(y)) 
                except Exception as e:
                    print(e)
            

        #get new data ater t ms
        t = 5000
        self.after(t, self.updateData)

