from abc import abstractmethod, ABCMeta

# Abstract base class for a state
class State(metaclass = ABCMeta):
    @abstractmethod
    def changeState(self):
        pass


# TODO Refactor tasks
class Preparing(State):
    def next(self, areas):
        for key, area in areas.items():
            if key == "save": continue

            if area.last_barcode_id == None: 
                return Preparing()
        return InProgress()

class InProgress(State):
    def next(self, areas):
        if areas["work"].last_barcode_id == areas["save"].curr_barcode_id:
            return Done()
        return InProgress()

class Done(State):
    def next(self, areas):
        areas["work"].last_barcode_id = None
        return Preparing()