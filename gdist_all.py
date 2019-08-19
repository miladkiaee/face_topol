import numpy as np
import csv
import os
import pandas as pd

cur_path = '/home/milad/Downloads/sameer/3D_ElasticCurves/'

subs_data = pd.read_csv(cur_path + 'subx.txt', '\t')

sorted_subs = subs_data.sort_values(by=['Severity'])
sorted_subs = sorted_subs.reset_index(drop=True)
sorted_subs.to_csv('sorted_subs.txt')
num_subjects = sorted_subs.count()[0]

dist_file = open(cur_path + 'distance_file.txt', 'w')
sub_toremove = open(cur_path + 'subs_toremove.txt', 'w')

for subid_1 in range(0, num_subjects):
    print('iter ', subid_1)
    for subid_2 in range(0, num_subjects):

        sub1 = sorted_subs.Subject[subid_1]
        sub2 = sorted_subs.Subject[subid_2]

        candid1 = cur_path + 'gdist_' + sub1 + '_' + sub2 + '.txt'
        candid2 = cur_path + 'gdist_' + sub2 + '_' + sub1 + '.txt'

        filepath = 'not_assigned'
        if os.path.exists(candid1):
            filepath = candid1
        if os.path.exists(candid2):
            filepath = candid2

        if subid_1 == subid_2:
            dist_file.write("%s, %s, %s\n" % (subid_1, subid_1, str(0)))

        elif filepath != 'not_assigned':
            curve_dists = np.ones(46)
            curve_dists = 0 * curve_dists
            with open(filepath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=' ')
                line_count = 0
                for row in csv_reader:
                    line_count += 1
                    level = int(row[2])
                    level_dist = float(row[3])
                    curve_dists[level - 3] = level_dist**2

                dist = np.sqrt(np.sum(curve_dists))
                # dist = np.power(np.prod(curve_dists), 1.0/90.0)
                dist_file.write("%s, %s, %s\n" % (subid_1, subid_2, dist))
        else:
            # feel with some special number since it seems we dont have distances for
            dist_file.write("%s, %s, %s\n" % (subid_1, subid_2, 'nan'))
            sub_toremove.write("%s, %s\n" % (sub1, sub2))

dist_file.close()
sub_toremove.close()
print('end!')
