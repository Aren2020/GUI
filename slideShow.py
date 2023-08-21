from tkinter import *
import os
from tkinter.messagebox import askyesno,showerror
from tkinter.filedialog import askopenfilename
from PIL import Image
from PIL.ImageTk import PhotoImage
import random
Size = (450,450)

imageTypes = [('Gif files','.gif'),
              ('Ppm files','.ppm'),
              ('Pgm files','.pgm'),
              ('Png files','.png'),
              ('Jpg files','.jpg'),
              ('All files','*')]
imageExt = [imagetype[1] for imagetype in imageTypes]

class SlideShow(Frame):
    def __init__(self,parent = None,picdir = r'C:\Users\User\Pictures\Screenshots',msecs = 3000,size = Size,**args):
        Frame.__init__(self,parent,**args)
        self.size = size
        self.makeWidgets()
        self.pack(expand = YES,fill = BOTH)
        self.opens = picdir
        files = []
        for label,ext in imageTypes[:-1]:
            for filename in os.listdir(picdir):
                fileext = os.path.splitext(filename)[1]
                if fileext in imageExt:
                    filepath = os.path.join(picdir,filename)
                    files = files + [filepath]
        self.images = [(x,Image.open(x)) for x in files]
        self.msecs = msecs
        self.beep = True
        self.drawn = None
    
    def makeWidgets(self):
        height,width = self.size
        self.canvas = Canvas(self,bg = 'white',height = height,width = width)
        self.canvas.pack(side = LEFT, fill = BOTH, expand = YES)
        self.onoff = Button(self,text = 'Start',command = self.onStart)
        self.onoff.pack(fill = X)
        Button(self,text = 'Open',command = self.onOpen).pack(fill = X)
        Button(self,text = 'Beep',command = self.onBeep).pack(fill = X)
        Button(self,text = 'Quit',command = self.onQuit).pack(fill = X)
    
    def onStart(self):
        self.loop = True
        self.onoff.config(text = 'Stop',command = self.onStop)
        self.canvas.config(height = self.size[0],width = self.size[1])
        self.onTimer()
    
    def onStop(self):
        self.loop = False
        self.onoff.config(text = 'Start',command = self.onStart)
    
    def onOpen(self):
        self.onStop()
        name = askopenfilename(initialdir = self.opens,filetypes = imageTypes)
        if name:
            if self.drawn:self.canvas.delete(self.drawn)
            imgopen = Image.open(name)
            img = PhotoImage(imgopen)
            self.canvas.config(height = img.height(),width = img.width())
            self.drawn = self.canvas.create_image(2,2,image = img,anchor = NW)
            self.image = name,img
    
    def onQuit(self):
        self.onStop()
        self.update()
        if askyesno('PyView','Really quit now?'):
            self.quit()
    
    def onBeep(self):
        self.beep = not self.beep
    
    def onTimer(self):
        if self.loop:
            self.drawNext()
            self.after(self.msecs,self.onTimer)
    
    def drawNext(self):
        if self.drawn: self.canvas.delete(self.drawn)
        if self.images:
            name,imgopen = random.choice(self.images)
            img = PhotoImage(imgopen)
            self.drawn = self.canvas.create_image(2,2,image = img,anchor = NW)
            self.image = name,img
            if self.beep: self.bell() # звук
            self.canvas.update()
        else:
            showerror('PyView','You have not any image')
            self.onStop()

if __name__=='__main__':
    import sys
    if len(sys.argv) == 2:
        picdir = sys.argv[1]
    else:
        picdir = r'C:\Users\User\Documents\html\задачник по html и css\pictures'
    root = Tk()
    root.title('PyView')
    Label(root,text = 'Python Slide Show Viewer').pack()
    SlideShow(root,picdir = picdir,bd = 3,relief = SUNKEN)
    root.mainloop()