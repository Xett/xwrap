import wx
from xwrap.App import *
from xwrap.Events import *
from xwrap.View import *
CELL_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT='Cell-Render-Panel-Mouse-Left-Down-Event'
class Cell:
    def __init__(self,x,y,state=False):
        self.x=x
        self.y=y
        self.state=state
    def flip(self):
        self.state=not self.state
class CellGrid:
    def __init__(self,events,width=10,height=10):
        self.events=events
        self.width=width
        self.height=height
        self.data={}
        self.events.BindData('Cell-Grid',self)
        self.populate()
    def populate(self):
        for i in range(1,self.width+1):
            for j in range(1,self.height+1):
                self.data['{}-{}'.format(j,i)]=Cell(j,i)
class CellGridBitmap(Bitmap):
    def __init__(self,parent):
        Bitmap.__init__(self,parent,'Cell-Grid-Bitmap')
    @property
    def width(self):
        return self.parent.GetSize()[0]
    @property
    def height(self):
        return self.parent.GetSize()[1]
    def Draw(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.image)
        dc.SetBackground(wx.Brush(wx.Colour('white')))
        dc.Clear()
        num_cells_x=self.events.data_model['Cell-Grid'].data.width
        num_cells_y=self.events.data_model['Cell-Grid'].data.height
        self.cell_width=self.width/num_cells_x
        self.cell_height=self.height/num_cells_y
        for i in range(num_cells_x):
            for j in range(num_cells_y):
                x=j*self.cell_width
                y=i*self.cell_height
                cell=self.events.data_model['Cell-Grid'].data.data['{}-{}'.format(j+1,i+1)]
                if cell.state:# Live
                    dc.SetBrush(wx.Brush(wx.Colour('black')))
                elif cell.state==False: # Dead
                    dc.SetBrush(wx.Brush(wx.Colour('white')))
                dc.DrawRectangle(x,y,self.cell_width,self.cell_height)
class CellRenderPanelMouseLeftDownEvent(Event):
    def __init__(self,cell_grid_id,cell_render_panel_id):
        Event.__init__(self,CELL_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT,self.resfunc)
        self.cell_grid_id=cell_grid_id
        self.cell_render_panel_id=cell_render_panel_id
    def resfunc(self,events):
        cell_grid=events.data_model[self.cell_grid_id].data
        cell_render_panel=events.data_model[self.cell_render_panel_id].data
        mouse_coord=cell_render_panel.new_mouse_coord
        x=int(mouse_coord[0]/(cell_render_panel.GetSize()[0]/cell_grid.width))+1
        y=int(mouse_coord[1]/(cell_render_panel.GetSize()[1]/cell_grid.height))+1
        cell=cell_grid.data['{}-{}'.format(x,y)]
        cell.flip()
        cell_render_panel.wxOnSize(None)
class CellRenderPanel(RenderPanel):
    def __init__(self,parent,name="Cell-Render-Panel"):
        RenderPanel.__init__(self,parent,name)
        self.cell_grid_bitmap=CellGridBitmap(self)
    def Draw(self,dc):
        dc.DrawBitmap(self.cell_grid_bitmap.image,self.cell_grid_bitmap.x,self.cell_grid_bitmap.y)
    def wxOnSize(self,event):
        self.cell_grid_bitmap.OnSize()
        RenderPanel.wxOnSize(self,event)
class MainFrame(Frame):
    def __init__(self,events,title="Cellular Automation"):
        Frame.__init__(self,events,title)
        self.CreateStatusBar()
        self.render_panel=CellRenderPanel(self)
        self.main_sizer.Add(self.render_panel,1,wx.EXPAND)
        self.Layout()
        self.Fit()
class App(BaseApp):
    def __init__(self):
        BaseApp.__init__(self)
        self.cell_grid=CellGrid(self.events)
        self.main_frame=MainFrame(self.events)
        self.events.Bind(CELL_RENDER_PANEL_MOUSE_LEFT_DOWN_EVENT,self.OnClick)
    def Initialise(self):
        self.main_frame.Show(True)
        self.MainLoop()
    def OnClick(self):
        cell_grid_id=self.events.data_model['Cell-Grid'].id
        cell_render_panel_id=self.events.data_model['Cell-Render-Panel'].id
        return CellRenderPanelMouseLeftDownEvent(cell_grid_id,cell_render_panel_id)
if __name__=='__main__':
    mp.freeze_support()
    app=App()
    app.events.CallEvent(INITIALISE_EVENT)
    del app
exit()
