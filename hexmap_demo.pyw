import wx
import numpy as np
import math
import copy
from xwrap.App import *
from xwrap.Events import *
from xwrap.View import *
from collections import OrderedDict
from hexmap import Iterators
from hexmap.Coords import Cube
from hexmap.Coords import Axial
from hexmap.Maps import RadialMap
NOTATION_TYPE_CONTROL_CHOICE_CHANGED_EVENT='Notation-Type-Control-Choice-Changed-Event'
SELECTED_TILE_TYPE_CONTROL_CHOICE_CHANGED_EVENT='Selected-Tile-Type-Control-Choice-Changed-Event'
RADIUS_SPIN_CONTROL_CHANGE_EVENT='Radius-Spin-Control-Change-Event'
SET_SELECTED_TILE_EVENT='Set-Selected-Tile-Event'
MAP_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT='Map-Render-Panel-Mouse-Left-Down-Event'
MAP_RENDER_PANEL_MOUSE_MOTION='Map-Render-Panel-Mouse-Motion-Event'
def pixel_to_hex(point):
    q=((2./3)*point[0])/100
    r=(((-1./3)*point[0])+(np.sqrt(3)/3)*point[1])/100
    return round(Axial(q,r).toCube())
class NotationTypeControlChoiceChangedEvent(Event):
    def __init__(self,notation_type_control_id,map_render_panel_id):
        Event.__init__(self,NOTATION_TYPE_CONTROL_CHOICE_CHANGED_EVENT,self.resfunc)
        self.notation_type_control_id=notation_type_control_id
        self.map_render_panel_id=map_render_panel_id
    def resfunc(self,events):
        choice=events.data_model[self.notation_type_control_id].data.GetString(events.data_model[self.notation_type_control_id].data.GetSelection())
        events.data_model[self.map_render_panel_id].data.SetNotationType(choice)
class SelectedTileTypeControlChoiceChangedEvent(Event):
    def __init__(self,selected_tile_type_control_id,map_render_panel_id,hexmap_id):
        Event.__init__(self,SELECTED_TILE_TYPE_CONTROL_CHOICE_CHANGED_EVENT,self.resfunc)
        self.selected_tile_type_control_id=selected_tile_type_control_id
        self.map_render_panel_id=map_render_panel_id
        self.hexmap_id=hexmap_id
    def resfunc(self,events):
        choice=events.data_model[self.selected_tile_type_control_id].data.GetString(events.data_model[self.selected_tile_type_control_id].data.GetSelection())
        selected_tile=events.data_model[self.map_render_panel_id].data.selected_tile
        hexmap=events.data_model[self.hexmap_id].data
        x=selected_tile.x
        y=selected_tile.y
        z=selected_tile.z
        tile=hexmap[Cube(x,y,z)]
        if tile!=False:
            if choice=='Movement Cost 1':
                tile.movement_cost=1
            elif choice=='Movement Cost 2':
                tile.movement_cost=2
            if choice=='Not Passable':
                tile.isPassable=False
            if not tile.isPassable:
                events.data_model[self.selected_tile_type_control_id].data.SetSelection(2)
            elif tile.movement_cost==1:
                events.data_model[self.selected_tile_type_control_id].data.SetSelection(0)
            elif tile.movement_cost==2:
                events.data_model[self.selected_tile_type_control_id].data.SetSelection(1)
class RadiusSpinControlChangeEvent(Event):
    def __init__(self,radius_spin_control_id,radius_id,hexmap_id,map_render_panel_id):
        Event.__init__(self,RADIUS_SPIN_CONTROL_CHANGE_EVENT,self.resfunc)
        self.radius_spin_control_id=radius_spin_control_id
        self.radius_id=radius_id
        self.hexmap_id=hexmap_id
        self.map_render_panel_id=map_render_panel_id
    def resfunc(self,events):
        radius=events.data_model[self.radius_spin_control_id].data.GetValue()
        events.data_model[self.radius_id].data=radius
        events.data_model[self.hexmap_id].data.populateMap(radius)
        events.data_model[self.map_render_panel_id].data.wxOnSize(None)
class SetSelectedTileEvent(Event):
    def __init__(self,selected_tile_x_spin_control_id,selected_tile_y_spin_control_id,selected_tile_z_spin_control_id,hexmap_id,map_render_panel_id):
        Event.__init__(self,SET_SELECTED_TILE_EVENT,self.resfunc)
        self.selected_tile_x_spin_control_id=selected_tile_x_spin_control_id
        self.selected_tile_y_spin_control_id=selected_tile_y_spin_control_id
        self.selected_tile_z_spin_control_id=selected_tile_z_spin_control_id
        self.hexmap_id=hexmap_id
        self.map_render_panel_id=map_render_panel_id
    def resfunc(self,events):
        x=events.data_model[self.selected_tile_x_spin_control_id].data.GetValue()
        y=events.data_model[self.selected_tile_y_spin_control_id].data.GetValue()
        z=events.data_model[self.selected_tile_z_spin_control_id].data.GetValue()
        events.data_model[self.map_render_panel_id].data.selected_tile=Cube(x,y,z)
        events.data_model[self.map_render_panel_id].data.wxOnSize(None)
class MapRenderPanelMouseLeftDownEvent(Event):
    def __init__(self,selected_tile_x_spin_control_id,selected_tile_y_spin_control_id,selected_tile_z_spin_control_id,selected_tile_type_control_id,hexmap_id,map_render_panel_id):
        Event.__init__(self,MAP_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT,self.resfunc)
        self.selected_tile_x_spin_control_id=selected_tile_x_spin_control_id
        self.selected_tile_y_spin_control_id=selected_tile_y_spin_control_id
        self.selected_tile_z_spin_control_id=selected_tile_z_spin_control_id
        self.selected_tile_type_control_id=selected_tile_type_control_id
        self.hexmap_id=hexmap_id
        self.map_render_panel_id=map_render_panel_id
    def resfunc(self,events):
        map_render_panel=events.data_model[self.map_render_panel_id].data
        selected_tile_x_spin_control=events.data_model[self.selected_tile_x_spin_control_id].data
        selected_tile_y_spin_control=events.data_model[self.selected_tile_y_spin_control_id].data
        selected_tile_z_spin_control=events.data_model[self.selected_tile_z_spin_control_id].data
        selected_tile_type_control=events.data_model[self.selected_tile_type_control_id].data
        hexmap=events.data_model[self.hexmap_id].data
        hovered_tile=map_render_panel.hovered_tile
        hx=hovered_tile.x
        hy=hovered_tile.y
        hz=hovered_tile.z
        htile=hexmap[Cube(hx,hy,hz)]
        if htile!=False:
            map_render_panel.selected_tile=map_render_panel.hovered_tile
            selected_tile_x_spin_control.SetValue(hx)
            selected_tile_y_spin_control.SetValue(hy)
            selected_tile_z_spin_control.SetValue(hz)
            if htile.isPassable==False:
                selected_tile_type_control.SetSelection(2)
            elif htile.movement_cost==1:
                selected_tile_type_control.SetSelection(0)
            elif htile.movement_cost==2:
                selected_tile_type_control.SetSelection(1)
            map_render_panel.hexmap_bitmap.Draw()
            map_render_panel.UpdateDrawing()
class MapRenderPanelMouseMotionEvent(Event):
    def __init__(self,hexmap_id,map_render_panel_id):
        Event.__init__(self,MAP_RENDER_PANEL_MOUSE_MOTION,self.resfunc)
        self.hexmap_id=hexmap_id
        self.map_render_panel_id=map_render_panel_id
    def resfunc(self,events):
        hexmap=events.data_model[self.hexmap_id].data
        map_render_panel=events.data_model[self.map_render_panel_id].data
        hovered_tile=pixel_to_hex(map_render_panel.point)
        if hovered_tile!=False:
            map_render_panel.hovered_tile=hovered_tile
            map_render_panel.hexmap_bitmap.Draw()
            map_render_panel.UpdateDrawing()
class HexmapBitmap(Bitmap):
    def __init__(self,parent):
        Bitmap.__init__(self,parent,'Hexmap-Bitmap')
        self.use_offset=True
        self.anchor.SetCoordinates(0.5,0.5)
    @property
    def width(self):
        diameter=(self.events.data_model['Hexmap-Radius'].data*2)+(self.events.data_model['Hexmap-Radius'].data*2)
        return diameter*((100)*np.sqrt(3)/2)
    @property
    def height(self):
        diameter=(self.events.data_model['Hexmap-Radius'].data*2)+self.events.data_model['Hexmap-Radius'].data
        return diameter*((((100)*2)/4)*3)
    @property
    def size(self):
        return (self.width,self.height)
    @property
    def x(self):
        return 0
    @property
    def y(self):
        return 0
    def Draw(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.image)
        dc.SetBackground(self.parent.brushes['background'])
        dc.Clear()
        height=(100)*np.sqrt(3)
        width=(100)*2
        hexmap=self.events.data_model['Hexmap'].data
        draw_hovered=False
        draw_selected=False
        for x,y,z in Iterators.RingIterator(hexmap.radius,6):
            if (x,y,z)==(self.parent.hovered_tile.x,self.parent.hovered_tile.y,self.parent.hovered_tile.z):
                draw_hovered=True
                if (x,y,z)==(self.parent.selected_tile.x,self.parent.selected_tile.y,self.parent.selected_tile.z):
                    draw_selected=True
            x_coord=x*((width/4)*3)
            y_coord=(y*(height/2))-(z*(height/2))
            h=[(vert[0]+x_coord+self.center_x,
                vert[1]-y_coord+self.center_y) for vert in self.parent.hexagon]
            tile=hexmap[Cube(x,y,z)]
            dc.SetBrush(wx.Brush(wx.Colour(255,255,255)))
            dc.SetPen(self.parent.pens['hex_outline'])
            if (x,y,z)==(self.parent.selected_tile.x,self.parent.selected_tile.y,self.parent.selected_tile.z):
                dc.SetBrush(wx.Brush(wx.Colour(0,0,255)))
            elif tile!=False:
                if tile.isPassable==False:
                    dc.SetBrush(self.parent.brushes['not_passable_tile'])
                elif tile.movement_cost==1:
                    dc.SetBrush(self.parent.brushes['movement_cost_1_tile'])
                elif tile.movement_cost==2:
                    dc.SetBrush(self.parent.brushes['movement_cost_2_tile'])
            dc.DrawPolygon(h)
            text_sizes={
                'X':dc.GetTextExtent(str(x)),
                'Y':dc.GetTextExtent(str(y)),
                'Z':dc.GetTextExtent(str(z))
            }
            if self.parent.notation_type=='Cube':
                cubic_coordinates={
                    'X':(x_coord+self.center_x-(text_sizes['X'][0]/2),-y_coord+self.center_y-(height/3)),
                    'Y':(x_coord+self.center_x-(width/4),-y_coord+self.center_y+(height/4)-text_sizes['Y'][1]),
                    'Z':(x_coord+self.center_x+(width/4)-text_sizes['Z'][0],-y_coord+self.center_y+(height/4)-text_sizes['Z'][1])
                }
                for coord,axis in zip([x,y,z],['X','Y','Z']):
                    dc.SetTextForeground(self.parent.text_colours[axis])
                    dc.DrawText(str(coord),cubic_coordinates[axis][0],cubic_coordinates[axis][1])
            elif self.parent.notation_type=='Axial':
                axial_coordinates={
                    'X':(x_coord+self.center_x-(width/4),-y_coord+self.center_y-(text_sizes['X'][1]/2)),
                    'Y':(x_coord+self.center_x+(width/4)-text_sizes['Y'][0],-y_coord+self.center_y-(text_sizes['Y'][1]/2))
                }
                dc.DrawText(str(x),axial_coordinates['X'][0],axial_coordinates['X'][1])
                dc.DrawText(str(y),axial_coordinates['Y'][0],axial_coordinates['Y'][1])
        if draw_hovered:
            pen=wx.Pen(wx.Colour('gold'))
            pen.SetWidth(5)
            dc.SetPen(pen)
            if draw_selected:
                dc.SetBrush(wx.Brush(wx.Colour(0,0,255)))
            x_coord=self.parent.hovered_tile.x*((width/4)*3)
            y_coord=(self.parent.hovered_tile.y*(height/2))-(self.parent.hovered_tile.z*(height/2))
            h=[(vert[0]+x_coord+self.center_x,
                vert[1]-y_coord+self.center_y) for vert in self.parent.hexagon]
            dc.DrawPolygon(h)
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
                'Y':{0:(np.cos((np.pi/180)*210),np.sin((np.pi/180)*210)),1:(np.cos((np.pi/180)*30),np.sin((np.pi/180)*30))},
                'Z':{0:(np.cos((np.pi/180)*330),np.sin((np.pi/180)*330)),1:(np.cos((np.pi/180)*150),np.sin((np.pi/180)*150))}
            }
        elif self.current_mode=='Axial':
            return {
                'X':{0:(np.cos((np.pi/180)*180),np.sin((np.pi/180)*180)),1:(np.cos((np.pi/180)*0),np.sin((np.pi/180)*0))},
                'Y':{0:(np.cos((np.pi/180)*210),np.sin((np.pi/180)*210)),1:(np.cos((np.pi/180)*30),np.sin((np.pi/180)*30))}
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
        if self.current_mode=='Cube':
            Zx1=ac['Z'][0][0] # Z axis line start coord x
            Zy1=ac['Z'][0][1] # Z axis line start coord y
            Zx2=ac['Z'][1][0] # Z axis line end coord x
            Zy2=ac['Z'][1][1] # Z axis line end coord y
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
        text_sizes=self.text_sizes(dc)
        nXx=text_sizes['-X'][0] # Negative X Axis x coordinate
        nXy=text_sizes['-X'][1] # Negative X Axis y coordinate
        pXx=text_sizes['+X'][0] # Positive X Axis x coordinate
        pXy=text_sizes['+X'][1] # Positive X Axis y coordinate
        nYx=text_sizes['-Y'][0] # Negative Y Axis x coordinate
        nYy=text_sizes['-Y'][1] # Negative Y Axis y coordinate
        pYx=text_sizes['+Y'][0] # Positive Y Axis x coordinate
        pYy=text_sizes['+Y'][1] # Positive Y Axis y coordinate
        if self.current_mode=='Cube':
            Zx1=ac['Z'][0][0] # Z axis line start coord x
            Zy1=ac['Z'][0][1] # Z axis line start coord y
            Zx2=ac['Z'][1][0] # Z axis line end coord x
            Zy2=ac['Z'][1][1] # Z axis line end coord y
            nZx=text_sizes['-Z'][0] # Negative Z Axis x coordinate
            nZy=text_sizes['-Z'][1] # Negative Z Axis y coordinate
            pZx=text_sizes['+Z'][0] # Positive Z Axis x coordinate
            pZy=text_sizes['+Z'][1] # Positive Z Axis y coordinate
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
                    wx.Point((hw*Xx2)+cw-pXx-(pXx/2),(hh*Xy2)+ch-(pXy/2))),
                'Y':(wx.Point((hw*Yx2)+cw-nYx-(nYx/2),(hh*Yy2)+ch-pYy),
                    wx.Point((hw*Yx1)+cw,(hh*Yy1)+ch))
            }
    def Draw(self):
        if self.current_mode=='Cube':
            self.DrawCubic()
        elif self.current_mode=='Axial':
            self.DrawAxial()
        else:
            self.DrawNone()
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
        self.selected_tile_x_control=SpinCtrl(self,'Selected-Tile-X-Spin-Control',SET_SELECTED_TILE_EVENT,min=-100)
        self.selected_tile_y_label=wx.StaticText(self,label='Y:')
        self.selected_tile_y_control=SpinCtrl(self,'Selected-Tile-Y-Spin-Control',SET_SELECTED_TILE_EVENT,min=-100)
        self.selected_tile_z_label=wx.StaticText(self,label='Z:')
        self.selected_tile_z_control=SpinCtrl(self,'Selected-Tile-Z-Spin-Control',SET_SELECTED_TILE_EVENT,min=-100)
        self.selected_tile_coord_sizer=wx.BoxSizer()
        self.selected_tile_coord_sizer.Add(self.selected_tile_x_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_x_control,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_y_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_y_control,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_z_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_z_control,0,wx.EXPAND)
        self.main_sizer.Add(self.selected_tile_label,0,wx.EXPAND)
        self.main_sizer.Add(self.selected_tile_coord_sizer,0,wx.EXPAND)
        self.selected_tile_type_control=RadioBox(self,'Selected-Tile-Type-Control',SELECTED_TILE_TYPE_CONTROL_CHOICE_CHANGED_EVENT,choices=['Movement Cost 1','Movement Cost 2','Not Passable'])
        self.main_sizer.Add(self.selected_tile_type_control,0,wx.EXPAND)
class HexMapControlPanel(Panel):
    def __init__(self,parent):
        Panel.__init__(self,parent,main_sizer_orientation=wx.VERTICAL)
        self.events=self.parent.events
        self.radius_label=wx.StaticText(self,label='Radius:')
        self.radius_control=SpinCtrl(self,'Radius-Spin-Control',RADIUS_SPIN_CONTROL_CHANGE_EVENT,value='1')
        self.radius_sizer=wx.BoxSizer()
        self.radius_sizer.Add(self.radius_label,1,wx.EXPAND)
        self.radius_sizer.Add(self.radius_control,1,wx.EXPAND)
        self.main_sizer.Add(self.radius_sizer,0,wx.EXPAND)
        self.notation_type_control=RadioBox(self,'Notation-Type-Control',NOTATION_TYPE_CONTROL_CHOICE_CHANGED_EVENT,choices=['None','Cube','Axial'])
        self.main_sizer.Add(self.notation_type_control,0,wx.EXPAND)
        self.selected_tile_control_panel=SelectedTileControlPanel(self)
        self.main_sizer.Add(self.selected_tile_control_panel,0,wx.EXPAND)
class MapRenderPanel(RenderPanel):
    def __init__(self,parent,name):
        RenderPanel.__init__(self,parent,name)
        self.selected_tile=Cube(0,0,0)
        self.hovered_tile=Cube(0,0,0)
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
        self.axis_bitmap=AxisBitmap(self)
        self.hexmap_bitmap=HexmapBitmap(self)
    @property
    def hexagon(self):
        return [(((100)*np.cos((np.pi/180)*(60*i))),
                 ((100)*np.sin((np.pi/180)*(60*i)))) for i in range(0,6)]
    def SetNotationType(self,choice):
        self.axis_bitmap.SetMode(choice)
        self.UpdateDrawing()
    def Draw(self,dc):
        self.hexmap_bitmap.DrawToBuffer(dc)
        self.axis_bitmap.DrawToBuffer(dc)
    def wxOnSize(self,event):
        self.hexmap_bitmap.OnSize()
        self.axis_bitmap.OnSize()
        RenderPanel.wxOnSize(self,event)
class MainFrame(Frame):
    def __init__(self,events,title="Hexmap Demo"):
        Frame.__init__(self,events,title)
        self.CreateStatusBar()
        self.hexmap_control_panel=HexMapControlPanel(self)
        self.render_panel=MapRenderPanel(self,'Map-Render-Panel')
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
        self.events.BindData('Hexmap-Radius',self.radius)
        self.hexmap=RadialMap(self.radius)
        self.events.BindData('Hexmap',self.hexmap)
        self.main_frame=MainFrame(self.events)
        self.events.Bind(NOTATION_TYPE_CONTROL_CHOICE_CHANGED_EVENT,self.NotationTypeControlChoiceChanged)
        self.events.Bind(SELECTED_TILE_TYPE_CONTROL_CHOICE_CHANGED_EVENT,self.SelectedTileTypeControlChoiceChanged)
        self.events.Bind(RADIUS_SPIN_CONTROL_CHANGE_EVENT,self.RadiusSpinControlChange)
        self.events.AddEvent(SET_SELECTED_TILE_EVENT)
        self.events.Bind(SET_SELECTED_TILE_EVENT,self.SetSelectedTile)
        self.events.Bind(MAP_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT,self.MapRenderPanelMouseLeftDown)
        self.events.Bind(MAP_RENDER_PANEL_MOUSE_MOTION,self.MapRenderPanelMouseMotion)
    def Initialise(self):
        self.main_frame.Show(True)
        self.MainLoop()
    def NotationTypeControlChoiceChanged(self):
        notation_type_control_id=self.events.data_model['Notation-Type-Control'].id
        map_render_panel_id=self.events.data_model['Map-Render-Panel'].id
        return NotationTypeControlChoiceChangedEvent(notation_type_control_id,map_render_panel_id)
    def SelectedTileTypeControlChoiceChanged(self):
        selected_tile_type_control_id=self.events.data_model['Selected-Tile-Type-Control'].id
        map_render_panel_id=self.events.data_model['Map-Render-Panel'].id
        hexmap_id=self.events.data_model['Hexmap'].id
        return SelectedTileTypeControlChoiceChangedEvent(selected_tile_type_control_id,map_render_panel_id,hexmap_id)
    def RadiusSpinControlChange(self):
        radius_spin_control_id=self.events.data_model['Radius-Spin-Control'].id
        radius_id=self.events.data_model['Hexmap-Radius'].id
        hexmap_id=self.events.data_model['Hexmap'].id
        map_render_panel_id=self.events.data_model['Map-Render-Panel'].id
        return RadiusSpinControlChangeEvent(radius_spin_control_id,radius_id,hexmap_id,map_render_panel_id)
    def SetSelectedTile(self):
        selected_tile_x_spin_control_id=self.events.data_model['Selected-Tile-X-Spin-Control'].id
        selected_tile_y_spin_control_id=self.events.data_model['Selected-Tile-Y-Spin-Control'].id
        selected_tile_z_spin_control_id=self.events.data_model['Selected-Tile-Z-Spin-Control'].id
        hexmap_id=self.events.data_model['Hexmap'].id
        map_render_panel_id=self.events.data_model['Map-Render-Panel'].id
        return SetSelectedTileEvent(selected_tile_x_spin_control_id,selected_tile_y_spin_control_id,selected_tile_z_spin_control_id,hexmap_id,map_render_panel_id)
    def MapRenderPanelMouseLeftDown(self):
        selected_tile_x_spin_control_id=self.events.data_model['Selected-Tile-X-Spin-Control'].id
        selected_tile_y_spin_control_id=self.events.data_model['Selected-Tile-Y-Spin-Control'].id
        selected_tile_z_spin_control_id=self.events.data_model['Selected-Tile-Z-Spin-Control'].id
        selected_tile_type_control_id=self.events.data_model['Selected-Tile-Type-Control'].id
        hexmap_id=self.events.data_model['Hexmap'].id
        map_render_panel_id=self.events.data_model['Map-Render-Panel'].id
        return MapRenderPanelMouseLeftDownEvent(selected_tile_x_spin_control_id,selected_tile_y_spin_control_id,selected_tile_z_spin_control_id,selected_tile_type_control_id,hexmap_id,map_render_panel_id)
    def MapRenderPanelMouseMotion(self):
        hexmap_id=self.events.data_model['Hexmap'].id
        map_render_panel_id=self.events.data_model['Map-Render-Panel'].id
        return MapRenderPanelMouseMotionEvent(hexmap_id,map_render_panel_id)
if __name__=='__main__':
    mp.freeze_support()
    app=App()
    app.events.CallEvent(INITIALISE_EVENT)
    del app
exit()
