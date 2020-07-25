import numpy as np

UserSelectedItems = [[False for _ in range(10)] for _ in range(10)]
DFSReached = [[False for _ in range(10)] for _ in range(10)]
__JoinableTileTemp = []
JoinableTileList = []

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
    __JoinableTileTemp.append((y, x))
    return BeginDFS(x + 1, y) or BeginDFS(x - 1, y) or BeginDFS(x, y + 1) or BeginDFS(x, y - 1)

for y in range(10):
    for x in range(10):
        if UserSelectedItems[y][x] and not DFSReached[y][x]:
            BeginDFS(x, y)
            JoinableTileList.append(__JoinableTileTemp)
            __JoinableTileTemp = []
JoinableTileList

# for aaa in UserSelectedItems:
#     print(aaa)

INF = int(1e9+7)
Result = []
for Tiles in JoinableTileList:
    MinX, MinY = INF, INF
    MaxX, MaxY = 0, 0
    RemakeTiles = np.array([])
    if len(Tiles) > 1:
        for y, x in Tiles:
            MinX = min(MinX, x)
            MinY = min(MinY, y)
            MaxX = max(MaxX, x)
            MaxY = max(MaxY, y)
        RemakeTiles = np.full((MaxY - MinY + 1, MaxX - MinX + 1), -1)
        for y, x in Tiles:
            ny, nx = y, x
            if MinX != 0:
                nx -= MaxX + 1
            if MinY != 0:
                ny -= MaxY + 1
            RemakeTiles[ny][nx] = y * 10 + x
    else:
        RemakeTiles = np.array([Tiles[0][0] * 10 + Tiles[0][1]])
        MinX, MinY = 0, 0
    Result.append(RemakeTiles)
for a in Result:
    print(a)
 
