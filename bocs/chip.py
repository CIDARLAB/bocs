from pymint import MINTDevice, MINTComponent
from typing import List, Optional
import numpy as np

class Chip:
    """The base Microfluidic Chip model that we will be using to create/model the devices

    We utlize MINTDevice as the core device information. MINT device would have all the netlist information.
    We then have the constraint matrix that will hold all the data capturing the Fluidic AND, Fluidic OR,
    and Fluidic NOT constraints. We also hold all the references for the devices.

    """


   def __init__(self) -> None:
       self.device: Optional[MINTDevice] = None
       self.constraint_matrix: np.ndarray = 


    @property
    def valves(self) -> List[MINTComponent]:
        return self.device.get_valves()

