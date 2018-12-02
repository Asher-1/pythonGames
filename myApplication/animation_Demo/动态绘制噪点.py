#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author: Asher
@time:2018/2/24 20:01
'''

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

fig = plt.figure()
data = np.random.random((255, 255))
im = plt.imshow(data, cmap='gray')

# animation function.  This is called sequentially
def animate(i):
    data = np.random.random((255, 255))
    im.set_array(data)
    return [im]

anim = animation.FuncAnimation(fig, animate, frames=200, interval=60, blit=True)
plt.show()