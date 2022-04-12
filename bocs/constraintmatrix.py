from typing import Dict
import numpy as np


class ConstraintMatrix:

    def __init__(self):
        self.header = []
        self.matrix = np.ndarray((0, 0))

    def set_header(self, header):
        self.header = header

    def insert_row(self, row: Dict[str, bool]):
        # TODO: insert the data into this
        pass