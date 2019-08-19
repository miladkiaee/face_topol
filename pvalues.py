import numpy as np
import csv
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import clim

import matplotlib.colors as colors
from matplotlib.colors import LogNorm
from matplotlib.colors import PowerNorm
import seaborn as sns

import matplotlib.pyplot as plt

# steps to follow
# collect the distance matrix

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

# create the two vector batch
b_size_x = 70
b_size_y = 70
ind_x = range(0, b_size_x)
ind_y = range(N-1-b_size_y, N)

# distance from x -> y
numberOfIterations = 1000
d_i = []
d_size = b_size_x*b_size_y
dg = np.zeros(d_size)

for i in range(0, b_size_x):
    for j in range(0, b_size_y):
        dg[i*b_size_y + j] = dist[ind_x[i], ind_y[j]]

dg = np.nan_to_num(dg)
d0 = np.average(dg)

for iter in range(numberOfIterations):
    pool_xy = np.append(ind_x, ind_y)
    np.random.shuffle(pool_xy)

    ind_x = np.random.choice(pool_xy, b_size_x, replace=False)
    ind_y = np.setdiff1d(pool_xy, ind_x)  # np.random.choice(pool_xy, b_size_y, replace=False)

    for i in range(0, b_size_x):
        for j in range(0, b_size_y):
            dg[i * b_size_y + j] = dist[ind_x[i], ind_y[j]]

    dg = np.nan_to_num(dg)
    d_i.append(np.average(dg))

f = open('pval.txt', 'w')
f.write('%f\n' % d0)
for i in range(numberOfIterations):
    f.write('%f\n' % d_i[i])

f.close()

plt.plot(d_i)
plt.show()
