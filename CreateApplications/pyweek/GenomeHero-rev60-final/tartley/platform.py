import sys

OSX = False
if sys.platform.startswith('darwin'):
    OSX = True
    print 'OSX platform found'

