from tkinter import *
from tkinter.simpledialog import *
import math, time, sys

###############################
# классы парометров настройки #
###############################

class ClockConfig:
    size = 200
    bg,fg = 'beige','brown'
    hh,mh,sh,cog = 'black','navy','green','red'
    picture = None

class PhotoClockConfig(ClockConfig):
    size = 320
    picture = r'C:\Users\User\Documents\html\"задачник по html и css"\pictures\thumbs'
    bg,hh,mh = 'white','blue','orange'

###############################
# Объект цифрового интерфейса #
###############################

class DigitalDisplay(Frame):
    def __init__(self,parent,cfg):
        Frame.__init__(self,parent)
        self.hour = Label(self)
        self.mins = Label(self)
        self.secs = Label(self)
        self.ampm = Label(self)
        for label in self.hour,self.mins,self.secs,self.ampm:
            label.config(bd = 4,relief = SUNKEN,bg = cfg.bg,fg = cfg.fg)
            label.pack(side = LEFT)
    
    def onUpdate(self,hour,mins,secs,ampm,cfg):
        mins = str(mins).zfill(2) # 01,02 то же что и "%02d" '
        self.hour.config(text = str(hour),width = 4)
        self.mins.config(text = str(mins),width = 4)
        self.secs.config(text = str(secs),width = 4)
        self.ampm.config(text = str(ampm),width = 4)
    
    def onResize(self,newWidth,newHeight,cfg):
        pass # ниче перисовывать не надо

#################################
# Объект аналогового интерфейса #
#################################

class AnalogDisplay(Canvas):
    def __init__(self,parent,cfg):
        Canvas.__init__(self,parent,width = cfg.size,height = cfg.size,bg = cfg.bg)
        self.drawClockface(cfg)
        self.hourHand = self.minsHand = self.secsHand = self.cog = None

    def drawClockface(self,cfg):  
        if cfg.picture:
            try:
                self.image = PhotoImage(file = cfg.picture)
            except:
                self.image = BitmapImage(file = cfg.picture)
            imgx = (cfg.size - self.image.width()) // 2
            imgy = (cfg.size - self.image.height()) // 2
            self.create_image(imgx+1,imgy+1,anchor = NW,image = self.image)
        originX = originY = radius = cfg.size // 2
        for i in range(60):
            x,y = self.point(i,60,radius-6,originX,originY)
            self.create_rectangle(x-1,y-1,x+1,y+1,fill = cfg.fg)
        for i in range(12):
            x,y = self.point(i,12,radius-6,originX,originY)
            self.create_rectangle(x-3,y-3,x+3,y+3,fill = cfg.fg)
        self.ampm = self.create_text(3,3,anchor = NW,fill = cfg.fg)
    
    def point(self,tick,units,radius,originX,originY):
        angle = tick * (360.0 / units)
        radiansPerDegree = math.pi / 180
        pointX = int( round( radius * math.sin(angle * radiansPerDegree)))
        pointY = int( round( radius * math.cos(angle * radiansPerDegree)))
        return (pointX + originX+1), (originY+1 - pointY)
    
    def onUpdate(self,hour,mins,secs,ampm,cfg):
        if self.cog:
            self.delete(self.cog)
            self.delete(self.hourHand)
            self.delete(self.minsHand)
            self.delete(self.secsHand)
        originX = originY = radius = cfg.size // 2
        hour = hour + (mins / 60.0)
        hx, hy = self.point(hour,12,(radius * .80),originX,originY)
        mx, my = self.point(mins,60,(radius * .90),originX,originY)
        sx, sy = self.point(secs,60,(radius * .95),originX,originY)
        self.hourHand = self.create_line(originX,originY,hx,hy,
                            width = (cfg.size * .04),
                            arrow = 'last',arrowshape = (25,15,15),fill = cfg.hh) #arrow стрелка
        self.minsHand = self.create_line(originX,originY,mx,my,
                            width = (cfg.size * .03),
                            arrow = 'last',arrowshape = (20,20,10),fill =cfg.mh)
        self.secsHand = self.create_line(originX,originY,sx,sy,
                            width = 1,
                            arrow = 'last',arrowshape = (5,10,5),fill = cfg.sh)
        cogsz = cfg.size * .01
        self.cog = self.create_oval(originX-cogsz,originY+cogsz,
                        originX+cogsz,originY-cogsz,fill = cfg.cog)
        self.dchars(self.ampm,0,END)
        self.insert(self.ampm,END,ampm)
    
    def onResize(self,newWidth,newHeight,cfg):
        newSize = min(newWidth,newHeight)
        if newSize != cfg.size+4:
            cfg.size = newSize-4
            self.delete('all')
            self.drawClockface(cfg)

##########################
# Состовной объект часов #
##########################

ChecksPerSec = 10

class Clock(Frame):
    def __init__(self,config = ClockConfig,parent = None):
        Frame.__init__(self,parent)
        self.cfg = config
        self.makeWidgets(parent)
        self.labelOn = 0
        self.display = self.digitalDisplay
        self.lastSec = self.lastMin = -1
        self.countdownSeconds = 0
        self.onSwitchMode(None)
        self.onTimer()
    
    def makeWidgets(self,parent):
        self.digitalDisplay = DigitalDisplay(self,self.cfg)
        self.analogDisplay = AnalogDisplay(self,self.cfg)
        self.dateLabel = Label(self,bd = 3,bg = 'red',fg = 'blue')
        parent.bind('<ButtonPress-1>',self.onSwitchMode)
        parent.bind('<ButtonPress-3>',self.onToggleLabel)
        parent.bind('<Configure>',self.onResize)
        parent.bind('<KeyPress-s>',self.onCountdownSec)
        parent.bind('<KeyPress-m>',self.onCountdownMin)
    
    def onSwitchMode(self,event):
        self.display.pack_forget()
        if self.display == self.analogDisplay:
            self.display = self.digitalDisplay
        else:
            self.display = self.analogDisplay
        self.display.pack(side = TOP,expand = YES,fill = BOTH)
    
    def onToggleLabel(self,event):
        self.labelOn += 1
        if self.labelOn % 2:
            self.dateLabel.pack(side = BOTTOM,fill = X)
        else:
            self.dateLabel.pack_forget()
        self.update()
    
    def onResize(self,event):
        if event.widget == self.display:
            self.display.onResize(event.width,event.height,self.cfg)

    def onTimer(self):
        secsSinceEpoch = time.time()
        timeTuple = time.localtime(secsSinceEpoch)
        hour,min,sec = timeTuple[3:6]
        if sec!= self.lastSec:
            self.lastSec = sec
            ampm = ((hour >=12) and 'PM') or 'AM'
            hour = (hour % 12) or 12
            self.display.onUpdate(hour,min,sec,ampm,self.cfg)
            self.dateLabel.config(text = time.ctime(secsSinceEpoch))
            self.countdownSeconds -= 1
            if self.countdownSeconds == 0:
                self.onCountdownExpire()
        self.after(1000 // ChecksPerSec,self.onTimer)
    
    def onCountdownSec(self,event):
        secs = askinteger('CountDown','Seconds?')
        if secs: self.countdownSeconds = secs
    
    def onCountdownMin(self,event):
        secs = askinteger('CountDown','Seconds?')
        if secs: self.countdownSeconds = secs * 60
    
    def onCountdownExpire(self):
        win = Toplevel()
        msg = Button(win,text = 'Timer Expired!',command = win.destroy)
        msg.config(font = ('courier',80,'normal'),fg = 'white',bg = 'navy')
        msg.config(padx = 10,pady = 10)
        msg.pack(expand = YES,fill = BOTH)
        win.lift()
        if sys.platform[:3] == 'win':
            win.state('zoomed')

###################
# Автономные часы #
###################

appname = 'PyClock 2.1'
from windows import PopupWindow,MainWindow

class ClockPopup(PopupWindow):
    def __init__(self,config = ClockConfig,name = ''):
        PopupWindow.__init__(self,appname,name)
        clock = Clock(config,self)
        clock.pack(expand = YES,fill = BOTH)
    
class ClockMain(MainWindow):
    def __init__(self,config = ClockConfig,name = ''):
        MainWindow.__init__(self,appname,name)
        clock = Clock(config,self)
        clock.pack(expand = YES,fill = BOTH)

class ClockWindow(Clock):
    def __init__(self,config = ClockConfig,parent = None,name = ''):
        Clock.__init__(self,config,parent)
        self.pack(expand = YES,fill = BOTH)
        title = appname
        if name: title = title + '-' + name
        self.master.title(title)
        self.master.protocol('WM_DELETE_WINDOW',self.quit)

if __name__=='__main__':
    def getOptions(config,argv):
        for attr in dir(ClockConfig):
            try:
                ix = argv.index('-' + attr)
            except:
                continue
            else:
                if ix in range(1,len(argv)-1):
                    if type(getattr(ClockConfig,attr))== int:
                        setattr(config,attr,int(argv[ix+1]))
                    else:
                        setattr(config,attr,argv[ix+1])
    
    #config = PhotoClockConfig()
    config = ClockConfig()
    if len(sys.argv) >=2:
        getOptions(config,sys.argv)
    #myclock = ClockWindow(config, Tk()) 
    #myclock = ClockPopup(ClockConfig(), 'popup') 
    myclock = ClockMain(config)
    myclock.mainloop()       

    






