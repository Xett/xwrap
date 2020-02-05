import wx
from .Events import *
import time
class BaseApp:
    def __init__(self):
        self.app=wx.App()
        self.events=Events()
        self.events.BindData('Application_Root',self)
        self.events.AddEvent(CLOSE_EVENT)
        self.events.Bind(CLOSE_EVENT,self.OnClose)
    def Start(self):
        self.events.Initialise()
        self.Initialise()
    def MainLoop(self):
        self.events.MainLoop()
        wx.CallAfter(self.main_frame.Destroy)
    def OnClose(self):
        return CloseEvent()
