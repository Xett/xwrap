import wx
from . import Events as e
class BitmapAnchor:
    def __init__(self,parent,anchor_x=0.0,anchor_y=0.0):
        self.parent=parent# Bitmap
        self.anchor_x=anchor_x
        self.anchor_y=anchor_y
    def SetCoordinates(self,anchor_x=0.0,anchor_y=0.0):
        self.anchor_x=anchor_x
        self.anchor_y=anchor_y
    def SetCoordinatesFromWorld(self,world_x,world_y):
        parent_coordinates=self.GetBitmapWorldCoordinates()
        parent_size=self.GetSize()
        self.anchor_x=(world_x-parent_coordinates[0])/parent_size[0]
        self.anchor_y=(world_y-parent_coordinates[1])/parent_size[1]
    def GetBitmapWorldCoordinates(self):
        return (self.parent.x,self.parent.y)
    def GetSize(self):
        return self.parent.size
    @property
    def x(self):
        return self.anchor_x*self.GetSize()[0]
    @property
    def y(self):
        return self.anchor_y*self.GetSize()[1]
    @property
    def local(self):
        return (self.x,self.y)
    @property
    def world_x(self):
        return self.GetBitmapWorldCoordinates()[0]-self.x
    @property
    def world_y(self):
        return self.GetBitmapWorldCoordinates()[1]-self.y
    @property
    def world(self):
        return (self.world_x,self.world_y)
class Bitmap:
    def __init__(self,parent,name,width=10,height=10,x=0,y=0):
        self.parent=parent
        self.events=self.parent.events
        self.name=name
        self._width=width
        self._height=height
        self._x=x
        self._y=y
        self.anchor=BitmapAnchor(self)
        self.image=wx.Bitmap(self.size)
        self.use_offset=False
        self.SetMask()
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
    def _Draw(self):
        self.Draw()
        self.SetMask()
    def Draw(self):
        return
    def SetMask(self):
        mask=wx.Mask(self.image,wx.Colour('white'))
        self.image.SetMask(mask)
    def OnSize(self):
        self.image=wx.Bitmap(self.size)
        self._Draw()
    def DrawToBuffer(self,buffer_device_context):
        x=self.anchor.world_x+self.parent.offset_coord[0] if self.use_offset else self.anchor.world_x
        y=self.anchor.world_y+self.parent.offset_coord[1] if self.use_offset else self.anchor.world_y
        buffer_device_context.DrawBitmap(self.image,x,y,useMask=True)
class Frame(wx.Frame):
    def __init__(self,events,title='Frame',size=(1920,1080)):
        wx.Frame.__init__(self,None,-1,title,size)
        self.events=events
        self.main_sizer=wx.BoxSizer()
        self.SetSizer(self.main_sizer)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
    def OnClose(self,event):
        self.events.CallEvent(e.CLOSE_EVENT)
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
        self.parent=parent
        self.events=parent.events
        self.name=name
        self.mouse_left_down_event_name='{}-Mouse-Left-Down-Event'.format(self.name)
        self.mouse_left_up_event_name='{}-Mouse-Left-Up-Event'.format(self.name)
        self.mouse_motion_event_name='{}-Mouse-Motion-Event'.format(self.name)
        self.new_mouse_coord=(0,0)
        self.old_mouse_coord=(0,0)
        self.offset_coord=(0,0)
        self.events.BindData(self.name,self)
        self.events.AddEvent(self.mouse_left_down_event_name)
        self.events.AddEvent(self.mouse_left_up_event_name)
        self.events.AddEvent(self.mouse_motion_event_name)
        self.Bind(wx.EVT_SIZE,self.wxOnSize)
        self.Bind(wx.EVT_PAINT,self.wxOnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS,self.wxUpdateMouse)
        self.text_colours={}
        self.pens={}
        self.brushes={}
        self.brushes['background']=wx.Brush('white')
    def wxOnSize(self,event):
        self.buffer_image=wx.Bitmap(*self.ClientSize)
        self.UpdateDrawing()
    def wxOnPaint(self,event):
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
    def wxUpdateMouse(self,event):
        self.old_mouse_coord=self.new_mouse_coord
        self.new_mouse_coord=(event.GetX(),event.GetY())
        center_x,center_y=(self.GetSize())/2
        self.point=(
            self.new_mouse_coord[0]-center_x-self.offset_coord[0],
            self.new_mouse_coord[1]-center_y-self.offset_coord[1])
        if self.old_mouse_coord!=self.new_mouse_coord:
            self.events.CallEvent(self.mouse_motion_event_name)
        if event.Dragging():
            self.is_dragging=True
            self.offset_coord=(self.offset_coord[0]+(self.new_mouse_coord[0]-self.old_mouse_coord[0]),self.offset_coord[1]+(self.new_mouse_coord[1]-self.old_mouse_coord[1]))
            self.UpdateDrawing()
            self.events.CallEvent(self.mouse_left_down_event_name)
            event.Skip()
        elif event.LeftDown():
            self.is_left_click_down=True
            self.events.CallEvent(self.mouse_left_down_event_name)
            event.Skip()
        elif event.LeftUp():
            self.is_dragging=False
            self.is_left_click_down=False
            self.events.CallEvent(self.mouse_left_up_event_name)
            event.Skip()
class RadioBox(wx.RadioBox):
    def __init__(self,parent,name,choice_event_name,choices=[]):
        wx.RadioBox.__init__(self,parent,choices=choices)
        self.parent=parent
        self.name=name
        self.choice_event_name=choice_event_name
        self.events=self.parent.events
        self.events.AddEvent(self.choice_event_name)
        self.events.BindData(self.name,self)
        self.Bind(wx.EVT_RADIOBOX,self.wxOnChoice)
    def wxOnChoice(self,event):
        self.events.CallEvent(self.choice_event_name)
class SpinCtrl(wx.SpinCtrl):
    def __init__(self,parent,name,change_event_name,value='0',min=0,max=100):
        wx.SpinCtrl.__init__(self,parent,value=value,min=min,max=max)
        self.parent=parent
        self.name=name
        self.change_event_name=change_event_name
        self.events=self.parent.events
        self.events.AddEvent(self.change_event_name)
        self.events.BindData(self.name,self)
        self.Bind(wx.EVT_SPINCTRL,self.wxOnChange)
    def wxOnChange(self,event):
        self.events.CallEvent(self.change_event_name)
