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
import numpy as np
import cv2

fnames = glob.glob(sys.argv[1] + "/*.jpg")
ids = [int(_) for _ in filter(lambda t: t, [re.findall(ur'0+(\d*)', _)[0] for _ in fnames]) ]
next_id = max(ids) + 1 if ids else 1
print next_id

v_num = 1 if len(sys.argv) < 3 else int(sys.argv[2])
vids = range(v_num)
# Open the video device.
videos = [v4l2capture.Video_device("/dev/video%s" % _) for _ in vids] 

# Suggest an image size to the device. The device may choose and
# return another size if it doesn't support the suggested one.
for video in videos:
    size_x, size_y = video.set_format(1920, 1080)

    video.create_buffers(1)

    video.start()
# Create a buffer to store image data in. This must be done before
# calling 'start' if v4l2capture is compiled with libv4l2. Otherwise
# raises IOError.

# Start the device. This lights the LED if it's a camera that has one.

# Wait a little. Some cameras take a few seconds to get bright enough.
time.sleep(1)

# Send the buffer to the device.
img = np.zeros((1080, 1920, 3), dtype=np.uint8)
hh = 1080 / 2
hw = 1920 / 2
result = []
for k, video in enumerate(videos):
    video.queue_all_buffers()
    select.select((video,), (), ())
# Wait for the device to fill the buffer.

# The rest is easy :-)
    image_data = video.read()
    video.close()
    image = Image.frombytes("RGB", (size_x, size_y), image_data)
    cv_img = (np.array(image))[:,:,::-1]
    result.append(cv_img)
#    print cv_img, cv_img.shape
#    print (k/2)*hh, (k/2)*hh + hh,  (k%2)*hw, (k%2)*hw + hw
#    print img.shape
    snap = cv2.resize(cv_img, None, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
    img[(k/2)*hh:(k/2)*hh + hh, (k%2)*hw: (k%2)*hw + hw, :] = snap
#    image.save(sys.argv[1] + '/image_%08d_%d.jpg' % (next_id, vids[k]))
#    print "Saved image.jpg (Size: " + str(size_x) + " x " + str(size_y) + ")"

cv2.imshow('test', cv2.resize(img, None, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR))
pk = cv2.waitKey() & 0xFF

if pk == 113:
    print 'Discarded'
else:
    for k, i in enumerate(result):
        cv2.imwrite(sys.argv[1] + '/image_%08d_%d.jpg' % (next_id, vids[k]), i)
        print 'Save image', sys.argv[1] + '/image_%08d_%d.jpg' % (next_id, vids[k])
