import wx
from .Events import *
from collections import OrderedDict
class Frame(wx.Frame):
    def __init__(self,events,title='Frame',size=(1920,1080)):
        wx.Frame.__init__(self,None,-1,title,size)
        self.events=events
        self.main_sizer=wx.BoxSizer()
        self.SetSizer(self.main_sizer)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
    def OnClose(self,event):
        self.events.CallEvent(CLOSE_EVENT)
class Panel(wx.Panel):
    def __init__(self,parent,main_sizer_orientation=wx.HORIZONTAL):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.events=self.parent.events
        self.main_sizer=wx.BoxSizer(orient=main_sizer_orientation)
        self.SetSizer(self.main_sizer)
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
class ListCtrl(wx.ListCtrl):
    def __init__(self,parent,name,insert_event_name,select_event_name):
        wx.ListCtrl.__init__(self,parent)
        self.parent=parent
        self.name=name
        self.insert_event_name=insert_event_name
        self.select_event_name=select_event_name
        self.events=self.parent.events
        self.events.AddEvent(self.insert_event_name)
        self.events.AddEvent(self.select_event_name)
        self.events.BindData(self.name,self)
        self.Bind(wx.EVT_LIST_INSERT_ITEM,self.wxOnItemInserted)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.wxOnItemSelected)
    def wxOnItemInserted(self,event):
        self.events.CallEvent(self.insert_event_name)
    def wxOnItemSelected(self,event):
        self.events.CallEvent(self.select_event_name)
