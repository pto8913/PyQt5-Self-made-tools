# --- STL ---
from typing import List

# --- PL ---
import numpy as np

# --- MyL ---

MINIMUM_ELEV = -100

class LoadedItemData:
    def __init__(self):
        super(LoadedItemData, self).__init__()

        self._ItemPriority = 0
        self._ItemNum = 0

        self._ItemPath = ""

        self._GridXLow = 0
        self._GridYLow = 0

        self._GridXHigh = 0
        self._GridYHigh = 0

        self._GridXSize = 0
        self._GridYSize = 0

        self._MinimumElev = 0

        self._Elev = np.array([])
        
    # --------------- ItemPriority ---------------
    @property    
    def ItemPriority(self) -> int:
        return self._ItemPriority
    @ItemPriority.setter
    def ItemPriority(self, In: int) -> None:
        self._ItemPriority = In

    # --------------- ItemNum ---------------
    @property    
    def ItemNum(self) -> int:
        return self._ItemNum
    @ItemNum.setter
    def ItemNum(self, In: int) -> None:
        self._ItemNum = In

    # --------------- ItemPath ---------------
    @property
    def ItemPath(self) -> str:
        return self._ItemPath
    @ItemPath.setter
    def ItemPath(self, In: str) -> None:
        self._ItemPath = In

    # --------------- GridXLow ---------------
    @property
    def GridXLow(self) -> int:
        return self._GridXLow
    @GridXLow.setter
    def GridXLow(self, In: int) -> None:
        self._GridXLow = In

    # --------------- GridYLow ---------------
    @property
    def GridYLow(self) -> int:
        return self._GridYLow
    @GridYLow.setter
    def GridYLow(self, In: int) -> None:
        self._GridYLow = In

    # --------------- GridXHigh ---------------
    @property
    def GridXHigh(self) -> int:
        return self._GridXHigh
    @GridXHigh.setter
    def GridXHigh(self, In: int) -> None:
        self._GridXHigh = In

    # --------------- GridYHigh ---------------
    @property
    def GridYHigh(self) -> int:
        return self._GridYHigh
    @GridYHigh.setter
    def GridYHigh(self, In: int) -> None:
        self._GridYHigh = In

    # --------------- GridXSize ---------------
    @property
    def GridXSize(self) -> int:
        return self._GridXSize
    @GridXSize.setter
    def GridXSize(self, In: int) -> None:
        self._GridXSize = In
    def CalcXSize(self) -> None:
        self._GridXSize = self._GridXHigh - self._GridXLow + 1
    
    # --------------- GridYSize ---------------
    @property
    def GridYSize(self) -> int:
        return self._GridYSize
    @GridYSize.setter
    def GridYSize(self, In: int) -> None:
        self._GridYSize = In
    def CalcYSize(self) -> None:
        self._GridYSize = self._GridYHigh - self._GridYLow + 1

    # --------------- Elev ---------------
    @property
    def MinimumElev(self) -> float:
        return self._MinimumElev
    @MinimumElev.setter
    def MinimumElev(self, In: float) -> None:
        self._MinimumElev = In

    def InitElev(self) -> None:
        self.CalcXSize()
        self.CalcYSize()
        self._Elev = np.zeros(self._GridYSize * self._GridXSize, dtype=np.uint16)
    
    def AddElev(self, Index: int, InValue: float) -> None:
        self._Elev[Index] = InValue
        
    @property
    def Elev(self) -> np.ndarray:
        return self._Elev
    @Elev.setter
    def Elev(self, In: np.ndarray) -> np.ndarray:
        self._Elev = In
    
    def Reshape(self) -> np.ndarray:
        self._Elev = self._Elev.reshape((self._GridYSize, self._GridXSize))
        # self._Elev = np.where(self._Elev <= MINIMUM_ELEV, self.MinimumElev, self._Elev)
        return self._Elev