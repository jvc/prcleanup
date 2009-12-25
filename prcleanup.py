#!/usr/bin/env python
'''
prcleanup.py - Delete poor quality videos.

Possibly the most handy hack-job script ever written. Instead of removing the
files, I prefer to print output that can be piped to /bin/sh. That way I can
look it over first, then run sh on it to actually remove.


Usage:
./prcleanup.py DIRECTORY [DIRECTORY..]
ie:

1.) Build the script
% ./prcleanup.py /videos > rm_script
2.) Examine the script (should actually edit it to remove the gems)
% cat rm_script
3.) Execute with ^p | sh
% cat rm_script | sh
'''

__version__   = "0.2"
__date__      = "2009-08-14"
__author__    = "Justin Chouinard <jvc@jvic.net)>"
__copyright__ = "Copyright 2009, Justin Chouinard"
__license__   = "MIT"

from subprocess import Popen, PIPE
import sys
import re
import os

'''The file name must match this list to be considered for removal.'''
ALLOWED_FILES = '\.(asf|wmv|mpg|avi|mpeg|mov|mp4)$';

'''The media must match fields is to the list of minimums to allow.'''
MINIMUMS = {
    'xres': 320,
    'yres': 240,
    'kbps': 400
    }


##############################################################################
allowed_file_re = re.compile(ALLOWED_FILES)

#VIDEO:  MPEG1  318x232  (aspect 1)  29.970 fps  1196.4 kbps (149.6 kbyte/s)
#VIDEO:  [XVID]  512x384  24bpp  29.970 fps  1196.3 kbps (146.0 kbyte/s)
vid_re = re.compile('^VIDEO:\s+[\[\]\w]+\s+(\d+)x(\d+)\s+.*' +
                    '\s+([\d\.]+)\s+fps\s+([\d\.]+)\s+kbps',
                    re.MULTILINE)

def check_file(file_name):
    if allowed_file_re.search(file_name) == None:
        return

    output = Popen(("mplayer", "-identify", "-frames", "0",
                    "-ao", "null", file_name),
                   stdout=PIPE, stderr=PIPE).communicate()[0]
    
    match = vid_re.search(output)
    if match == None:
        sys.stderr.write(output)
    else:
        videoInfo = {
            'file_name': file_name,
            'xres': int(match.group(1)),
            'yres': int(match.group(2)),
            'fps': match.group(3),
            'kbps': abs(float(match.group(4)))
        }

        for key in MINIMUMS:
            if videoInfo[key] == 0:
                pass
            elif videoInfo[key] < MINIMUMS[key]:
                print '# %s at %d did not reach the minimum of %d' % (key, videoInfo[key], MINIMUMS[key])
                print 'rm \"%s\"' % (file_name)
                break

def check_directory(path):
    for root, dirs, files in os.walk(path):
        for directory in dirs:
            check_directory(directory)
        for file_name in files:
            check_file(os.path.join(root, file_name))
        

def usage():
    print >>sys.stderr, __doc__
    
def main():
    for path in sys.argv[1:]:
        check_directory(path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    else:
        main()

