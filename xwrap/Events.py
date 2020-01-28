import multiprocessing as mp
from collections import OrderedDict
INITIALISE_EVENT='Initialise-Event'
MAIN_LOOP_EVENT='Main-Loop-Event'
CLOSE_EVENT='Close-Event'
class Event:
    def __init__(self,name,resfunc):
        self.name=name
        self.resfunc=resfunc
class InitialiseEvent(Event):
    def __init__(self,resfunc=None):
        Event.__init__(self,INITIALISE_EVENT,resfunc)
class MainLoopEvent(Event):
    def __init__(self,resfunc=None):
        Event.__init__(self,MAIN_LOOP_EVENT,resfunc)
class CloseEvent(Event):
    def __init__(self,resfunc=None):
        Event.__init__(self,CLOSE_EVENT,resfunc)
        self.running=False
class Data:
    def __init__(self,id,name,data):
        self.id=id
        self.name=name
        self.data=data
class DataModel:
    def __init__(self):
        self.data=[]
    def Bind(self,name,data):
        self.data.append(Data(len(self.data),name,data))
    def GetByName(self,name):
        for data in self.data:
            if data.name==name:
                return data
    def GetByID(self,id):
        return self.data[id]
    def __getitem__(self,key):
        if isinstance(key,str):
            if key.isdigit():
                return self.GetByID(int(key))
            else:
                return self.GetByName(key)
        elif isinstance(key,int):
            return self.GetByID(key)
        return None
    def __len__(self):
        return len(self.data)
class Events:
    def __init__(self):
        self.processes=[]
        self.cpu_count=mp.cpu_count()
        self.task_queue=mp.Queue()
        self.done_queue=mp.Queue()
        self.running=True
        self.task_queue_index=0
        self.done_queue_index=0
        self.events={}
        self.data_model=DataModel()
    def Initialise(self):
        for i in range(self.cpu_count):
            process=mp.Process(target=self.Worker,args=(self.task_queue,self.done_queue))
            process.start()
            self.processes.append(process)
    @property
    def num_processes(self):
        return len(self.processes)
    def AddEvent(self,key):
        self.events[key]=OrderedDict()
    def Bind(self,event_key,func):
        self.events[event_key][func]=0
    def BindData(self,name,data):
        self.data_model.Bind(name,data)
    def CallEvent(self,event):
        if self.running:
            for func in self.events[event.name]:
                task=func(event)
                self.task_queue.put(task)
    def Close(self):
        for process in self.processes:
            process.terminate()
            process.join()
    def ProcessDoneQueue(self):
        try:
            output=self.done_queue.get(timeout=0.1)
        except:
            output=None
        return output
    def Worker(cls,input,output):
        running=True
        while running:
            event=input.get()
            if event!=None:
                if hasattr(event,'do'):
                    event.do()
                if hasattr(event,'running'):
                    running=event.running
            output.put((mp.current_process().name,mp.current_process().pid,event))
        return
    Worker=classmethod(Worker)
