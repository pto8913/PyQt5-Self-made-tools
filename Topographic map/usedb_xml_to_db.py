import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from mpl_toolkits.axes_grid1 import make_axes_locatable
import mysql.connector as con

#def filename(lat, lon):
#  lat_a = lat / (2/ 3)
#  lon_b = (lon - int(lon)) / (1/ 8)
#  lat_b = (lat_a - int(lat_a)) / (1/ 8)
#  lat_c = (lat_b * 10) % 10
#  lon_c = (lon_b * 10) % 10
#  return "{}{}".format(int(lat_c), int(lon_c))

def elev():
  #path = filename(lat, lon)
  
  try:
    conn = con.connect(
      user = "root",
      password = "pass",
      host = "localhost",
      database = "name"
    )
    cur = conn.cursor()
    cur.execute(
      "select sp, elevation\
       from fg46\
       where lc_lat >= 35.6666666667 and lc_lat <= 35.675;"# and uc_lat <= 35.683 and lc_lon >= 139.763 and uc_lon <= 139.776;"
    )
    raw = []
    sp = 0
    for s, e in cur.fetchall():
      sp = max(sp, s)
      raw.append(e)
    cur.close
    conn.close
    elevs = np.full((1500 * 2250, ), -10)
    elevs[sp: len(raw) + sp] = raw
    
  except:
    pass
  elevs = elevs.reshape((2250, 1500))
  elevs = np.flipud(elevs)
  return elevs

elevs = elev()
#elevs[np.isnan(elevs)] = np.nanmin(elevs)

fig, ax = plt.subplots()
elevs = np.flipud(elevs)
ls = LightSource(azdeg = 180, altdeg = 65)
color = ls.shade(elevs, cm.rainbow)
cs = ax.imshow(elevs, cm.rainbow)
ax.imshow(color)

make_axes = make_axes_locatable(ax)
cax = make_axes.append_axes("right", size = "2%", pad = 0.05)
fig.colorbar(cs, cax)

ax.set_xticks([])
ax.set_yticks([])

plt.show()
