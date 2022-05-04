import numpy as np

array = np.loadtxt('GUI/times.txt', dtype=float)
num_u = int(len(array) / 30)
fin_array = np.zeros((30, num_u))
for i in range(30):
    for j in range(num_u):
        if j == 0:
            fin_array[i][j] = -1 * array[i*num_u]
        else:
            fin_array[i][j] = array[(i*num_u)+j]

sum_arr = np.zeros((30, num_u-1))

for i in range(30):
    for j in range(num_u-1):
        sum_arr[i][j] = fin_array[i][0] + fin_array[i][j+1]

print(sum_arr)

mean = np.mean(sum_arr)
print(mean)