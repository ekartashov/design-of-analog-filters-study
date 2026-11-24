#!/usr/bin/env python3

## A sctipt that generates PGF/TikZ data for 3D plotting.

##
## Warning: TeX variables with locally predefined names and files with function names in script directory will be overwritten!!
##

## About:
# When run, the script generates four files in its directory per defined function in [EDIT] section: 
# 1. <fn_name>.csv          --> Point data in x, y, z order (one line = one point)
# 2. <fn_name>_anchors.csv  --> Anchor point data per line in patch type order defined in PGF help document (one line = one patch)
# 3. <fn_name>_def.tex      --> TeX file to include in target TeX document to define variables for one plot
# 3. All_plots_undef.tex          --> TeX file to include in target TeX document to unset ALL script defined variables

import sys, math
import pandas as pd
import numpy as np
from enum import Enum
from numpy import inf
from tabulate import tabulate
import textwrap
# Graph preview modules
# from mpl_toolkits import mplot3d
# import matplotlib.pyplot as plt

# Ignore by zero division, it will give 'inf' and be corrected
np.seterr(divide='ignore')
# Set numpy print options
np.set_printoptions(formatter={'float': '{: 0.3f}'.format})

class PatchType:
    def __init__(self, indexes, scale):
        self.indexes = indexes
        self.scale = scale

class PlotFunc:
    filename = None
    inputs = []
    func = None
    ticks = None 
    titles = None
    ranges = None
    patch_type = None
    precisions = None
    title = None
    legends = {}
    def __init__(self, filename, inputs, func, ticks, tiles, ranges, patch_type, *args, **kwargs):
        self.filename = filename
        self.inputs = inputs
        self.func = func
        self.ticks = ticks
        self.tiles = tiles
        self.ranges = ranges
        self.patch_type = patch_type
        self.precisions = kwargs.get('precisions', [3, 3, 3])
        self.title = kwargs.get('title', None)
        self.limit_shifts = kwargs.get('limit_shifts', np.array([[1.05, 1.05], [1.05, 1.05], [1.05, 1.05]]))
        for ax_i, ax in enumerate(['x','y','z']):
            self.legends = kwargs.get('legends', ['x','y','z'])
        
    def print_info(self):
        table = []
        for var in vars(PlotFunc):
            if not var.startswith('__') and not var.endswith('__'):
                wrapped_msg = textwrap.fill(str(eval('self.' + var)), 50)
                table.append([var.capitalize(), wrapped_msg])
        print(tabulate(table, tablefmt='grid'))
    
    def exec_(self, *args, **kwargs):
        if len(args) != len(self.inputs):
            raise Exception("Missing arguments to assing as inputs")
        else:
            for iter_, input_ in enumerate(self.inputs):
                exec(input_ + ' = args[iter_]')
        return eval(self.func)

coons =  PatchType(indexes=[[0, 0],[1, 0],[2, 0],[3, 0],[3, 1],[3, 2],[3, 3],[2, 3],[1, 3],[0, 3],[0, 2],[0, 1]], scale=3)
biquad = PatchType(indexes=[[0, 0],[2, 0],[2, 2],[0, 2],[1, 0],[2, 1],[1, 2],[0, 1],[1, 1]], scale=2)
rectangle = PatchType(indexes=[[0, 0],[1, 0],[1, 1],[0, 1]], scale=1)

fn_names = []

class Ax(Enum):
    x = 0
    y = 1
    z = 2

class Ex(Enum):
    m = 0
    M = 1

class Cl(Enum):
    r = 0
    c = 1

def get_anchor(tile_number, scale):
    return (scale) * (tile_number + 1)

def get_first_anchor(tile_number, scale):
    return get_anchor(tile_number - 1, scale)

def get_last_anchor(tile_number, scale):
    return get_anchor(tile_number, scale) + 1

def set_tex_func(name, var):
    return '\\newcommand{\\' + str(name) + '}' + '{' + str(var) + '}'

def unset_tex_func(name):
    return '\\let\\' + name + '\\undefined'

def get_next_tick(min, max, ticks):
    return min + ((abs(min) + abs(max))/(ticks - 1))

################
## EDIT BEIGN ##
################

hpf_2 = PlotFunc(
    filename = 'hpf_2',
    inputs = ['sigma', 'omega'],
    func = '20 * np.log10(np.divide((np.power(omega, 2) + np.power(sigma, 2)), np.sqrt(5.656854248 * np.power(omega, 2) * sigma + 5.656854248 * np.power(sigma, 3) + 22.62741699 * sigma + np.power(sigma, 4) + (2 * np.power(omega, 2) + 16) * np.power(sigma, 2) + np.power(omega, 4) + 16)))',
    legends = ['$\sigma$', '$\omega$', '$\lvert H_{HPF\\_II}(s) \\rvert$'],
    ticks = np.array([5, 5, 5]),
    tiles = np.array([25, 25]),
    ranges = np.array([[-5, 5],[-5, 5],[-40,30]]),
    patch_type = coons
)
fn_names.append('hpf_2')

lpf_2 = PlotFunc(
    filename = 'lpf_2',
    inputs = ['sigma', 'omega'],
    func = '20 * np.log10(np.divide(4 , np.sqrt(5.656854248 * np.power(omega, 2) * sigma + 5.656854248 * np.power(sigma, 3) + 22.62741699 * sigma + np.power(sigma, 4) + (2 * np.power(omega, 2) + 16) * np.power(sigma, 2) + np.power(omega, 4) + 16)))',
    legends = ['$\sigma$', '$\omega$', '$\lvert H_{LPF\\_II}(s) \\rvert$'],
    ticks = np.array([5, 5, 5]),
    tiles = np.array([25, 25]),
    ranges = np.array([[-5, 5],[-5, 5],[-40,30]]),
    patch_type = coons
)
fn_names.append('lpf_2')

bpf_2 = PlotFunc(
    filename = 'bpf_2',
    inputs = ['sigma', 'omega'],
    func = '20 * np.log10(2.828427124 * np.sqrt(np.power(omega, 2) + np.power(sigma, 2)) * np.sqrt(np.divide(1, (5.656854248 * np.power(omega, 2) * sigma + 5.656854248 * np.power(sigma, 3) + 22.62741699 * sigma + np.power(sigma, 4) + (2 * np.power(omega, 2) + 16) * np.power(sigma, 2) + np.power(omega, 4) + 16))))',
    legends = ['$\sigma$', '$\omega$', '$\lvert H_{BPF\\_II}(s) \\rvert$'],
    ticks = np.array([5, 5, 5]),
    tiles = np.array([25, 25]),
    ranges = np.array([[-5, 5],[-5, 5],[-40,30]]),
    patch_type = coons
)

fn_names.append('bpf_2')

bpf_4 = PlotFunc(
    filename = 'bpf_4',
    inputs = ['sigma', 'omega'],
    func = '20 * np.log10(np.divide((9 * np.power(omega, 2) + 9 * np.power(sigma, 2)), np.sqrt(14.14213562 * (np.power(sigma, 4) + (2 * np.power(omega, 2) + 25) * np.power(sigma, 2) + np.power(omega, 4) + np.power(omega, 2) + 36)*(np.power(omega, 2) + np.power(sigma, 2) + 6) * sigma + np.power(sigma, 8) + (4 * np.power(omega, 2) + 100) * np.power(sigma, 6) + (6 * np.power(omega, 4) + 200 * np.power(omega, 2) + 1297) * np.power(sigma, 4) + (4 * np.power(omega, 6) + 100 * np.power(omega, 4) + 818 * np.power(omega, 2) + 3600 ) * np.power(sigma, 2) + np.power(omega, 8) + 97* np.power(omega, 4) + 1296)))',
    legends = ['$\sigma$', '$\omega$', '$\lvert H_{BPF\\_IV}(s) \\rvert$'],
    ticks = np.array([5, 5, 5]),
    tiles = np.array([25, 25]),
    ranges = np.array([[-5, 5],[-5, 5],[-50,40]]),
    patch_type = coons
)
fn_names.append('bpf_4')

##############
## EDIT END ##
##############

for fn in fn_names:
    # Prompt
    eval(fn + '.print_info()')
    print('')
    
    # Plot function setup
    for attr in vars(eval(fn)):
        exec("{0} = {1}.{0}".format(attr, fn))

    points_numbers = get_last_anchor(tiles, patch_type.scale)
    points = [np.linspace(ranges[Ax.x.value][Ex.m.value], ranges[Ax.x.value][Ex.M.value], points_numbers[Ax.x.value]), np.linspace(ranges[Ax.y.value][Ex.m.value], ranges[Ax.y.value][Ex.M.value], points_numbers[Ax.y.value])]
    X, Y = np.meshgrid(points[Ax.x.value], points[Ax.y.value])
    
    # Points
    Z = np.array(eval(fn + '.exec_(X, Y)'))
    Z[Z == -inf] = ranges[Ax.z.value][Ex.m.value]
    Z[Z == inf] = ranges[Ax.z.value][Ex.M.value]
    Z[Z <= ranges[Ax.z.value][Ex.m.value]] = ranges[Ax.z.value][Ex.m.value]
    Z[Z >= ranges[Ax.z.value][Ex.M.value]] = ranges[Ax.z.value][Ex.M.value]

    X_flat = X.flatten().reshape(np.prod(Z.shape), 1).round(decimals=3)
    Y_flat = Y.flatten().reshape(np.prod(Z.shape), 1).round(decimals=3)
    Z_flat = Z.flatten().reshape(np.prod(Z.shape), 1).round(decimals=3)
    pd.DataFrame(np.hstack((X_flat, Y_flat, Z_flat))).to_csv(fn + ".csv", header=False, index=False)

    Z_n = np.arange(points_numbers[Cl.r.value] * points_numbers[Cl.c.value]).reshape(points_numbers[Cl.r.value], points_numbers[Cl.c.value])
    A = np.zeros((0, len(patch_type.indexes)))
    A_i = np.zeros(0)
    A_ir = np.zeros(0)
    
    # Patches' anchors
    for t_r in range(tiles[Cl.r.value] + 1):
        for t_c in range(tiles[Cl.c.value] + 1):
            A_ir = Z_n[get_first_anchor(t_r, patch_type.scale):get_last_anchor(t_r, patch_type.scale), get_first_anchor(t_c, patch_type.scale):get_last_anchor(t_c, patch_type.scale)]
            A_i = np.zeros(0)
            for index in patch_type.indexes:
                A_i = np.concatenate((A_i, [A_ir[index[Cl.r.value], index[Cl.c.value]]]), axis=0)
            A_ir = np.zeros(0)
            A = np.concatenate((A, [A_i.flatten()]), axis=0)
    pd.DataFrame(A).to_csv(fn + "_anchors.csv", header=False, index=False)
    
    # fig = plt.figure()
    # ax = plt.axes(projection='3d')
    # ax.plot_surface(X, Y, Z, rstride=1, cstride=1,cmap='viridis', edgecolor='none')
    # ax.set_title('surface')
    # plt.show()

    # Limits

    contents = ''
    contents += set_tex_func('minX', str(ranges[Ax.x.value][Ex.m.value] * limit_shifts[Ax.x.value][Ex.m.value])) + '%\n'
    contents += set_tex_func('maxX', str(ranges[Ax.x.value][Ex.M.value] * limit_shifts[Ax.x.value][Ex.M.value])) + '%\n'
    
    contents += set_tex_func('minY', str(ranges[Ax.y.value][Ex.m.value] * limit_shifts[Ax.y.value][Ex.m.value])) + '%\n'
    contents += set_tex_func('maxY', str(ranges[Ax.y.value][Ex.M.value] * limit_shifts[Ax.y.value][Ex.M.value])) + '%\n'

    contents += set_tex_func('minZ', str(math.floor(np.min(Z)) * limit_shifts[Ax.z.value][Ex.m.value])) + '%\n'
    contents += set_tex_func('maxZ', str(math.floor(np.max(Z)) * limit_shifts[Ax.z.value][Ex.M.value])) + '%\n'

    contents += set_tex_func('minTickX', str(ranges[Ax.x.value][Ex.m.value])) + '%\n'
    contents += set_tex_func('nextTickX', str(get_next_tick(ranges[Ax.x.value][Ex.m.value], ranges[Ax.x.value][Ex.M.value], ticks[Ax.x.value]))) + '%\n'
    contents += set_tex_func('maxTickX', str(ranges[Ax.x.value][Ex.M.value])) + '%\n'

    contents += set_tex_func('minTickY', str(ranges[Ax.y.value][Ex.m.value])) + '%\n'
    contents += set_tex_func('nextTickY', str(get_next_tick(ranges[Ax.y.value][Ex.m.value], ranges[Ax.y.value][Ex.M.value], ticks[Ax.y.value]))) + '%\n'
    contents += set_tex_func('maxTickY', str(ranges[Ax.y.value][Ex.M.value])) + '%\n'

    contents += set_tex_func('minTickZ', str(math.floor(np.min(Z)))) + '%\n'
    contents += set_tex_func('nextTickZ', str(get_next_tick(math.floor(np.min(Z)), math.floor(np.min(Z)), ticks[Ax.z.value]))) + '%\n'
    contents += set_tex_func('maxTickZ', str(math.floor(np.max(Z)))) + '%\n'

    for axis_i, axis in enumerate(['x', 'y', 'z']):
        contents += set_tex_func('legend' + axis.upper(), legends[axis_i]) + '%\n'

    contents += set_tex_func('ticksX', str(points_numbers[Cl.r.value])) + '%\n'
    contents += set_tex_func('ticksY', str(points_numbers[Cl.r.value])) + '%'
    
    fn_set = open(fn + "_def.tex", "wt")
    fn_set.write(contents)
    fn_set.close()

    # Graph preview
    # fig = plt.figure()
    # ax = plt.axes(projection='3d')
    # ax.plot_surface(X, Yl, Z, rstride=1, cstride=1,cmap='viridis', edgecolor='none')
    # ax.set_title('surface')
    # plt.show()


contents = ''
contents += unset_tex_func('minX') + '%\n'
contents += unset_tex_func('maxX') + '%\n'

contents += unset_tex_func('minY') + '%\n'
contents += unset_tex_func('maxY') + '%\n'

contents += unset_tex_func('minZ') + '%\n'
contents += unset_tex_func('maxZ') + '%\n'

contents += unset_tex_func('minTickX') + '%\n'
contents += unset_tex_func('nextTickX') + '%\n'
contents += unset_tex_func('maxTickX') + '%\n'

contents += unset_tex_func('minTickY') + '%\n'
contents += unset_tex_func('nextTickY') + '%\n'
contents += unset_tex_func('maxTickY') + '%\n'

contents += unset_tex_func('minTickZ') + '%\n'
contents += unset_tex_func('nextTickZ') + '%\n'
contents += unset_tex_func('maxTickZ') + '%\n'

for axis in ['x', 'y', 'z']:
    contents += unset_tex_func('legend' + axis.upper()) + '%\n'

contents += unset_tex_func('ticksX') + '%\n'
contents += unset_tex_func('ticksY') + '%'

fn_unset = open("All_plots_undef.tex", "wt")
fn_unset.write(contents)
fn_unset.close()