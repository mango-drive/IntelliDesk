import csv
import cv2

COLOR_RED = (211, 47, 47)
COLOR_PURPLE = (186, 104, 200)
COLOR_BLUE = (41, 182, 246)
COLOR_LIME = (102, 255, 0)
COLOR_YELLOW = (255, 255, 0)

class Artist:
    def draw_barcode(self, frame, barcode, color):
        if barcode is not None:
            (x, y, w, h) = barcode.rect
            self.draw_rectangle(frame, x, y, w, h, color)

    def draw_workstation(self, frame, workstation):
          for area in workstation.areas.values():
                self.draw_rectangle(frame, 
                area.r.x,
                area.r.y,
                area.r.w,
                area.r.h )

                self.draw_barcode(frame, area.barcode, area.color)

    def draw_rectangle(self, frame, x, y, w, h, color=(171, 178, 185)):
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

class Task:
    def __init__(self, mode=None, base=None, src=None, dest=None):
        self.task = None
        self.update(mode=mode, base=base, src=src, dest=dest)
    
    def dump(self):
        return [self.task["mode"], 
                self.task["base"], 
                self.task["from"],
                self.task["work"]]

    def update(self, mode=None, base=None, src=None, dest=None):
        self.task = {
            "mode": mode,
            "base": base,
            "from": src,
            "work": dest,
        }
        
        self.state = "DOING"
        for data in self.task.values():
            if data is None: self.state = "INCOMPLETE"
        
        return self.task
    
class Logger:
    def __init__(self, db="tasks.csv"):
        self.db = db
    
    def write(self, row):
        with open(self.db, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    def log(self, task):
        if task.state == "DONE":
            dump = task.dump()
            self.write(dump)
            task.state = "SAVED"
    


class WorkStation:
    """
    Workstation Areas
    0,0---1/3,0---2/3,0---1,0
    |   0   |       |       |
    0,1/3---+       |       |
    |   1   |   3   |   4   |
    0,2/3---+       |       |
    |   2   |       |       |
    0,1-----+-------+-------+
    """
    def __init__(self, w, h):
        self.areas = []
        x1 = w/3; x2 = 2*w/3
        y1 = h/3; y2 = 2*h/3

        self.areas = {
            "mode": Area("mode", Rectangle(0, 0, x1, y1), COLOR_PURPLE),
            "base": Area("base", Rectangle(0, y1, x1, y1), COLOR_BLUE),
            "from": Area("from", Rectangle(0, y2, x1, y1), COLOR_LIME),
            "work": Area("work", Rectangle(x1, 0, x1, h), COLOR_RED),
            "save": Area("save", Rectangle(x2, 0, x1, h), COLOR_YELLOW),
        }

        self.task = Task()
        
    def process(self, barcodes):
        for barcode in barcodes:
            for area in self.areas.values():
                area.acknowledge(barcode)

        self.task.update(mode=self.areas["mode"].get_decoded_barcode_data(),
                    base=self.areas["base"].get_decoded_barcode_data(),
                    src=self.areas["from"].get_decoded_barcode_data(),
                    dest=self.areas["work"].get_decoded_barcode_data()
        )


        if (self.user_moves_work_barcode_into_save_area()):
            self.task.state = "DONE"

            for area in self.areas.values():
                area.prev_barcode = None
                area.barcode = None
            
        return self.task
    
    def user_moves_work_barcode_into_save_area(self):
        if (self.task.state == "DOING"):
            saveBarcode = self.areas["save"].get_most_recent_barcode()
            return saveBarcode == self.task.task["work"]
        return False
    
class Area:
    def __init__(self, name, boundary_rect, color):
        self.name = name
        self.r = boundary_rect
        self.prev_barcode = None
        self.barcode = None
        self.color = color

    def get_rectangle(self):
        return self.r

    def is_different(self, barcode):
        return self.prev_barcode is not None and self.prev_barcode.data != barcode.data

    def is_new(self, barcode):
        return self.prev_barcode is None or self.is_different(barcode)

    def acknowledge(self, barcode):
        # reset the most up to date barcode in case barcode has left
        # the area
        self.barcode = None
        (x, y, w, h) = barcode.rect
        barcodeRect= Rectangle(x, y, w, h)
        if self.r.contains(barcodeRect):
            self.barcode = barcode
            if self.is_new(barcode):
                self.prev_barcode = barcode

    def get_most_recent_barcode(self):
        if self.barcode is not None:
            return self.barcode.data.decode("utf-8")
        else:
            return None

    def get_decoded_barcode_data(self):
        if self.prev_barcode is not None:
            return self.prev_barcode.data.decode("utf-8")
        else:
            return None


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

