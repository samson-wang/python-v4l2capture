#!/usr/bin/python
#
# python-v4l2capture
#
# This file is an example on how to capture a picture with
# python-v4l2capture. It waits between starting the video device and
# capturing the picture, to get a good picture from cameras that
# require a delay to get enough brightness. It does not work with some
# devices that require starting to capture pictures immediatly when
# the device is started.
#
# 2009, 2010 Fredrik Portstrom
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

from PIL import Image
import select
import time
import v4l2capture
import sys
import glob
import re

fnames = glob.glob(sys.argv[1] + "/*.jpg")
ids = [int(_) for _ in filter(lambda t: t, [re.findall(ur'0+(\d*)', _)[0] for _ in fnames]) ]
next_id = max(ids) + 1 if ids else 1
print next_id

# Open the video device.
video = v4l2capture.Video_device("/dev/video0")

# Suggest an image size to the device. The device may choose and
# return another size if it doesn't support the suggested one.
size_x, size_y = video.set_format(1920, 1920)

# Create a buffer to store image data in. This must be done before
# calling 'start' if v4l2capture is compiled with libv4l2. Otherwise
# raises IOError.
video.create_buffers(1)

# Start the device. This lights the LED if it's a camera that has one.
video.start()

# Wait a little. Some cameras take a few seconds to get bright enough.
time.sleep(1)

# Send the buffer to the device.
video.queue_all_buffers()

# Wait for the device to fill the buffer.
select.select((video,), (), ())

# The rest is easy :-)
image_data = video.read()
video.close()
image = Image.frombytes("RGB", (size_x, size_y), image_data)
image.save(sys.argv[1] + '/image_%08d.jpg' % next_id)
print "Saved image.jpg (Size: " + str(size_x) + " x " + str(size_y) + ")"
