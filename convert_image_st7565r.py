#!/usr/bin/python
#
# This program converts an image to a C byte array suitable for sending to a
# Newhaven NHD-C12832A1Z-FSW-FBW-3V3 LCD. It probably works for other displays
# based on the ST7565R chip or similar chips as well.
#
# This takes an image as input (any format supported by PIL will work) and
# prints a C definition to standard output. The image must have a height
# divisible by 8.
#
# The image is treated as monochrome. Any image pixel that is either white or
# completely transparent will show up as white on the display. Any other pixel
# will show up as black.
#
# This program requires Python and PIL (the Python Image Library).
#
# Usage:
#   convert_image_st7565r.py IMAGEFILE
#
# The data format is described in the data sheet:
#
# http://www.newhavendisplay.com/app_notes/ST7565R.pdf
#
# This was written by Aaron Isotton in 2016 and is in the public domain. Do with
# it whatever you want.

import os.path
import PIL.Image
import sys

def run(infile):
    image = PIL.Image.open(infile)
    if image.height % 8:
        raise RuntimeError('Image height should be multiple of 8, but is %s',
                           image.height)
    # We convert to RGBA to have a consistent data format.
    image = image.convert('RGBA')

    # The common direction of the NHD-C12832A1Z-FSW-FBW-3V3 is right-up, meaning
    # that (0, 0) is at the bottom left. We have to mirror the image vertically
    # to compensate for that.
    image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)

    print '/* %s (%sx%s) */' % (os.path.basename(infile), image.width, image.height)
    print 'uint8_t data[%d] = {' % (image.height * image.width / 8)
    for page in range(image.height / 8):
        print '    ',
        for x in range(image.width):
            byte = 0
            for row in range(8):
                pos = (x, page * 8 + row)
                r, g, b, a = image.getpixel(pos)
                # Any pixel that is white or transparent will become white on
                # the display. Any other pixel will become black.
                bit = int(a > 0 and (r < 255 or g < 255 or b < 255))
                byte |= (bit << row)
            print '0x%02x,' % byte,
        print
    print '};'

def main():
    try:
        if len(sys.argv) != 2:
            raise RuntimeError('Usage: %s IMAGEFILE' % sys.argv[0])
        run(sys.argv[1])
    except RuntimeError as e:
        print >> sys.stderr, 'Error: %s' % e
        sys.exit(1)

if __name__ == '__main__': main()
