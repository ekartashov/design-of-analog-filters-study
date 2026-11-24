#!/usr/bin/env python3
from enum import Enum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ticks=[10, 10]
ranges=[[-5, 5],[-5, 5]]

class Axis(Enum):
    x = 0
    y = 1
    z = 2

## Functions
def H_hpf_2(sigma, omega):
    return 20 * np.log((np.power(omega, 2) + np.power(sigma, 2)) / np.sqrt(5.656854248 * np.power(omega, 2) * sigma + 5.656854248 * np.power(sigma, 3) + 22.62741699 * sigma + np.power(sigma, 4) + (2 * np.power(omega, 2) + 16) * np.power(sigma, 2) + np.power(omega, 4) + 16))

def H_lpf_2(sigma, omega):
    return 20 * np.log(4 / np.sqrt(5.656854248 * np.power(omega, 2) * sigma + 5.656854248 * np.power(sigma, 3) + 22.62741699 * sigma + np.power(sigma, 4) + (2 * np.power(omega, 2) + 16) * np.power(sigma, 2) + np.power(omega, 4) + 16))

def H_bpf_2(sigma, omega):
    return 20 * np.log(2.828427124 * np.sqrt(np.power(omega, 2) + np.power(sigma, 2)) * np.sqrt(1 / (5.656854248 * np.power(omega, 2) * sigma + 5.656854248 * np.power(sigma, 3) + 22.62741699 * sigma + np.power(sigma, 4) + (2 * np.power(omega, 2) + 16) * np.power(sigma, 2) + np.power(omega, 4) + 16.)))

def H_bpf_4(sigma, omega):
    return 20 * np.log((9 * np.power(omega, 2) + 9 * np.power(sigma, 2)) / np.sqrt(14.14213562 * (np.power(sigma, 4) + (2 * np.power(omega, 2) + 25) * np.power(sigma, 2) + np.power(omega, 4) + np.power(omega, 2) + 36)*(np.power(omega, 2) + np.power(sigma, 2) + 6) * sigma + np.power(sigma, 8) + (4 * np.power(omega, 2) + 100) * np.power(sigma, 6) + (6 * np.power(omega, 4) + 200 * np.power(omega, 2) + 1297) * np.power(sigma, 4) + (4 * np.power(omega, 6) + 100 * np.power(omega, 4) + 818 * np.power(omega, 2) + 3600 ) * np.power(sigma, 2) + np.power(omega, 8) + 97* np.power(omega, 4) + 1296))

plot_flag = input('Do you want to preview plots? [y/n]: ')
csv_flag = input('Do you want to generate plots in .csv? [y/n]: ')

## Function names array
fn_arr=[[H_hpf_2, '$H_{hpf\_2}(s)$', 'H_hpf_2'],
        [H_lpf_2, '$H_{lpf\_2}(s)$', 'H_lpf_2'],
        [H_bpf_2, '$H_{bpf\_2}(s)$', 'H_bpf_2'],
        [H_bpf_4, '$H_{bpf\_4}(s)$', 'H_bpf_4']]

class FnName(Enum):
    fn = 0
    tex = 1
    name = 2

## Define ranges
x = np.linspace(ranges[Axis.x.value][0], ranges[Axis.x.value][1], ticks[Axis.x.value])
y = np.linspace(ranges[Axis.y.value][0], ranges[Axis.y.value][1], ticks[Axis.y.value])
X, Y = np.meshgrid(x, y)

print('####')
print(X)
print('####')
print(Y)
print('####')
## Plot size
fig = plt.figure(dpi=150, figsize=[30,30])

for fn_num in range(len(fn_arr)):
    # Calculate values of function
    Z = np.array(fn_arr[fn_num][FnName.fn.value](X, Y))
    
    # Dump values in a .csv file
    if csv_flag == "y":
        X_flat = X.flatten()
        Y_flat = Y.flatten()
        Z_flat = Z.flatten()
        D_flat = np.transpose(np.vstack([X.flatten(), Y.flatten(), Z.flatten()]))
        pd.DataFrame(D_flat).to_csv(fn_arr[fn_num][FnName.name.value] + ".csv", header=False, index=False)
        pd.DataFrame([np.min(Z), np.max(Z), ticks[Axis.x.value], ticks[Axis.y.value]]).to_csv(fn_arr[fn_num][FnName.name.value] + "_limits.csv", header=False, index=False)

    # Generate plot preview
    if plot_flag == "y":
        ax = fig.add_subplot(1, 4, fn_num+1, projection='3d')
        surf = ax.plot_surface(X, Y, Z,cmap='viridis')
        ax.set_title(fn_arr[fn_num][1])
        fig.colorbar(surf ,ax=ax, shrink=0.5, aspect=5)
        ax.set_xlim(ranges[Axis.x.value][0], ranges[Axis.x.value][1])
        ax.set_ylim(ranges[Axis.y.value][0], ranges[Axis.y.value][1],)
        ax.set_zlim(np.min(Z), np.max(Z))
        ax.set_xlabel('$\sigma[]$')
        ax.set_ylabel('$\omega[s^{-1}]$')
        ax.set_zlabel('$|H(s)|[dB]$')

if plot_flag == "y":
    plt.show()
