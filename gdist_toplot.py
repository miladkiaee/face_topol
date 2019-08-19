import numpy as np
import csv
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import clim

import matplotlib.colors as colors
from matplotlib.colors import LogNorm
from matplotlib.colors import PowerNorm
import seaborn as sns

cur_path = '/home/milad/Downloads/sameer/3D_ElasticCurves/'
dis_file_path = cur_path + 'distance_file.txt'

x = []
y = []
z = []
with open(dis_file_path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        line_count += 1
        x.append(float(row[0]))
        y.append(float(row[1]))
        z.append(float(row[2]))

N = 173
dist = np.random.random((N, N))

for i in range(0, N):
    for j in range(0, N):
        dist[i, j] = z[j + i*(N+1)]

# plt.pcolor(dist, cmap=current_cmap)
masked_array = np.ma.array(dist, mask=np.isnan(dist))

np.savetxt('distance_matrix.txt', dist, delimiter=',',  fmt='%1.4e')

#cmap = matplotlib.colors.ListedColormap(['black', 'grey', 'green',  'red',
                                         # 'blue', 'black', 'black'])
#cmap.set_bad('black', 0.8)
#boundaries = [0, 0.001, 0.4,  0.5,  0.55,  0.65, 0.8,  1]
#norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)


# plt.pcolor(masked_array, cmap='gist_rainbow',
  #          vmin=0.3, vmax=0.6)
plt.axvline(x=78, label='-OSA-'.format(0.3), c='w', linewidth=4)
plt.axhline(y=78, label='-OSA-'.format(0.3), c='w', linewidth=4)
# plt.colorbar()
# plt.show()

l2 = masked_array
l2 = l2 + 0.001
l2 = l2/l2.max()

# uneven bounds changes the colormapping
sns.set()
colors = ["black", "blue", "brown", "red", "yellow", "white"]
sns.heatmap(l2, cmap=sns.xkcd_palette(colors), norm=PowerNorm(gamma=1), vmin=0.6, vmax=l2.max())
# sns.heatmap(l2)
# plt.show()
plt.savefig('/home/milad/geodesic_l2.png', dpi=1000)
