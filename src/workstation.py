import cv2

class ObservableBarcode:
    rectangle = None
    _owner = None
    observers = []
    b_id = None

    def __init__(self, b_id, b_rect, observers):
        self.b_id = b_id
        self.rectangle = Rectangle(*b_rect)
        self.observers = observers

    def register_with_new_owner(self):
        self._owner = None
        for observer in self.observers:
            if observer.contains(self): 
                self._owner = observer
                break
        if self._owner: self._owner.register(self)

    def notify(self):
        if self._owner: 
            self._owner.monitor(self)
        else: 
            self.register_with_new_owner()

    def move_to(self, rectangle):
        self.rectangle = rectangle
        self.notify()
    
    def get_color(self):
        if self._owner: return self._owner.color
        else:           return COLOR_GREY 

class BarcodeAreaObserver:
    last_barcode_id = None
    ba_id = None
    boundary = None

    def __init__(self, ba_id, boundary_rectangle, color):
        self.ba_id = ba_id
        self.boundary = boundary_rectangle
        self.color = color

    def monitor(self, subject):
        if not self.contains(subject):
            subject.register_with_new_owner()
    
    def register(self, subject):
        self.last_barcode_id = subject.b_id

    def contains(self, subject):
        return self.boundary.contains(subject.rectangle)


COLOR_RED = (211, 47, 47)
COLOR_PURPLE = (186, 104, 200)
COLOR_BLUE = (41, 182, 246)
COLOR_LIME = (102, 255, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREY = (171, 178, 185)

class WorkStation:
    def __init__(self, width, height):
        x1 = width/3
        x2 = 2*width/3
        y1 = height/3; 
        y2 = 2*height/3

        self.areas = []
        self.areas.append(BarcodeAreaObserver("mode", Rectangle(0, 0, x1, y1), COLOR_PURPLE))
        self.areas.append(BarcodeAreaObserver("base", Rectangle(0, y1, x1, y1), COLOR_BLUE))
        self.areas.append(BarcodeAreaObserver("from", Rectangle(0, y2, x1, y1), COLOR_LIME))
        self.areas.append(BarcodeAreaObserver("work", Rectangle(x1, 0, x1, height), COLOR_RED))
        self.areas.append(BarcodeAreaObserver("save", Rectangle(x2, 0, x1, height), COLOR_YELLOW))

        self.observable_barcodes = {}

    def update(self, bcode_id):
        if bcode_id in self.observable_barcodes.keys():
            self.observable_barcodes[bcode_id].move_to(Rectangle(*bcode.rect))
        else:
            print("New barcode", bcode_id)
            self.observable_barcodes[bcode_id] = ObservableBarcode(bcode_id, bcode.rect, self.areas)


    def process(self, detected_qrs):
        detected_dict = {}

        for bcode in detected_qrs:
            bcode_id = bcode.data.decode("utf-8")
            detected_dict[bcode_id] = bcode
            self.update(bcode_id)
        
        to_remove = list(set(self.observable_barcodes) - set(detected_dict.keys()))
        for key in to_remove:
            del self.observable_barcodes[key]

        
        inProgress = {}
        for area in self.areas:
            inProgress[area.ba_id] = area.last_barcode_id
        
        return inProgress
        
    
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
    def draw_workstation(self, workstation, frame):
        for area in workstation.areas:
            self.draw_rectangle(area.boundary, frame)

        for barcode in workstation.observable_barcodes.values():
            self.draw_rectangle(barcode.rectangle, frame, color=barcode.get_color())
        
    def draw_rectangle(self, r, frame, color=COLOR_GREY, thickness=3):
        cv2.rectangle(frame, (r.x, r.y), (r.x + r.w, r.y + r.h), color, thickness)
