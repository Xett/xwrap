import wx
from .Events import *
import time
class CloseEvent(Event):
    def __init__(self):
        Event.__init__(self,CLOSE_EVENT,self.resfunc)
    def resfunc(self,events):
        events.running=False
class BaseApp:
    def __init__(self):
        self.app=wx.App()
        self.events=Events()
        self.events.AddEvent(INITIALISE_EVENT)
        self.events.Bind(INITIALISE_EVENT,self.OnInitialise)
        self.events.AddEvent(MAIN_LOOP_EVENT)
        self.events.AddEvent(CLOSE_EVENT)
        self.events.Bind(CLOSE_EVENT,self.OnClose)
    def OnInitialise(self):
        self.events.Initialise()
        self.Initialise()
    def MainLoop(self):
        self.events.MainLoop()
        wx.CallAfter(self.main_frame.Destroy)
    def OnClose(self):
        return CloseEvent()
