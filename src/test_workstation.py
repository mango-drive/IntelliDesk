import os
import unittest
import csv
from workstation import WorkStation, Rectangle, Area, Task, Logger

def read_lines(file):
    lines = []
    with open(file, mode="r") as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            line = [None if i == '' else i for i in line]
            lines.append(line)
    return lines

class MockBarcode:
    def __init__(self, rect, data):
        self.rect = rect
        self.data = data

class TestRectangle(unittest.TestCase):
    def setUp(self):
        self.small = Rectangle(2, 2, 1, 1)
        self.large = Rectangle(0, 0, 10, 10)

    def test_small_does_not_contain_large(self):
        self.assertFalse(self.small.contains(self.large))
    
    def test_large_contains_small(self):
        self.assertTrue(self.large.contains(self.small))
    
    def test_far_away_rectangles(self):
        rect1 = Rectangle(0, 0, 5, 5)
        rect2 = Rectangle(10, 10, 1, 1)
        self.assertFalse(rect1.contains(rect2))

class TestArea(unittest.TestCase):
    def setUp(self):
        self.area = Area("test_area", Rectangle(0, 0, 10, 10))
        self.mock_barcode = MockBarcode((2, 2, 1, 1), b"test_barcode")
        self.area.acknowledge(self.mock_barcode)

    def test_area_ack_barcode_inside(self):
        self.assertTrue(self.area.barcode is self.mock_barcode)
    
    def test_area_ack_prev_barcode_inside(self):
        self.assertTrue(self.area.prev_barcode is self.mock_barcode)

    def test_ack_barcode_outside(self):
        # move the barcode elsewhere
        self.mock_barcode.rect = (15, 15, 1, 1)
        self.area.acknowledge(self.mock_barcode)
        self.assertTrue(self.area.barcode is None)
        self.assertTrue(self.area.prev_barcode is self.mock_barcode)


class TestTask(unittest.TestCase):
    def setUp(self):

        self.task = Task()

    def test_incomplete_state(self):
        self.assertTrue(self.task.state == "INCOMPLETE")

    def test_complete_state(self):
        self.task = Task(mode="ModeVerb", 
                        base="Base", 
                        src="SrcContainer", 
                        dest="DestContainer")
        self.assertTrue(self.task.state == "DOING") 

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.file = "test.csv"
        f = open(self.file, mode="w")
        f.truncate()
        f.close()

        self.logger = Logger(self.file)

        self.task = Task(mode="ModeVerb", 
                        base="Base", 
                        src="SrcContainer", 
                        dest="DestContainer")

        self.mock_task = Task(mode="MockTask")
        self.mock_task.state = "DONE"



    def test_has_a_writable_db(self):
        self.logger.write(["a", "b", "c"])
        self.logger.write(["d", "e", "f"])

        lines = read_lines(self.file)

        self.assertTrue(lines == [["a", "b", "c"],
                                 ["d", "e", "f"]])
        
        
    def test_writes_done_task_to_file(self):
        self.logger.log(self.mock_task)

        lines = read_lines(self.file)
        dump = self.mock_task.dump()

        self.assertTrue(lines[0] == self.mock_task.dump())

    def test_marks_task_as_saved(self):
        self.logger.log(self.mock_task)
        self.assertTrue(self.mock_task.state == "SAVED")

    def test_does_not_log_a_saved_task(self):
        self.logger.log(self.task) # should mark task as saved

        lines = read_lines(self.file)
        self.assertTrue(len(lines) == 0)


class TestWorkstation(unittest.TestCase):
    def setUp(self):
        self.w = WorkStation(300, 300)

        # a scene where all areas except the work area and save area
        # are filled by a barcode 
        self.incomplete_scene = [
            MockBarcode((1, 1, 1, 1), b"mode"),
            MockBarcode((1, 101, 1, 1), b"base"),
            MockBarcode((1, 201, 1, 1), b"from"),
        ]

        self.barcode_in_work_area = MockBarcode((101, 1, 1, 1), b"dest")
        self.same_barcode_in_save_area = MockBarcode((201, 1, 1, 1), b"dest")


        # doing_scene: a scene where all areas except save area have a barcode
        self.doing_scene = self.incomplete_scene.copy()
        self.doing_scene.append(self.barcode_in_work_area)

        # done_scene: destination barcode moved to save area
        self.done_scene = self.incomplete_scene.copy()
        self.done_scene.append(self.same_barcode_in_save_area)

        self.file = "test.csv"
        f = open(self.file, mode="w")
        f.truncate()
        f.close()

        self.logger = Logger(self.file)

    def test_process_returns_incomplete_task(self):
        task=self.w.process(self.incomplete_scene)
        self.assertTrue(task.state == "INCOMPLETE")

    def test_process_returns_doing_task(self):
        task = self.w.process(self.doing_scene)
        self.assertTrue(task.state == "DOING")
    
    def test_barcode_in_save_when_task_incomplete(self):
        task = self.w.process(self.done_scene)
        self.assertTrue(task.state == "INCOMPLETE")
    
    def test_work_barcode_not_moved_to_save(self):
        self.w.process(self.incomplete_scene)
        self.w.process(self.doing_scene)
        self.assertEqual(self.w.user_moves_work_barcode_into_save_area(), False)
        
    def test_task_marked_as_done(self):
        task = self.w.process(self.doing_scene)
        task = self.w.process(self.done_scene)
        self.assertEqual(task.state, "DONE") 

    def test_done_task_logged(self):
        print("User is in middle of task")
        task = self.w.process(self.doing_scene)
        self.logger.log(task)

        lines = read_lines(self.file)
        self.assertEqual(len(lines), 0)
        
        print("User saves")
        task = self.w.process(self.done_scene)
        self.logger.log(task)

        lines = read_lines(self.file)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], ['mode', 'base', 'from', 'dest'])

        print("Camera redetects a done scene, but it should not be logged")
        task = self.w.process(self.done_scene)
        self.logger.log(task)
        lines = read_lines(self.file)
        self.assertEqual(len(lines), 1)

        print("User sets up for the same task")
        task = self.w.process(self.incomplete_scene)
        self.logger.log(task)
        lines = read_lines(self.file)
        self.assertEqual(len(lines), 1)

        print("User is in the middle of doing the same task")
        task = self.w.process(self.doing_scene)
        self.logger.log(task)
        lines = read_lines(self.file)
        self.assertEqual(len(lines), 1)

        print("User completes it again")
        self.w.process(self.done_scene)
        self.logger.log(task)
        lines = read_lines(self.file)
        self.assertEqual(len(lines), 2)

if __name__ == "__main__":
    unittest.main()
