from abc import abstractmethod, ABCMeta

# Abstract base class for a state
class State(metaclass = ABCMeta):
    @abstractmethod
    def next(self):
        pass

# TODO Refactor tasks
class Preparing(State):
    def next(self, areas):
        for key, area in areas.items():
            if key == "save": continue

            if area.last_barcode_id == None: 
                return PREPARING
        print("In progress")
        return INPROGRESS

class InProgress(State):
    def next(self, areas):
        if areas["work"].last_barcode_id == areas["save"].curr_barcode_id:
            print("Done")
            return DONE
        return INPROGRESS

class Done(State):
    def next(self, areas):
        areas["work"].last_barcode_id = None
        print("Preparing")
        return PREPARING

INPROGRESS = InProgress()
DONE = Done()
PREPARING = Preparing()

class Task:
    def __init__(self):
        print("Preparing")
        self.state = PREPARING
        self.description = None

    def update(self, areas):
        self.description = " ".join(str(area.last_barcode_id) for area in areas.values())
        self.state = self.state.next(areas)

    