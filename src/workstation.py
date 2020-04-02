import cv2

RED = (211, 47, 47)
PURPLE = (186, 104, 200)
BLUE = (41, 182, 246)
LIME = (102, 255, 0)
YELLOW = (255, 255, 0)
GREY = (171, 178, 185)

class ObservableBarcode:
    rectangle = None
    _owner = None
    observers = {}
    b_id = None

    def __init__(self, b_id, b_rect, observers=None):
        self.b_id = b_id
        self.rectangle = Rectangle(*b_rect)
        self.observers = observers
        self.notify()

    def register_with_new_owner(self):
        self._owner = None
        for observer in self.observers.values():
            if observer.contains(self): 
                self._owner = observer
                break
        if self._owner: self._owner.register(self)

    def notify(self):
        if self._owner: self._owner.monitor(self)
        else:           self.register_with_new_owner()

    def move_to(self, rectangle):
        self.rectangle = Rectangle(*rectangle)
        self.notify()
    
    def get_color(self):
        if self._owner: return self._owner.color
        else:           return GREY 

class BarcodeAreaObserver:
    last_barcode_id = None
    curr_barcode_id = None
    boundary = None

    def __init__(self, boundary_rectangle, color=GREY):
        self.boundary = Rectangle(*boundary_rectangle)
        self.color = color

    def monitor(self, subject):
        if not self.contains(subject): 
            self.curr_barcode_id = None
            subject.register_with_new_owner()
    
    def register(self, subject):
        self.last_barcode_id = subject.b_id
        self.curr_barcode_id = subject.b_id

    def contains(self, subject):
        return self.boundary.contains(subject.rectangle)
    
    def is_empty(self):
        return self.curr_barcode_id == None

class State: pass

class TaskPreparing(State):
    def run(self, task):
        print("Task Preparing state")
        pass
    
    def next(self, areas):
        for key, area in areas.items():
            if key == "save": continue

            if area.last_barcode_id == None: 
                return TaskPreparing()
        return TaskInProgress()

class TaskInProgress(State):
    def run(self, task):
        print("Task In Progress state")
        pass

    def next(self, areas):
        if areas["work"].last_barcode_id == areas["save"].curr_barcode_id:
            return TaskDone()
        return TaskInProgress()

class TaskDone(State):
    def __init__(self):
        self.log_success = False
    def run(self, task):
        print("Task Done state")
        print("Logging task", task)
        self.log_success = True

    def next(self, areas):
        if self.log_success:
            areas["work"].last_barcode_id = None
            return TaskPreparing()
        return  TaskDone()

class WorkStation:
    def __init__(self, width, height):
        x1 = width/3
        x2 = 2*width/3
        y1 = height/3; 
        y2 = 2*height/3

        self.areas = { "mode": BarcodeAreaObserver((0, 0, x1, y1), PURPLE),
                       "base": BarcodeAreaObserver((0, y1, x1, y1), BLUE),
                       "from": BarcodeAreaObserver((0, y2, x1, y1), LIME),
                       "work": BarcodeAreaObserver((x1, 0, x1, height), RED),
                       "save": BarcodeAreaObserver((x2, 0, x1, height), YELLOW)
        }

        self.observed_barcodes = {}

        self.state = TaskPreparing()

    def update(self, bcode_id, bcode_rect):
        if bcode_id in self.observed_barcodes.keys():
            self.observed_barcodes[bcode_id].move_to(bcode_rect)
        else:
            self.observed_barcodes[bcode_id] = ObservableBarcode(bcode_id, bcode_rect, observers = self.areas)

    def process(self, detected_qrs):
        detected_dict = {}

        for bcode in detected_qrs:
            bcode_id = bcode.data.decode("utf-8")
            detected_dict[bcode_id] = bcode
            self.update(bcode_id, bcode.rect)
        
        to_remove = list(set(self.observed_barcodes.keys()) - set(detected_dict.keys()))
        for key in to_remove:
            del self.observed_barcodes[key]

        task = " ".join(str(area.last_barcode_id) for area in self.areas.values())
        
        self.state.run(task)
        self.state = self.state.next(self.areas)

        return task
    
    def get_task_description():
        return 

class Rectangle:
    def __init__(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
    
    def contains(self, rect):
        return self.h > rect.h and self.w > rect.w and \
            self.x < rect.x and self.y < rect.y and \
            self.x+self.w > rect.x + rect.w and \
            self.y+self.h > rect.y + rect.h

class Artist:
    font = cv2.FONT_HERSHEY_DUPLEX

    def draw_workstation(self, workstation, frame):
        for area in workstation.areas.values():
            self.draw_rectangle(area.boundary, frame)

        for barcode in workstation.observed_barcodes.values():
            color = barcode.get_color()
            self.draw_rectangle(barcode.rectangle, frame, color=color)

            text_org = (barcode.rectangle.x, barcode.rectangle.y - 20)
            cv2.putText(frame, barcode.b_id, text_org, self.font, 1, color, 2, cv2.LINE_AA)
        
    def draw_rectangle(self, r, frame, color=GREY, thickness=3):
        cv2.rectangle(frame, (r.x, r.y), (r.x + r.w, r.y + r.h), color, thickness)





    
