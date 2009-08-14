#!/usr/bin/env python
#
# video_cleanup.py - Delete poor quality videos.
#
# Author: Justin Chouinard <jchouinard@blackpantssoftware.com>
#
# Possibly the most handy hack-job script ever written. Instead of removing the
# files, I prefer to print output that can be piped to /bin/sh. That way I can
# look it over first, then run sh on it to actually remove.
#
# Example usage:
#
# 1.) Build the script
#  % ./video_cleanup.py someDir
# 2.) Examine
#  % cat rm_script
# 3.) Execute
#  % cat rm_script | sh
#

from subprocess import Popen, PIPE
import sys
import re
import os

minimum = {
    'xres': 320,
    'yres': 240,
    'kbps': 400
    }

ALLOWED_FILES = '\.(asf|wmv|mpg|avi|mpeg|mov|mp4)$';

allowedFileRe = re.compile(ALLOWED_FILES)
#VIDEO:  MPEG1  318x232  (aspect 1)  29.970 fps  1196.4 kbps (149.6 kbyte/s)
#VIDEO:  [XVID]  512x384  24bpp  29.970 fps  1196.3 kbps (146.0 kbyte/s)
vidRe = re.compile('^VIDEO:\s+[\[\]\w]+\s+(\d+)x(\d+)\s+.*\s+([\d\.]+)\s+fps\s+([\d\.]+)\s+kbps', re.MULTILINE)

def check_file(fileName):
    if allowedFileRe.search(fileName) == None:
        return

    output = Popen(("mplayer", "-identify", "-frames", "0", "-ao", "null", fileName), stdout=PIPE, stderr=PIPE).communicate()[0]
    match = vidRe.search(output)
    if match == None:
        sys.stderr.write(output)
    else:
        videoInfo = {
            'fileName': fileName,
            'xres': int(match.group(1)),
            'yres': int(match.group(2)),
            'fps': match.group(3),
            'kbps': abs(float(match.group(4)))
        }

        for key in minimum:
            if videoInfo[key] == 0:
                pass
            elif videoInfo[key] < minimum[key]:
                print '# %s at %d did not reach the minimum of %d' % (key, videoInfo[key], minimum[key])
                print 'rm \"%s\"' % (fileName)
                break

def check_directory(path):
    for root, dirs, files in os.walk(path):
        for directory in dirs:
            check_directory(directory)
        for fileName in files:
            check_file(os.path.join(root, fileName))
        

def main():
    for path in sys.argv[1:]:
        check_directory(path)

if __name__ == '__main__':
    main()


