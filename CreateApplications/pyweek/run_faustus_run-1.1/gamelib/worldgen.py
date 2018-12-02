import random
import vector

from gamelib.constants import *

def make_random_floor(length, xstep, ystep):
    cx = 0
    cy = random.randint(FLOOR_LOW, FLOOR_HIGH)
    yield vector.v(cx, cy)
    while cx < length:
        nx = cx + random.randint(xstep // 2, xstep * 3 // 2)
        ny = cy + random.randint(-ystep, ystep)
        ny = max(FLOOR_LOW, min(FLOOR_HIGH, ny))
        yield vector.v(nx, ny)
        cx = nx; cy = ny

def deepen_floor(floor, depth):
    a, b = floor[:2]
    yield a - (b - a).perpendicular().scaled_to(depth)
    for idx in xrange(1, len(floor) - 1):
        a, b, c = floor[idx-1:idx+2]
        ad = -(b - a).perpendicular().scaled_to(depth)
        cd = -(c - b).perpendicular().scaled_to(depth)
        x = (ad + cd).scaled_to(depth)
        dist = -(c - b).normalised().cross(x)
        yield b + x * depth / dist
    b, c = floor[-2:]
    yield c - (c - b).perpendicular().scaled_to(depth)

def make_long_feature(start, length, xstep, ystep, low, high):
    low = int(low)
    high = int(high)
    cx = start
    cy = random.randint(high - 3*ystep, high)
    yield vector.v(cx, cy)
    while cx < start+length:
        nx = cx + random.randint(xstep // 2, 3 * xstep // 2)
        ny = cy + random.randint(-ystep, ystep)
        ny = max(high - 3*ystep, min(high, ny))
        yield vector.v(nx, ny)
        cx = nx; cy = ny
    cx += random.randint(-xstep // 2, xstep // 2)
    cy = random.randint(low, low + 3*ystep)
    yield vector.v(cx, cy)
    while cx > start:
        nx = cx - random.randint(xstep // 2, 3 * xstep // 2)
        ny = cy + random.randint(-ystep, ystep)
        ny = max(low, min(low + 3*ystep, ny))
        yield vector.v(nx, ny)
        cx = nx; cy = ny

def deepen_feature(surface, depth):
    for idx, b in enumerate(surface):
        a = surface[(idx-1)%len(surface)]
        c = surface[(idx+1)%len(surface)]
        ad = -(b - a).perpendicular().scaled_to(depth)
        cd = -(c - b).perpendicular().scaled_to(depth)
        x = (ad + cd).scaled_to(depth)
        dist = -(c - b).normalised().cross(x)
        yield b + x * depth / dist

def make_simple_infinite_floor(xstep, ystep):
    low = FLOOR_LOW
    high = FLOOR_HIGH
    cx = 0
    cy = random.randint(low, high)
    yield vector.v(cx, cy)
    while True:
        cx += random.randint(xstep // 2, xstep * 3 // 2)
        cy = cy + random.randint(-ystep, ystep)
        cy = max(low, min(high, cy))
        yield vector.v(cx, cy)

def make_infinite_floor(xstep, ystep):
    low = FLOOR_LOW
    high = FLOOR_HIGH
    temp_high = None
    cx = 0
    cy = random.randint(low, high)
    cliff_timer = 0
    lf_timer = 0
    yield vector.v(cx, cy), None
    while True:
        cx += random.randint(xstep // 2, xstep * 3 // 2)
        if cx > lf_timer:
            temp_high = None
        if random.random() < 0.2 and not cliff_timer and cx > lf_timer:
            height = random.randint(low - cy, high - cy)
            cy += height
            yield vector.v(cx, cy), None
            cliff_timer = 10
        else:
            cy = cy + random.randint(-ystep, ystep)
            cy = max(low, min(temp_high or high, cy))
            f = None
            if random.random() < 0.05 and cx > lf_timer:
                pos = vector.v(cx, cy)
                l = random.randint(500, 1500)
                h = random.randint(200, 300)
                f = make_long_feature(pos.x, l, 30, 10, pos.y + h, pos.y + 400)
                temp_high = pos.y + h - 100
                lf_timer = cx + l + 200
            yield vector.v(cx, cy), f
        cliff_timer = max(0, cliff_timer - 1)

def deepen_infinite_floor(floor, depth):
    a, b = floor[:2]
    yield a - (b - a).perpendicular().scaled_to(depth)
    idx = 0
    while True:
        idx += 1
        a, b, c = floor[idx-1:idx+2]
        ad = -(b - a).perpendicular().scaled_to(depth)
        cd = -(c - b).perpendicular().scaled_to(depth)
        x = (ad + cd).scaled_to(depth)
        dist = -(c - b).normalised().cross(x)
        yield b + x * depth / dist
