import wx
from . import Events as e
class Bitmap:
    def __init__(self,parent,name,width=10,height=10,x=0,y=0):
        self.parent=parent
        self.events=self.parent.events
        self.name=name
        self._width=width
        self._height=height
        self._x=x
        self._y=y
        self.draw_event_name='{}-Draw-Event'.format(self.name)
        self.onsize_event_name='{}-OnSize-Event'.format(self.name)
        self.events.AddEvent(self.draw_event_name)
        self.events.Bind(self.draw_event_name,self.DrawEvent)
        self.events.AddEvent(self.onsize_event_name)
        self.events.Bind(self.onsize_event_name,self.OnSize)
        self.image=wx.Bitmap(self.size)
    @property
    def width(self):
        return self._width
    @property
    def height(self):
        return self._height
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @property
    def size(self):
        return (self.width,self.height)
    @property
    def center_x(self):
        return self.size[0]/2
    @property
    def center_y(self):
        return self.size[1]/2
    def Draw(dc,image,size,center_x,center_y):
        return
    def OnSize(self,event):
        return BitmapOnSizeTask(event,self.name)
    def DrawEvent(self,event):
        return BitmapDrawTask(event,self.Draw)
class Frame(wx.Frame):
    def __init__(self,events,title='Frame',size=(1920,1080)):
        wx.Frame.__init__(self,None,-1,title,size)
        self.events=events
        self.main_sizer=wx.BoxSizer()
        self.SetSizer(self.main_sizer)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
    def OnClose(self,event):
        self.events.CallEvent(e.CloseEvent())
class Panel(wx.Panel):
    def __init__(self,parent,main_sizer_orientation=wx.HORIZONTAL):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.events=self.parent.events
        self.main_sizer=wx.BoxSizer(orient=main_sizer_orientation)
        self.SetSizer(self.main_sizer)
class RenderPanel(wx.Panel):
    def __init__(self,parent,name=''):
        wx.Panel.__init__(self,parent,size=(100,100))
        self.events=parent.events
        self.name=name
        self.events.BindData(self.name,self)
        self.Bind(wx.EVT_SIZE,self.wxOnSize)
        self.Bind(wx.EVT_PAINT,self.wxOnPaint)
        self.text_colours={}
        self.pens={}
        self.brushes={}
        self.brushes['background']=wx.Brush('white')
    def wxOnSize(self,event):
        self.buffer_image=wx.Bitmap(*self.ClientSize)
        self.UpdateDrawing()
    def wxOnPaint(self,events):
        wx.BufferedPaintDC(self,self.buffer_image)
    def UpdateDrawing(self):
        dc=wx.MemoryDC()
        try:
            dc.SelectObject(self.buffer_image)
        except:
            self.wxOnSize(None)
        self._Draw(dc)
        self.Refresh(eraseBackground=False)
        self.Update()
    def _Draw(self,dc):
        dc.SetBackground(self.brushes['background'])
        dc.Clear()
        self.Draw(dc)
class RadioBox(wx.RadioBox):
    def __init__(self,parent,choices=[],name=''):
        wx.RadioBox.__init__(self,parent,choices=choices)
        self.parent=parent
        self.name=name
        self.events=self.parent.events
        self.events.BindData(self.name,self)
