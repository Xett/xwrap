import wx
from . import Events as e
#############################
#       Event Constants     #
#############################
RENDER_PANEL_ONSIZE_EVENT='Render-Panel-OnSize-Event'
RENDER_PANEL_ONPAINT_EVENT='Render-Panel-OnPaint-Event'
RENDER_PANEL_DRAW_MAIN_EVENT='Render-Panel-Draw-Main-Event'
BUFFER_BITMAP_DRAW_BUFFER_EVENT='Buffer-Bitmap-Draw-Buffer-Event'
BUFFER_BITMAP_ONSIZE_EVENT='Buffer-Bitmap-OnSize-Event'
#####################
#       Frame       #
#####################
class Frame(wx.Frame):
    def __init__(self,events,title='Frame',size=(1920,1080)):
        wx.Frame.__init__(self,None,-1,title,size)
        self.events=events
        self.main_sizer=wx.BoxSizer()
        self.SetSizer(self.main_sizer)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
    def OnClose(self,event):
        self.events.CallEvent(e.CloseEvent())
#############################
#       Buffer Bitmap       #
#############################
    ############################
    #       Draw Buffer        #
    ############################
class BufferBitmapDrawBufferTask(e.Task):
    def __init__(self,event):
        e.Task.__init__(self,event,self.resfunc)
    def do(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.event.image)
        dc.SetBackground(wx.Brush(wx.Colour('white')))
        dc.Clear()
        for image,coord in self.event.images.items():
            dc.DrawBitmap(image.image,coord[0],coord[1])
    def resfunc(self,events):
        events.data_model[event.id].data.image=event.image
class BufferBitmapDrawBufferEvent(e.Event):
    def __init__(self,image,images):
        e.Event.__init__(self,BUFFER_BITMAP_DRAW_BUFFER_EVENT)
        self.image=image
        self.images=images
    ######################
    #       On Size      #
    ######################
class BufferBitmapOnSizeTask(e.Task):
    def __init__(self,event):
        e.Task.__init__(self,event,self.resfunc)
    def do(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.event.image)
        dc.SetBackground(wx.Brush(wx.Colour('white')))
        dc.Clear()
        for image,coord in self.event.images.items():
            dc.DrawBitmap(image.image,coord[0],coord[1])
    def resfunc(self,events):
        events.data_model[event.id].data.image=event.image
class BufferBitmapOnSizeEvent(e.Event):
    def __init__(self,id,image,images):
        e.Event.__init__(self,BUFFER_BITMAP_ONSIZE_EVENT)
        self.id=id
        self.image=image
        self.images=images
    #####################
    #       Class       #
    #####################
class BufferBitmap:
    def __init__(self,parent,events,name='BufferBitmap'):
        self.parent=parent
        self.events=events
        self.images={}
        self.events.Bind(BUFFER_BITMAP_DRAW_BUFFER_EVENT,self.DrawBuffer)
        self.events.BindData(name,self)
    @property
    def width(self):
        return self.parent.GetSize()[0]
    @property
    def height(self):
        return self.parent.GetSize()[1]
    @property
    def size(self):
        return self.parent.GetSize()
    def AddImage(self,image,x=0,y=0):
        self.images[image]=(x,y)
    def OnSize(self,event):
        self.events.CallEvent(BufferBitmapOnSizeEvent(self.events.data_model['BufferBitmap'].id,self.image,self.images))
    def DrawBuffer(self,event):
        return BufferBitmapDrawBufferTask(event)
    def Draw(self,dc):
        dc.DrawBitmap(self.image,0,0)
#############################
#       Render Panel        #
#############################
    #####################
    #       On Size     #
    #####################
class RenderPanelOnSizeTask(e.Task):
    def __init__(self,event):
        e.Task.__init__(self,event,self.resfunc)
class RenderPanelOnSizeEvent(e.Event):
    def __init__(self):
        e.Event.__init__(self,RENDER_PANEL_ONSIZE)
    #########################
    #       On Paint        #
    #########################
class RenderPanelOnPaintTask(e.Task):
    def __init__(self,event):
        e.Task.__init__(self,event,self.resfunc)
    def resfunc(self,events):
        wx.BufferedPaintDC(self,self.events.data_model[self.id].data.image)
class RenderPanelOnPaintEvent(e.Event):
    def __init__(self,id):
        e.Event.__init__(self,RENDER_PANEL_ONSIZE)
        self.id=id
    #########################
    #       Draw Main       #
    #########################
class RenderPanelDrawMainTask(e.Task):
    def __init__(self,event):
        e.Task.__init__(self,event,self.resfunc)
    def resfunc(self,app):
        self.dc=wx.MemoryDC()
        self.buffer_bitmap.Draw(self.dc)
class RenderPanelDrawMainEvent(e.Event):
    def __init__(self):
        e.Event.__init__(self,RENDER_PANEL_ONSIZE)
    #####################
    #       Class       #
    #####################
class RenderPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.events=self.parent.events
        self.buffer_bitmap=BufferBitmap(self)
        self.buffer_bitmap.addImage()
    def initialise(self):
        self.events.Bind(RENDER_PANEL_DRAW_MAIN_EVENT,self.Draw)
        self.events.Bind(RENDER_PANEL_ONSIZE,self.buffer_bitmap.OnSize)
        self.events.Bind(RENDER_PANEL_ONSIZE,self.OnSize)
        self.events.Bind(RENDER_PANEL_ONPAINT,self.OnPaint)
        self.Bind(wx.EVT_SIZE,self.wxOnSize)
        self.Bind(wx.EVT_PAINT,self.wxOnPaint)
        self.events.CallEvent(RENDER_PANEL_DRAW_MAIN_EVENT)
    def wxOnPaint(self,events):
        self.events.callEvent(RenderPanelOnPaintEvent())
    def OnPaint(self,event):
        return RenderPanelOnPaintTask()
    def wxOnSize(self,events):
        self.events.callEvent(RenderPanelOnSizeEvent())
    def OnSize(self,event):
        return RenderPanelOnSizeTask(self.UpdateDrawing)
    def UpdateDrawing(self,events):
        self.events.CallEvent(RENDER_PANEL_DRAW_MAIN_EVENT)
        self.Refresh(eraseBackground=False)
        self.Update()
    def Draw(self,event):
        return RenderPanelDrawMainTask()
#####################
#       Panel       #
#####################
    #####################
    #       Class       #
    #####################
class Panel(wx.Panel):
    def __init__(self,parent,main_sizer_orientation=wx.HORIZONTAL):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.events=self.parent.events
        self.main_sizer=wx.BoxSizer(orient=main_sizer_orientation)
        self.SetSizer(self.main_sizer)
