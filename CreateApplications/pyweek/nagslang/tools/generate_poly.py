import optparse
import sys
import math


def parse_params(args):
    params = {}
    for arg in args:
        key, _, value = arg.partition("=")
        params[key] = value
    return params


def parse_args(args):
    """Parse arguments."""
    parser = optparse.OptionParser(usage="%prog <type> arg1=foo arg2=bar")

    parser.add_option('-x',
                      dest='offset_x', type=int, default=0,
                      help='X offset for poly.')

    parser.add_option('-y',
                      dest='offset_y', type=int, default=0,
                      help='Y offset for poly.')

    opts, args = parser.parse_args(args)
    args = args[1:]

    if not args:
        parser.print_help()
        return None, {}, opts

    obj_type = args[0]
    params = parse_params(args[1:])
    return obj_type, params, opts


class PolyGenerator(object):
    def __init__(self, opts):
        self.offset_x = opts.offset_x
        self.offset_y = opts.offset_y

    def generate(self, obj_type, params):
        handler = getattr(self, 'generate_%s' % (obj_type,),
                          self.unknown_type)
        return handler(params)

    def print_poly(self, poly):
        print "Poly:"
        for point in poly:
            print "  - [%d, %d]" % tuple(point)

    def unknown_type(self, params):
        prefix = "generate_"
        known_types = [k[len(prefix):] for k in self.__dict__
                       if k.startswith(prefix)]
        raise ValueError("Unknown object type. Known types: %s" %
                         ",".join(known_types))

    def check_params(self, params, *sigs):
        results = []
        for name, parser in sigs:
            value = params.get(name)
            try:
                result = parser(value)
            except:
                raise ValueError(
                    "Failed to parse param %s with value %s (parser: %r)"
                    % (name, value, parser))
            results.append(result)
        return results

    def apply_opts(self, poly):
        new_poly = []
        for p in poly:
            x = p[0] + self.offset_x
            y = p[1] + self.offset_y
            new_poly.append([x, y])
        return new_poly

    def generate_circle(self, params):
        r, steps = self.check_params(params, ("r", int), ("steps", int))
        poly = []
        rad, step_size = 0, 2 * math.pi / steps
        for p in range(steps + 1):
            x, y = r * math.sin(rad), r * math.cos(rad)
            poly.append([x, y])
            rad += step_size
        return self.apply_opts(poly)


if __name__ == "__main__":
    obj_type, params, opts = parse_args(sys.argv)
    if obj_type is not None:
        p = PolyGenerator(opts)
        poly = p.generate(obj_type, params)
        p.print_poly(poly)
