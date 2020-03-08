# Python 2.7

import Image # Python Imaging Library (PIL)
import operator
import os
import sys

def pixelize(picture, step):
  img_src = Image.open(picture)
  pixels_src = img_src.load()

  if img_src.size[0] % step != 0 or img_src.size[1] % step != 0:
    print('Not divisible!')
  else:
    img_dst = Image.new(img_src.mode, (img_src.size[0], img_src.size[1]))
    pixels_dst = img_dst.load()
    for i in range(0, img_src.size[0] / step):
      for j in range(0, img_src.size[1] / step):
        averageColor = getAverageColor(pixels_src, i * step, j * step, step, step)
        fillWithColor(pixels_dst, averageColor, i * step, j * step, step, step)
    img_dst = img_dst.quantize(256)
    img_dst.show()
    img_dst.convert('RGB').save('Pixelized_{}'.format(os.path.basename(picture)))

def getAverageColor(pixels, i, j, w, h):
  average = (0, 0, 0)
  for x in range(i, i + w):
    for y in range(j, j + h):
      average = tuple(map(operator.add, average, pixels[x, y]))
  return tuple([value / (w * h) for value in average])

def fillWithColor(pixels, averageColor, i, j, w, h):
  for x in range(i, i + w):
    for y in range(j, j + h):
      pixels[x, y] = averageColor

try:
  pixelize(sys.argv[1], int(sys.argv[2]))
except IndexError:
  print('Usage: {} FILE PIXEL_SIZE'.format(sys.argv[0]))
