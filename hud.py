import tkinter
from tkinter import messagebox
import tracker
import threading
# from spawnThreadedHuds import startHudThread


# dragable boarderless window
# ref. https://stackoverflow.com/questions/29641616/drag-window-when-using-overrideredirect
class hudWindow(tkinter.Tk):

    def __init__(self, sn, master=None):
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

        # right click close
        self.bind("<Button-2>", self.quit)

    def dataToStr(self, data):
        # return data['sn'][:5] + "("+ str(data['nHands']) + ")\n ol: " + data['openLimp'] + " r: " + data['rfi']
        return data['sn'][:5] + "("+ str(data['nHands']) + ")\n" + str(data['vpip']) + " | " + data['openLimp'] + "/" + data['rfi']
    
    def quit(self, n):
        self.destroy()

    def dragwin(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry('+{x}+{y}'.format(x=x, y=y))

    def clickwin(self, event):
        self._offsetx = event.x
        self._offsety = event.y


    def getHoleCardLines(self, event):
        
        '''
        data = {
            'preflopLine' : preflopLine
            'pos' : pos
            'holeCards' : holeCards }  
        '''
        
        posList = ['BTN', 'CO', 'HJ', 'LJ', 'MP', 'UG']
        sortOrder = {}
        for i in range(len(posList)):
            sortOrder[posList[i]] = i
        str1 = ''
        holeCardLinesSortedByHands = sorted(self.holeCardLines, key=lambda k: k['holeCards'])
        if (len(self.holeCardLines) > 0):
            for data in sorted(holeCardLinesSortedByHands, key=lambda i:sortOrder[i['pos']]):
                # str1 += "  [" + line + "]"
                str1 += data['pos'] + " " + data['holeCards'] + ": " + data['preflopLine'] + "\n"
        messagebox.showinfo("lines", str1)



    
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
            lbl = tkinter.Label(self, text=parsedData, fg="white", bg="black")
            lbl.grid(column=0, row=0)

            # update holeCardLines
            self.holeCardLines = holeCardLines
            

            # #pop-up for holeCardLines
            # btn = tkinter.Button(self, text ="lines", command=self.btnCallBack(holeCardLines))
            # btn.pack()

        #get new data ater t ms
        t = 5000
        self.after(t, self.updateData)


# if __name__ == '__main__':
#     sn = 'gaiggibeliin'
#     x,y = (0,0)
#     print("starting a new thread for: ", sn)
#     t = threading.Thread(target=worker, args=(sn,x,y))
#     threads.append(t)
#     t.start()
