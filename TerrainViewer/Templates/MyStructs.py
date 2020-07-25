# --- STL ---
from typing import List

# --- PL ---
import numpy as np

# --- MyL ---


MINIMUM_ELEV = -100

class LoadedItemData:
    def __init__(self):
        super(LoadedItemData, self).__init__()

        self._ItemPath = ""

        self._MinimumElev = 0

        self._GridXSize = 225
        self._GridYSize = 150

        self._Elev = np.full(self._GridXSize * self._GridYSize, MINIMUM_ELEV, dtype = np.uint16)
        
    # --------------- ItemPath ---------------
    @property
    def ItemPath(self) -> str:
        return self._ItemPath
    @ItemPath.setter
    def ItemPath(self, In: str) -> None:
        self._ItemPath = In

    # --------------- Grid Size ---------------
    @property
    def GridXSize(self) -> int:
        return self._GridXSize

    @property
    def GridYSize(self) -> int:
        return self._GridYSize

    # --------------- Elev ---------------
    @property
    def MinimumElev(self) -> float:
        return self._MinimumElev
    @MinimumElev.setter
    def MinimumElev(self, In: float) -> None:
        self._MinimumElev = In

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