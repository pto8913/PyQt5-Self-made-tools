# --- STL ---
from typing import Union

# --- PL ---

# --- MyL ---

class Math:
    def clamp(Target: Union[int, float], Min: Union[int, float], Max: Union[int, float]) -> Union[int, float]:
        if Target < Min:
            return Min
        if Max < Target:
            return Max 
        return Target