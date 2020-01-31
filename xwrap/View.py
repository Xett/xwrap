import wx
from . import Events as e
MAP_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT='Map-Render-Panel-Mouse-Left-Down-Event'
MAP_RENDER_PANEL_MOUSE_LEFT_UP_EVENT='Map-Render-Panel-Mouse-Left-Up-Event'
MAP_RENDER_PANEL_MOUSE_MOTION='Map-Render-Panel-Mouse-Motion'
class Bitmap:
    def __init__(self,parent,name,width=10,height=10,x=0,y=0):
        self.parent=parent
        self.events=self.parent.events
        self.name=name
        self._width=width
        self._height=height
        self._x=x
        self._y=y
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
    def Draw(self):
        return
    def OnSize(self):
        self.image=wx.Bitmap(self.size)
        self.Draw()
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
        self.events=parent.events
        self.name=name
        self.new_mouse_coord=(0,0)
        self.old_mouse_coord=(0,0)
        self.offset_coord=(0,0)
        self.events.BindData(self.name,self)
        self.events.AddEvent(MAP_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT)
        self.events.AddEvent(MAP_RENDER_PANEL_MOUSE_LEFT_UP_EVENT)
        self.events.AddEvent(MAP_RENDER_PANEL_MOUSE_MOTION)
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
            self.events.CallEvent(MAP_RENDER_PANEL_MOUSE_MOTION)
        if event.Dragging():
            self.is_dragging=True
            self.offset_coord=(self.offset_coord[0]+(self.new_mouse_coord[0]-self.old_mouse_coord[0]),self.offset_coord[1]+(self.new_mouse_coord[1]-self.old_mouse_coord[1]))
            self.UpdateDrawing()
            self.events.CallEvent(MAP_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT)
            event.Skip()
        elif event.LeftDown():
            self.is_left_click_down=True
            self.events.CallEvent(MAP_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT)
            event.Skip()
        elif event.LeftUp():
            self.is_dragging=False
            self.is_left_click_down=False
            self.events.CallEvent(MAP_RENDER_PANEL_MOUSE_LEFT_UP_EVENT)
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
