import wx
from . import Events as e
import time
class CloseEvent(e.Event):
    def __init__(self):
        e.Event.__init__(self,e.CLOSE_EVENT,self.resfunc)
    def resfunc(self,events):
        events.running=False
class BaseApp:
    def __init__(self):
        self.app=wx.App()
        self.events=e.Events()
        self.events.AddEvent(e.INITIALISE_EVENT)
        self.events.Bind(e.INITIALISE_EVENT,self.OnInitialise)
        self.events.AddEvent(e.MAIN_LOOP_EVENT)
        self.events.AddEvent(e.CLOSE_EVENT)
        self.events.Bind(e.CLOSE_EVENT,self.OnClose)
    def OnInitialise(self):
        self.events.Initialise()
        self.Initialise()
    def MainLoop(self):
        self.events.MainLoop()
        wx.CallAfter(self.main_frame.Destroy)
    def OnClose(self):
        return CloseEvent()
