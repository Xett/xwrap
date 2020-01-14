from xwrap.App import BaseApp
from xwrap.Events import InitialiseEvent
from xwrap.View import Frame
import multiprocessing as mp
import wx
import xwrap.Events as e
import numpy as np
import math
PROCESS_TASKS_EVENT='Process-Tasks-Event'
class ProcessTask(e.Task):
    def __init__(self,event):
        e.Task.__init__(self,event,self.resfunc)
    def do(self):
        result=0
        angle_rad=math.radians(np.random.normal()*10)
        result+=math.tanh(angle_rad)/math.cosh(angle_rad)/(np.random.normal()*10)
        self.event.result=result
        self.event.name=mp.current_process().name
        self.event.pid=mp.current_process().pid
    def resfunc(self,events):
        events.data_model[self.event.output_text_control_id].data.AppendText('{} {} {}\n'.format(self.event.name,self.event.pid,self.event.result))
class ProcessTasksEvent(e.Event):
    def __init__(self,id):
        e.Event.__init__(self,PROCESS_TASKS_EVENT)
        self.output_text_control_id=id
class MainFrame(Frame):
    def __init__(self,events,title='Test App'):
        Frame.__init__(self,events,title)
        self.main_panel=wx.Panel(self,wx.ID_ANY)
        self.panel_sizer=wx.GridBagSizer(5,5)
        self.start_button=wx.Button(self.main_panel,wx.ID_ANY,"Start")
        self.Bind(wx.EVT_BUTTON,self.StartButton,self.start_button)
        self.start_button.SetDefault()
        self.start_button.SetToolTipString('Start the execution of tasks')
        self.start_button.ToolTip.Enable(True)
        self.output_text_control=wx.TextCtrl(self.main_panel,wx.ID_ANY,style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.events.BindData('MainFrame_OutputTextControl',self.output_text_control)
        self.panel_sizer.Add(self.start_button,(0,0),flag=wx.ALIGN_CENTER|wx.LEFT|wx.TOP|wx.RIGHT,border=5)
        self.panel_sizer.Add(self.output_text_control,(1,0),flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,border=5)
        self.panel_sizer.AddGrowableCol(0)
        self.panel_sizer.AddGrowableRow(1)
        self.main_panel.SetSizer(self.panel_sizer)
        self.main_sizer.Add(self.main_panel,1,wx.EXPAND)
    def StartButton(self,event):
        for i in range(self.events.num_processes):
            id=self.events.data_model['MainFrame_OutputTextControl'].id
            self.events.CallEvent(ProcessTasksEvent(id))
class TestApp(BaseApp):
    def __init__(self):
        BaseApp.__init__(self)
        self.events.AddEvent(PROCESS_TASKS_EVENT)
        self.events.Bind(PROCESS_TASKS_EVENT,self.ProcessTasks)
        self.main_frame=MainFrame(self.events)
    def Initialise(self,event):
        self.main_frame.Show(True)
        self.MainLoop()
    def ProcessTasks(self,event):
        return ProcessTask(event)
if __name__=="__main__":
    mp.freeze_support()
    test_app=TestApp()
    test_app.events.CallEvent(InitialiseEvent())
