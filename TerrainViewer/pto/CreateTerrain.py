import glob

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget
)

import numpy as np

class CreateTerrain(QWidget):
    def __init__(
        self, 
        InLatLowerLeft: float, InLonLowerLeft: float,
        InLatUpperRight: float, InLonUpperRight: float
    ):
        super(CreateTerrain, self).__init__()
        
        self.LowerLeftLat = InLatLowerLeft
        self.LowerLeftLon = InLonLowerLeft
        self.UpperRightLat = InLatUpperRight
        self.UpperRightLon = InLonUpperRight

        self.ImageHoriSize = 0
        self.ImageVertSize = 0
    
    
    

class Calculator():
    def __init__(        
        self, 
        InLatLowerLeft: float, InLonLowerLeft: float,
        InLatUpperRight: float, InLonUpperRight: float
    ):
        super(Calculator, self).__init__()

