UserSelectedItems = [[False for _ in range(10)] for _ in range(10)]
DFSReached = [[False for _ in range(10)] for _ in range(10)]
__JoinedTileTemp = []
JoinedTileList = []

import random
for _ in range(20):
    RandomIndex = random.randint(0, 99)
    x = RandomIndex % 10
    y = RandomIndex // 10
    UserSelectedItems[y][x] = True

def BeginDFS(x: int, y: int) -> None:
    if x < 0 or y < 0 or x >= 10 or y >= 10 or not UserSelectedItems[y][x]:
        return
    if DFSReached[y][x]:
        return
    DFSReached[y][x] = True
    __JoinedTileTemp.append((y, x))
    return BeginDFS(x + 1, y) or BeginDFS(x - 1, y) or BeginDFS(x, y + 1) or BeginDFS(x, y - 1)

for y in range(10):
    for x in range(10):
        if UserSelectedItems[y][x] and not DFSReached[y][x]:
            BeginDFS(x, y)
            JoinedTileList.append(__JoinedTileTemp)
            __JoinedTileTemp = []
JoinedTileList

# for aaa in UserSelectedItems:
#     print(aaa)