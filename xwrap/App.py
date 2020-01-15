import wx
from . import Events as e
import time
class BaseApp:
    def __init__(self):
        self.app=wx.App()
        self.events=e.Events()
        self.events.AddEvent(e.INITIALISE_EVENT)
        self.events.Bind(e.INITIALISE_EVENT,self.OnInitialise)
        self.events.AddEvent(e.MAIN_LOOP_EVENT)
        self.events.AddEvent(e.CLOSE_EVENT)
        self.events.Bind(e.CLOSE_EVENT,self.OnClose)
    def OnInitialise(self,event):
        self.events.Initialise()
        self.Initialise(event)
    def MainLoop(self):
        self.running=True
        event_loop=wx.GUIEventLoop()
        wx.EventLoop.SetActive(event_loop)
        while self.running:
            self.events.CallEvent(e.MainLoopEvent(self))
            while self.events.done_queue.qsize()>0:
                output=self.events.ProcessDoneQueue()
                if output!=None:
                    if output[2]!=None:
                        output[2].resfunc(self.events)
            while event_loop.Pending():
                event_loop.Dispatch()
            event_loop.ProcessIdle()
        while event_loop.Pending():
            event_loop.Dispatch()
    def OnClose(self,event):
        while self.events.task_queue.qsize()>0 or self.events.done_queue.qsize()>0:
            time.sleep(0.1)
        self.running=False
        self.events.Close()
        wx.CallAfter(self.main_frame.Destroy)
        return e.CloseTask(event,self.events.Close)
