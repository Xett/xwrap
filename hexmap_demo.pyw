import wx
import multiprocessing as mp
import numpy as np
import math
import copy
from xwrap.App import *
from xwrap.Events import *
from xwrap.View import *
from collections import OrderedDict
#from hexmap import Iterators
#from hexmap.Coords import Cube
#from hexmap.Coords import Axial
#from hexmap.Maps import RadialMap
import wx
def pixel_to_hex(point):
    q=((2./3)*point[0])/100
    r=(((-1./3)*point[0])+(np.sqrt(3)/3)*point[1])/100
    return round(Axial(q,r).toCube())
#class BufferBitmapOnSizeTask(e.Task):
#    def __init__(self,event):
#        e.Task.__init__(self,event)
#    def resfunc(self,events):
#        events.CallEvent(BufferBitmapDrawBufferEvent(self.event.buffer_bitmap_id,self.event.size,self.event.images))
#class BufferBitmapOnSizeEvent(e.Event):
#    def __init__(self,buffer_bitmap_id,size,images):
#        e.Event.__init__(self,BUFFER_BITMAP_ONSIZE_EVENT)
#        self.buffer_bitmap_id=buffer_bitmap_id
#        self.size=size
#        self.images=images
#class BufferBitmap:
#    def __init__(self,parent,name='BufferBitmap'):
#        self.parent=parent
#        self.name=name
#        self.events=self.parent.events
#        self.image=wx.Bitmap(*self.size)
#        self.images={}
#        self.events.AddEvent(BUFFER_BITMAP_DRAW_BUFFER_EVENT)
#        self.events.AddEvent(BUFFER_BITMAP_ONSIZE_EVENT)
#        self.events.Bind(BUFFER_BITMAP_DRAW_BUFFER_EVENT,self.DrawBuffer)
#        self.events.BindData(self.name,self)
#    @property
#    def width(self):
#        return self.parent.GetSize()[0]
#    @property
#    def height(self):
#        return self.parent.GetSize()[1]
#    @property
#    def size(self):
#        return self.parent.GetSize()
#    def AddImage(self,image,x=0,y=0):
#        self.images[image]=(x,y)
#    def OnSize(self,event):
#        name_id=self.events.data_model[self.name].id
#        self.events.CallEvent(BufferBitmapOnSizeEvent(name_id,self.size,self.images))
#    def DrawBuffer(self,event):
#        return BufferBitmapDrawBufferTask(event)
#class BitmapDrawTask(Task):
#    def __init__(self,event,drawfunc):
#        Task.__init__(self,event)
#        self.drawfunc=drawfunc
#    def do(self):
#        dc=wx.MemoryDC()
#        image=wx.Bitmap(size)
#        dc.SelectObject(image)
#        dc.Clear()
        #self.drawfunc(dc,image,self.size,self.center_x,self.center_y)
#class BitmapDrawEvent(Event):
#    def __init__(self,draw_event_name,size,center_x,center_y):
#        Event.__init__(self,draw_event_name)
#        self.size=size
#        self.center_x=center_x
#        self.center_y=center_y
#class BitmapOnSizeTask(Task):
#    def __init__(self,event):
#        Task.__init__(self,event,self.resfunc)
#    def resfunc(self,events):
#        return#self.events.data_model[self.event.bitmap_id].data=wx.Bitmap(self.event.size)
        #events.CallEvent(BitmapDrawEvent(self.event.draw_event_name))
#class BitmapOnSizeEvent(Event):
#    def __init__(self,onsize_event_name,bitmap_id,size,draw_event_name):
#        Event.__init__(self,onsize_event_name)
#        self.bitmap_id=bitmap_id
#        self.size=size
#        self.draw_event_name=draw_event_name
class HexmapBitmap(Bitmap):
    def __init__(self,parent):
        Bitmap.__init__(self,parent,'Hexmap-Bitmap')
    @property
    def width(self):
        return self.parent.GetSize()[0]
    @property
    def height(self):
        return self.parent.GetSize()[1]
    @property
    def size(self):
        return self.parent.GetSize()
    @property
    def x(self):
        return 0
    @property
    def y(self):
        return 0
    def Draw(dc,image,size,center_x,center_y):
        height=(100)*np.sqrt(3)
        width=(100)*2
        for x,y,z in Iterators.RingIterator(self.parent.hexmap.radius,6):
            x_coord=x*((width/4)*3)
            y_coord=(y*(height/2))-(z*(height/2))
            h=[(vert[0]+x_coord+center_x+self.parent.offset_coord[0],
                vert[1]-y_coord+center_y+self.parent.offset_coord[1]) for vert in self.parent.hexagon]
            tile=self.parent.hexmap[Cube(x,y,z)]
            dc.SetBrush(wx.Brush(wx.Colour(255,255,255)))
            if (x,y,z)==(self.parent.hovered_tile.x,self.parent.hovered_tile.y,self.parent.hovered_tile.z):
                dc.SetBrush(wx.Brush(wx.Colour(0,255,255)))
            elif (x,y,z)==(self.parent.selected_tile.x,self.parent.selected_tile.y,self.parent.selected_tile.z):
                dc.SetBrush(wx.Brush(wx.Colour(0,0,255)))
            elif tile!=False:
                if tile.isPassable==False:
                    dc.SetBrush(self.parent.brushes['not_passable_tile'])
                elif tile.movement_cost==1:
                    dc.SetBrush(self.parent.brushes['movement_cost_1_tile'])
                elif tile.movement_cost==2:
                    dc.SetBrush(self.parent.brushes['movement_cost_2_tile'])
            dc.SetPen(self.parent.pens['hex_outline'])
            dc.DrawPolygon(h)
            text_sizes={
                'X':dc.GetTextExtent(str(x)),
                'Y':dc.GetTextExtent(str(y)),
                'Z':dc.GetTextExtent(str(z))
            }
            if self.parent.notation_type=='Cube':
                cubic_coordinates={
                    'X':(x_coord+center_x+self.parent.offset_coord[0]-(text_sizes['X'][0]/2),-y_coord+center_y+self.parent.offset_coord[1]-(height/3)),
                    'Y':(x_coord+center_x+self.parent.offset_coord[0]-(width/4),-y_coord+center_y+self.parent.offset_coord[1]+(height/4)-text_sizes['Y'][1]),
                    'Z':(x_coord+center_x+self.parent.offset_coord[0]+(width/4)-text_sizes['Z'][0],-y_coord+center_y+self.parent.offset_coord[1]+(height/4)-text_sizes['Z'][1])
                }
                for coord,axis in zip([x,y,z],['X','Y','Z']):
                    dc.SetTextForeground(self.parent.text_colours[axis])
                    dc.DrawText(str(coord),cubic_coordinates[axis][0],cubic_coordinates[axis][1])
            elif self.parent.notation_type=='Axial':
                axial_coordinates={
                    'X':(x_coord+center_x+self.parent.offset_coord[0]-(width/4),-y_coord+center_y+self.parent.offset_coord[1]-(text_sizes['X'][1]/2)),
                    'Y':(x_coord+center_x+self.parent.offset_coord[0]+(width/4)-text_sizes['Y'][0],-y_coord+center_y+self.parent.offset_coord[1]-(text_sizes['Y'][1]/2))
                }
                dc.DrawText(str(x),axial_coordinates['X'][0],axial_coordinates['X'][1])
                dc.DrawText(str(y),axial_coordinates['Y'][0],axial_coordinates['Y'][1])
class AxisBitmap(Bitmap):
    def __init__(self,parent):
        Bitmap.__init__(self,parent,'Axis-Bitmap')
        self.SetMode('None')
    @property
    def width(self):
        return self.parent.GetSize()[0]//8
    @property
    def height(self):
        return self.parent.GetSize()[1]//8
    @property
    def size(self):
        return (self.width,self.width) if self.width<self.height else (self.height,self.height)
    @property
    def x(self):
        return 0
    @property
    def y(self):
        return self.parent.GetSize()[1]-self.size[1]
    @property
    def axis_coords(self):
        if self.current_mode=='Cube':
            return {
                'X':{0:(np.cos((np.pi/180)*180),np.sin((np.pi/180)*180)),1:(np.cos((np.pi/180)*0),np.sin((np.pi/180)*0))},
                'Y':{0:(np.cos((np.pi/180)*240),np.sin((np.pi/180)*240)),1:(np.cos((np.pi/180)*60),np.sin((np.pi/180)*60))},
                'Z':{0:(np.cos((np.pi/180)*300),np.sin((np.pi/180)*300)),1:(np.cos((np.pi/180)*120),np.sin((np.pi/180)*120))}
            }
        elif self.current_mode=='Axial':
            return {
                'X':{0:(np.cos((np.pi/180)*180),np.sin((np.pi/180)*180)),1:(np.cos((np.pi/180)*0),np.sin((np.pi/180)*0))},
                'Y':{0:(np.cos((np.pi/180)*240),np.sin((np.pi/180)*240)),1:(np.cos((np.pi/180)*60),np.sin((np.pi/180)*60))}
            }
    def text_sizes(self,dc):
        if self.current_mode=='Cube':
            return {
                '+X':dc.GetTextExtent('+X'),
                '-X':dc.GetTextExtent('-X'),
                '+Y':dc.GetTextExtent('+Y'),
                '-Y':dc.GetTextExtent('-Y'),
                '+Z':dc.GetTextExtent('+Z'),
                '-Z':dc.GetTextExtent('-Z')
            }
        elif self.current_mode=='Axial':
            return {
                '+X':dc.GetTextExtent('+X'),
                '-X':dc.GetTextExtent('-X'),
                '+Y':dc.GetTextExtent('+Y'),
                '-Y':dc.GetTextExtent('-Y')
            }
    @property
    def line_axis(self):
        hw=self.size[0]/2 #half width
        hh=self.size[1]/2 #half height
        ac=self.axis_coords
        Xx1=ac['X'][0][0] # X axis line start coord x
        Xy1=ac['X'][0][1] # X axis line start coord y
        Xx2=ac['X'][1][0] # X axis line end coord x
        Xy2=ac['X'][1][1] # X axis line end coord y
        Yx1=ac['Y'][0][0] # Y axis line start coord x
        Yy1=ac['Y'][0][1] # Y axis line start coord y
        Yx2=ac['Y'][1][0] # Y axis line end coord x
        Yy2=ac['Y'][1][1] # Y axis line end coord y
        Zx1=ac['Z'][0][0] # Z axis line start coord x
        Zy1=ac['Z'][0][1] # Z axis line start coord y
        Zx2=ac['Z'][1][0] # Z axis line end coord x
        Zy2=ac['Z'][1][1] # Z axis line end coord y
        if self.current_mode=='Cube':
            return {
                'X':(wx.Point(hw*Xx1,hh*Xy1),wx.Point(hw*Xx2,hh*Xy2)),
                'Y':(wx.Point(hw*Yx1,hh*Yy1),wx.Point(hw*Yx2,hh*Yy2)),
                'Z':(wx.Point(hw*Zx1,hh*Zy1), wx.Point(hw*Zx2,hh*Zy2))
            }
        elif self.current_mode=='Axial':
            return {
                'X':(wx.Point(hw*Xx1,hh*Xy1),wx.Point(hw*Xx2,hh*Xy2)),
                'Y':(wx.Point(hw*Yx1,hh*Yy1),wx.Point(hw*Yx2,hh*Yy2))
            }
        return
    def text_axis(self,dc):
        hw=self.size[0]/2 #half width
        hh=self.size[1]/2 #half height
        cw=self.size[0]/2 #center width
        ch=self.size[1]/2 #center height
        ac=self.axis_coords
        Xx1=ac['X'][0][0] # X axis line start coord x
        Xy1=ac['X'][0][1] # X axis line start coord y
        Xx2=ac['X'][1][0] # X axis line end coord x
        Xy2=ac['X'][1][1] # X axis line end coord y
        Yx1=ac['Y'][0][0] # Y axis line start coord x
        Yy1=ac['Y'][0][1] # Y axis line start coord y
        Yx2=ac['Y'][1][0] # Y axis line end coord x
        Yy2=ac['Y'][1][1] # Y axis line end coord y
        Zx1=ac['Z'][0][0] # Z axis line start coord x
        Zy1=ac['Z'][0][1] # Z axis line start coord y
        Zx2=ac['Z'][1][0] # Z axis line end coord x
        Zy2=ac['Z'][1][1] # Z axis line end coord y
        text_sizes=self.text_sizes(dc)
        nXx=text_sizes['-X'][0] # Negative X Axis x coordinate
        nXy=text_sizes['-X'][1] # Negative X Axis y coordinate
        pXx=text_sizes['+X'][0] # Positive X Axis x coordinate
        pXy=text_sizes['+X'][1] # Positive X Axis y coordinate
        nYx=text_sizes['-Y'][0] # Negative Y Axis x coordinate
        nYy=text_sizes['-Y'][1] # Negative Y Axis y coordinate
        pYx=text_sizes['+Y'][0] # Positive Y Axis x coordinate
        pYy=text_sizes['+Y'][1] # Positive Y Axis y coordinate
        nZx=text_sizes['-Z'][0] # Negative Z Axis x coordinate
        nZy=text_sizes['-Z'][1] # Negative Z Axis y coordinate
        pZx=text_sizes['+Z'][0] # Positive Z Axis x coordinate
        pZy=text_sizes['+Z'][1] # Positive Z Axis y coordinate
        if self.current_mode=='Cube':
            return {
                'X':(wx.Point((hw*Xx1)+cw,(hh*Xy1)+ch-(nXy/2)),
                    wx.Point((hw*Xx2)+cw-pXx-(pXx/2),(hh*Xy2)+ch-(pXy/2))),
                'Y':(wx.Point((hw*Yx2)+cw-nYx-(nYx/2),(hh*Yy2)+ch-pYy),
                    wx.Point((hw*Yx1)+cw,(hh*Yy1)+ch)),
                'Z':(wx.Point((hw*Zx1)+cw-nZx,(hh*Zy1)+ch),
                    wx.Point((hw*Zx2)+cw,(hh*Zy2)+ch-pZy))
            }
        elif self.current_mode=='Axial':
            return {
                'X':(wx.Point((hw*Xx1)+cw,(hh*Xy1)+ch-(nXy/2)),
                    wx.Point((hw*Xx2)+cw-pXx,(hh*Xy2)+ch-(pXy/2))),
                'Y':(wx.Point((hw*Yx1)+cw-nYx-(nYx/2),(hh*Yy1)+ch-nYy),
                    wx.Point((hw*Yx2)+cw,(hh*Yy2)+ch))
            }
    def Draw(self):
        if self.current_mode=='Cube':
            self.DrawCubic()
        elif self.current_mode=='Axial':
            self.DrawAxial()
        else:
            self.DrawNone()
    def OnSize(self):
        self.image=wx.Bitmap(self.size)
        self.Draw()
    def SetMode(self,choice):
        self.current_mode=choice
        self.OnSize()
    def DrawCubic(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.image)
        dc.SetBackground(self.parent.brushes['background'])
        dc.Clear()
        line_axis=self.line_axis
        text_axis=self.text_axis(dc)
        for axis in ['X','Y','Z']:
            pen=None
            if axis=='X':
                pen=wx.Pen(wx.Colour('green'))
            elif axis=='Y':
                pen=wx.Pen(wx.Colour('red'))
            else:
                pen=wx.Pen(wx.Colour('blue'))
            dc.SetPen(pen)
            dc.DrawLines(line_axis[axis],xoffset=self.center_x,yoffset=self.center_y)
            dc.DrawText('-{}'.format(axis),text_axis[axis][0])
            dc.DrawText('+{}'.format(axis),text_axis[axis][1])
    def DrawAxial(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.image)
        dc.SetBackground(self.parent.brushes['background'])
        dc.Clear()
        line_axis=self.line_axis
        text_axis=self.text_axis(dc)
        for axis in ['X','Y']:
            dc.SetPen(self.pen_axis[axis])
            dc.DrawLines(line_axis[axis],xoffset=self.center_x,yoffset=self.center_y)
            dc.DrawText('-{}'.format(axis),text_axis[axis][0])
            dc.DrawText('+{}'.format(axis),text_axis[axis][1])
    def DrawNone(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.image)
        dc.SetBackground(self.parent.brushes['background'])
        dc.Clear()
class SelectedTileControlPanel(Panel):
    def __init__(self,parent):
        Panel.__init__(self,parent,main_sizer_orientation=wx.VERTICAL)
        self.selected_tile_label=wx.StaticText(self,label='Selected Tile')
        self.selected_tile_x_label=wx.StaticText(self,label='X:')
        self.selected_tile_x_control=wx.SpinCtrl(self,min=-100)
        self.selected_tile_y_label=wx.StaticText(self,label='Y:')
        self.selected_tile_y_control=wx.SpinCtrl(self,min=-100)
        self.selected_tile_z_label=wx.StaticText(self,label='Z:')
        self.selected_tile_z_control=wx.SpinCtrl(self,min=-100)
        self.selected_tile_coord_sizer=wx.BoxSizer()
        self.selected_tile_coord_sizer.Add(self.selected_tile_x_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_x_control,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_y_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_y_control,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_z_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_z_control,0,wx.EXPAND)
        self.main_sizer.Add(self.selected_tile_label,0,wx.EXPAND)
        self.main_sizer.Add(self.selected_tile_coord_sizer,0,wx.EXPAND)
        self.selected_tile_type_control=wx.RadioBox(self,choices=['Movement Cost 1','Movement Cost 2','Not Passable'])
        self.main_sizer.Add(self.selected_tile_type_control,0,wx.EXPAND)
class HexMapControlPanel(Panel):
    def __init__(self,parent):
        Panel.__init__(self,parent,main_sizer_orientation=wx.VERTICAL)
        self.events=self.parent.events
        self.radius_label=wx.StaticText(self,label='Radius:')
        self.radius_control=wx.SpinCtrl(self,value='1')
        self.radius_sizer=wx.BoxSizer()
        self.radius_sizer.Add(self.radius_label,1,wx.EXPAND)
        self.radius_sizer.Add(self.radius_control,1,wx.EXPAND)
        self.main_sizer.Add(self.radius_sizer,0,wx.EXPAND)
        self.notation_type_control=RadioBox(self,choices=['None','Cube','Axial'],name='Notation-Type-Control')
        self.main_sizer.Add(self.notation_type_control,0,wx.EXPAND)
        self.selected_tile_control_panel=SelectedTileControlPanel(self)
        self.main_sizer.Add(self.selected_tile_control_panel,0,wx.EXPAND)
class MapRenderPanel(RenderPanel):
    def __init__(self,parent):
        RenderPanel.__init__(self,parent)
#        self.selected_tile=Cube(0,0,0)
#        self.hovered_tile=Cube(0,0,0)
        self.notation_type='None'
        self.text_colours['X']=wx.Colour('green')
        self.text_colours['Y']=wx.Colour('pink')
        self.text_colours['Z']=wx.Colour(30,144,155)
        self.pens['x']=wx.Pen('green')
        self.pens['y']=wx.Pen('pink')
        self.pens['z']=wx.Pen(wx.Colour(30,144,255))
        self.pens['q']=wx.Pen('green')
        self.pens['r']=wx.Pen('pink')
        self.pens['hex_outline']=wx.Pen('black')
        self.brushes['background']=wx.Brush('white')
        self.brushes['not_passable_tile']=wx.Brush(wx.Colour(0,0,0))
        self.brushes['movement_cost_1_tile']=wx.Brush(wx.Colour(255,255,255))
        self.brushes['movement_cost_2_tile']=wx.Brush(wx.Colour(139,69,19))
#        self.hexmap_bitmap=HexmapBitmap(self)
        self.axis_bitmap=AxisBitmap(self)
#        self.Show(True)
    @property
    def hexagon(self):
        return [(((100)*np.cos((np.pi/180)*(60*i))),
                 ((100)*np.sin((np.pi/180)*(60*i)))) for i in range(0,6)]
    def Draw(self,dc):
        dc.DrawBitmap(self.axis_bitmap.image,10,self.axis_bitmap.y)
    def wxOnSize(self,event):
        self.axis_bitmap.OnSize()
        RenderPanel.wxOnSize(self,event)
#    def init(self,hexmap,lock):
#        self.hexmap=hexmap
#        self.lock=lock
#        self.dc=Observable(wx.MemoryDC())
#        self.dc.addCallback(self.Draw)
#        self.OnSize(None)
#        self.Draw(self.dc.get())
#        self.Bind(wx.EVT_SIZE,self.OnSize)
#        self.Bind(wx.EVT_PAINT,self.OnPaint)
#        self.Bind(wx.EVT_MOUSE_EVENTS,self.UpdateMouse)
#    def OnPaint(self,event):
#        wx.BufferedPaintDC(self,self.buffer)
#    def OnSize(self,event):
#        self.buffer=wx.Bitmap(*self.GetSize())
#        self.hexmap_bitmap.OnSize()
#        self.axis_bitmap.OnSize()
#        self.UpdateDrawing()
#    def Draw(self,dc):
#        dc.SelectObject(self.buffer)
#        dc.SetBackground(self.brushes['background'])
#        dc.Clear()
#        self.lock.acquire()
#        self.hexmap_bitmap.DrawHexmap()
#        self.hexmap_bitmap.Draw(dc)
#        self.axis_bitmap.Draw(dc)
#        self.lock.release()
#    def UpdateDrawing(self):
#        self.dc.set(wx.MemoryDC())
#        self.Refresh(eraseBackground=False)
#        self.Update()
#    def UpdateMouse(self,event):
#        self.old_mouse_coord=self.new_mouse_coord
#        self.new_mouse_coord=(event.GetX(),event.GetY())
#        center_x,center_y=(self.GetSize())/2
#        point=(self.new_mouse_coord[0]-center_x-self.offset_coord[0],
#               self.new_mouse_coord[1]-center_y-self.offset_coord[1])
#        self.hovered_tile=pixel_to_hex(point)
#        if event.Dragging():
#            self.is_dragging=True
#            self.lock.acquire()
#            self.offset_coord=(self.offset_coord[0]+(self.new_mouse_coord[0]-self.old_mouse_coord[0]),self.offset_coord[1]+(self.new_mouse_coord[1]-self.old_mouse_coord[1]))
#            self.lock.release()
#            self.UpdateDrawing()
#        elif event.LeftDown():
#            self.is_left_click_down=True
#        elif event.LeftUp():
#            self.is_dragging=False
#            self.is_left_click_down=False
class MainFrame(Frame):
    def __init__(self,events,title="Hexmap Demo"):
        Frame.__init__(self,events,title)
        self.CreateStatusBar()
        self.hexmap_control_panel=HexMapControlPanel(self)
        self.render_panel=MapRenderPanel(self)
        self.inner_sizer=wx.BoxSizer()
        self.main_sizer.Add(self.inner_sizer,1,wx.EXPAND)
        self.inner_sizer.Add(self.hexmap_control_panel,0,wx.EXPAND)
        self.inner_sizer.Add(self.render_panel,1,wx.EXPAND)
        self.Layout()
        self.Fit()
class App(BaseApp):
    def __init__(self):
        BaseApp.__init__(self)
        self.radius=1
        #self.hexmap=RadialMap(self.radius)
        self.main_frame=MainFrame(self.events)
    def Initialise(self,event):
        self.main_frame.Show(True)
        self.MainLoop()
#        self.main_frame.init(self.hexmap,self.lock)
#        self.draw_thread=threading.Thread(target=self.drawLoop)
#        self.main_frame.hexmap_control_panel.radius_control.Bind(wx.EVT_SPINCTRL, self.SetRadius)
        #self.main_frame.hexmap_control_panel.zoom_control.Bind(wx.EVT_SPINCTRL, self.SetZoom)
#        self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_x_control.Bind(wx.EVT_SPINCTRL, self.SetSelectedTile)
#        self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_y_control.Bind(wx.EVT_SPINCTRL, self.SetSelectedTile)
#        self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_z_control.Bind(wx.EVT_SPINCTRL, self.SetSelectedTile)
#        self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.Bind(wx.EVT_RADIOBOX, self.SetSelectedTileType)
#        self.main_frame.render_panel.Bind(wx.EVT_LEFT_DOWN,self.RenderPanelLeftMouseDown)
#        self.main_frame.hexmap_control_panel.notation_type_control.Bind(wx.EVT_RADIOBOX, self.SetNotationType)
#    def SetRadius(self,event):
#        self.radius=self.main_frame.hexmap_control_panel.radius_control.GetValue()
#        self.hexmap.populateMap(self.radius)
    #def SetZoom(self,event):
        #self.main_frame.render_panel.zoom=self.main_frame.hexmap_control_panel.zoom_control.GetValue()
#    def SetSelectedTile(self,event):
#        x=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_x_control.GetValue()
#        y=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_y_control.GetValue()
#        z=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_z_control.GetValue()
#        self.main_frame.render_panel.selected_tile=Cube(x,y,z)
#        tile=self.hexmap[Cube(x,y,z)]
#        if tile!=False:
#            if not tile.isPassable:
#                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(2)
#            elif tile.movement_cost==1:
#                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(0)
#            elif tile.movement_cost==2:
#                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(1)
#    def SetSelectedTileType(self,event):
#        choice=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.GetString(self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.GetSelection())
#        x=self.main_frame.render_panel.selected_tile.x
#        y=self.main_frame.render_panel.selected_tile.y
#        z=self.main_frame.render_panel.selected_tile.z
#        tile=self.hexmap[Cube(x,y,z)]
#        if tile!=False:
#            if choice=='Movement Cost 1':
#                tile.movement_cost=1
#            elif choice=='Movement Cost 2':
#                tile.movement_cost=2
#            if choice=='Not Passable':
#                tile.isPassable=False
#    def RenderPanelLeftMouseDown(self,event):
#        tile=self.hexmap[Cube(self.main_frame.render_panel.hovered_tile.x,self.main_frame.render_panel.hovered_tile.y,self.main_frame.render_panel.hovered_tile.z)]
#        if tile!=False:
#            self.main_frame.render_panel.selected_tile=self.main_frame.render_panel.hovered_tile
#            self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_x_control.SetValue(self.main_frame.render_panel.selected_tile.x)
#            self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_y_control.SetValue(self.main_frame.render_panel.selected_tile.y)
#            self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_z_control.SetValue(self.main_frame.render_panel.selected_tile.z)
#            if tile.isPassable==False:
#                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(2)
#            elif tile.movement_cost==1:
#                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(0)
#            elif tile.movement_cost==2:
#                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(1)
#    def SetNotationType(self,event):
#        choice=self.main_frame.hexmap_control_panel.notation_type_control.GetString(self.main_frame.hexmap_control_panel.notation_type_control.GetSelection())
#        self.main_frame.render_panel.notation_type=choice
#        self.main_frame.render_panel.axis_bitmap.SetMode(choice)
if __name__=='__main__':
    mp.freeze_support()
    app=App()
    app.events.CallEvent(InitialiseEvent())
    del app
exit()
