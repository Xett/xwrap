import wx
from .Events import *
from collections import OrderedDict
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
        return self._width if self._width>0 else 1
    @property
    def height(self):
        return self._height if self_height>0 else 1
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @property
    def size(self):
        return (self.width if self.width>0 else 1,self.height if self.height>0 else 1)
    @property
    def center_x(self):
        return self.size[0]/2
    @property
    def center_y(self):
        return self.size[1]/2
    def UpdateBitmap(self):
        self.Draw()
        self.SetMask()
    def Draw(self):
        return
    def SetMask(self):
        mask=wx.Mask(self.image,wx.Colour('white'))
        self.image.SetMask(mask)
    def OnSize(self):
        self.image=wx.Bitmap(self.size)
        self.UpdateBitmap()
    def DrawToBuffer(self,buffer_device_context):
        x=self.anchor.world_x+self.parent.offset_coord[0] if self.use_offset else self.anchor.world_x
        y=self.anchor.world_y+self.parent.offset_coord[1] if self.use_offset else self.anchor.world_y
        buffer_device_context.DrawBitmap(self.image,x,y,useMask=True)
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
        self.layers=OrderedDict()
    def AddLayer(self,layer_name):
        self.layers[layer_name]=OrderedDict()
    def AddBitmapToLayer(self,layer_name,bitmap):
        self.layers[layer_name][bitmap.name]=bitmap
    def wxOnSize(self,event):
        self.buffer_image=wx.Bitmap(*self.ClientSize)
        for layer_key,layer in self.layers.items():
            for bitmap_key,bitmap in layer.items():
                bitmap.OnSize()
        self.UpdateDrawing()
    def wxOnPaint(self,event):
        wx.BufferedPaintDC(self,self.buffer_image)
    def UpdateDrawing(self):
        dc=wx.MemoryDC()
        try:
            dc.SelectObject(self.buffer_image)
        except:
            self.wxOnSize(None)
        self.Draw(dc)
        self.Refresh(eraseBackground=False)
        self.Update()
    def Draw(self,dc):
        dc.SetBackground(self.brushes['background'])
        dc.Clear()
        for layer_key,layer in self.layers.items():
            for bitmap_key,bitmap in layer.items():
                bitmap.DrawToBuffer(dc)
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
