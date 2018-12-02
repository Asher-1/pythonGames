import pyglet.resource

def cargar(imagen):
    img = pyglet.resource.image (imagen)
    return img.get_region (1,1, img.width-2, img.height-1)

Vector = complex

def to_tuple(v):
    return v.real, v.imag

def intersection (p, v, x1, x2):
    """Intersection of ray at p with direction v with then segement going
    from x1 to x2
    Requires x1 != x2"""
    w, z = to_tuple(x2-x1)
    x, y = to_tuple(x1-p)
    divisor = v.imag*w - v.real*z
    if -1e-8 < divisor < 1e-8: return None # Parallel
    k1 = (w*y - x*z) / divisor
    i = p+k1*v # Intersection point, perhaps not in segment
    if k1 >=0 and 0.0 <= ((i-x1)/(x2-x1)).real <= 1.0: # Forwards and inside segment
        return i
    else:
        return None
    
    
