import sys,os,math
from tkinter import *
from tkinter.filedialog import *

from PIL import Image
from PIL.ImageTk import PhotoImage

saveDialog = SaveAs(title = 'Save As (filename gives image type)')
openDialog = Directory(title = 'Select Image Directory To Open')

trace = print
appname = 'PyPhoto 1.1'

def makeThumbs(imgdir,size = (100,100),subdir = 'thumbs'):
    thumbdir = os.path.join(imgdir,subdir)
    if not os.path.exists(thumbdir):
        os.mkdir(thumbdir)
    
    thumbs = []
    for imgfile in os.listdir(imgdir):
        thumbpath = os.path.join(thumbdir,imgfile)
        if os.path.exists(thumbpath):
            thumbobj = Image.open(thumbpath)
            thumbs.append((imgfile,thumbobj))
        else:
            print('making',thumbpath)
            imgpath = os.path.join(imgdir,imgfile)
            try:
                imgobj = Image.open(imgpath)
                imgobj.thumbnail(size,Image.ANTIALIAS)
                imgobj.save(thumbpath)
                thumbs.append((imgfile,imgobj))
            except:
                print('Skipping: ',imgpath)
    return thumbs

class ScrolledCanvas(Canvas):
    def __init__(self,container):
        Canvas.__init__(self,container)
        self.config(borderwidth = 0)
        vbar = Scrollbar(container)
        hbar = Scrollbar(container,orient = 'horizontal')

        vbar.pack(side = RIGHT,fill = Y)
        hbar.pack(side = BOTTOM,fill = X)
        self.pack(side = TOP, fill = BOTH, expand = YES)

        vbar.config(command = self.yview)
        hbar.config(command = self.xview)
        self.config(yscrollcommand = vbar.set)
        self.config(xscrollcommand = hbar.set)

class ViewOne(Toplevel):
    def __init__(self,imgdir,imgfile,forcesize = ()):
        Toplevel.__init__(self)
        helptxt = '(click L/R or press I/O to resize, S to save, D to open)'
        self.title(appname + imgfile + ' ' + helptxt)
        imgpath = os.path.join(imgdir,imgfile)
        imgpil = Image.open(imgpath)
        self.canvas = ScrolledCanvas(self)
        self.drawImage(imgpil,forcesize)
        self.canvas.bind('<Button-1>',self.onSizeToDisplayHeight)
        self.canvas.bind('<Button-3>',self.onSizeToDisplayWidth)
        self.bind('<KeyPress-i>', self.onZoomIn)
        self.bind('<KeyPress-o>', self.onZoomOut)
        self.bind('<KeyPress-s>', self.onSaveImage)
        self.bind('<KeyPress-d>', self.onDirectoryOpen)
    
    def drawImage(self,imgpil,forcesize = ()):
        imgtk = PhotoImage(image = imgpil)
        scrwide, scrhigh = forcesize or self.maxsize() # размеры экрана
        imgwide = imgtk.width()
        imghigh = imgtk.height()

        fullsize = (0,0, imgwide, imghigh)
        viewwide = min(imgwide,scrwide)
        viewhigh = min(imghigh,scrhigh)

        canvas = self.canvas
        canvas.delete('all')
        canvas.config(height = viewhigh,width = viewwide)
        canvas.config(scrollregion = fullsize) # размер прокрутки
        canvas.create_image(0,0,image = imgtk,anchor = NW)
    
        if imgwide <= scrwide and imghigh <= scrhigh:
            self.state('normal') # размер окна по изоброжению
        elif sys.platform[:3] == 'win':
            self.state('zoomed') # в виндоус на весь экран
        self.saveimage = imgpil
        self.savephoto = imgtk
        trace((scrwide,scrhigh),imgpil.size)

    def sizeToDisplaySide(self,scaler):
        imgpil = self.saveimage
        scrwide, scrhigh = self.maxsize()
        imgwide, imghigh = imgpil.size
        newwide, newhigh = scaler(scrwide, scrhigh, imgwide, imghigh) 
        if (newwide * newhigh < imgwide * imghigh):
            filter = Image.ANTIALIAS
        else:
            filter = Image.BICUBIC
        imgnew = imgpil.resize((newwide, newhigh), filter)  
        self.drawImage(imgnew)
    
    def onSizeToDisplayHeight(self,event):
        def scaleHigh(scrwide,scrhigh,imgwide,imghigh):
            newhigh = scrhigh
            newwide = int(scrhigh * (imgwide / imghigh))
            return (newwide,newhigh)
        self.sizeToDisplaySide(scaleHigh)
    
    def onSizeToDisplayWidth(self,event):
        def scaleWide(scrwide, scrhigh, imgwide, imghigh):
            newwide = scrwide
            newhigh = int(scrwide * (imghigh / imgwide))
            return (newwide,newhigh)
        self.sizeToDisplaySide(scaleWide)
    
    def zoom(self,factor):
        imgpil = self.saveimage
        wide, high = imgpil.size
        if factor < 1.0:
            filter = Image.ANTIALIAS
        else:
            filter = Image.BICUBIC
        new = imgpil.resize((int(wide * factor), int(high * factor)), filter)
        self.drawImage(new)
    
    def onZoomIn(self,event,incr = 0.10):
        self.zoom(1.0+incr)

    def onZoomOut(self,event,incr = 0.10):
        self.zoom(1.0-incr)
    
    def onSaveImage(self,event):
        filename = saveDialog.show()
        if filename:
            self.saveimage.save(filename)
    
    def onDirectoryOpen(self,event):
        dirname = openDialog.show()
        if dirname:
            ViewOne.viewThumbs(dirname,kind = Toplevel)
    
    def viewThumbs(imgdir,kind = Toplevel,numcols = None,height = 400,width = 500):
        win = kind()
        helptxt = '(press D to open other)'
        win.title(appname + imgdir + ' ' + helptxt)
        quit = Button(win, text ='Quit',command = win.quit,bg = 'beige')
        quit.pack(side = BOTTOM,fill = X)
        canvas = ScrolledCanvas(win)
        canvas.config(height = height,width = width)
        
        thumbs = makeThumbs(imgdir)
        numthumbs = len(thumbs)
        if not numcols:
            numcols = int(math.ceil(math.sqrt(numthumbs)))
        numrows = int(math.ceil(numthumbs / numcols))
        
        linksize  = max(max(thumb[1].size) for thumb in thumbs) #самый большой размер из фото
        trace(linksize)
        fullsize = (0,0,(linksize*numcols),(linksize*numrows))
        canvas.config(scrollregion= fullsize)

        rowpos = 0
        savephotos = []
        while thumbs:
            thumbsrow, thumbs = thumbs[:numcols],thumbs[numcols:]
            colpos = 0
            for (imgfile,imgobj) in thumbsrow:
                photo = PhotoImage(imgobj)
                link = Button(canvas,image = photo)
                def handler(savefile = imgfile):
                    ViewOne(imgdir,savefile)
                link.config(command = handler,width = linksize,height = linksize)
                link.pack(side = LEFT,expand = YES)
                canvas.create_window(colpos,rowpos,anchor=NW,window=link,width=linksize,height=linksize)
                colpos += linksize
                savephotos.append(photo)
            rowpos += linksize
        win.bind('<KeyPress-d>',ViewOne.onDirectoryOpen)
        win.savephotos = savephotos
        return win

if __name__=='__main__':
    imgdir = 'images'
    if len(sys.argv) > 1:imgdir = sys.argv[1]
    if os.path.exists(imgdir):
        mainwin = ViewOne.viewThumbs(imgdir,kind = Tk)
    else:
        mainwin = Tk()
        mainwin.title(appname + 'Open')
        handler = lambda:ViewOne.onDirectoryOpen(None,None)
        Button(mainwin,text = 'Open Image Directory',command = handler).pack()
    mainwin.mainloop()
    