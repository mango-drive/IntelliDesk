import os
import unittest
import csv
from workstation import ( WorkStation,            \
                          Rectangle,              \
                          ObservableBarcode,      \
                          BarcodeAreaObserver,    \
)

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

class TestObservableBarcode(unittest.TestCase):
    def setUp(self):
        # Area at origin, with width=10, height=10
        self.observers = {
            "test_area": BarcodeAreaObserver((0, 0, 10, 10))
        }
        # The user positions a qr code inside the area. 
        self.qr_code = ObservableBarcode("b", (1, 1, 1, 1), observers=self.observers)
        self.qr_code_outside = ObservableBarcode("b_out", (11, 11, 1, 1), observers=self.observers)

    def test_initial_location_is_observed(self):
        # The area owns the qr code
        self.assertTrue(self.observers["test_area"].last_barcode_id == "b")
        self.assertTrue(self.qr_code._owner is self.observers["test_area"])

if __name__ == "__main__":
    unittest.main()
