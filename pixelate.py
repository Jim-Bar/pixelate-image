#!/usr/bin/env python3

# Copyright (c) 2020 Jean-Marie Baran
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from PIL import Image  # Pillow (fork of Python Imaging Library PIL).
from PIL.PyAccess import PyAccess
from typing import Tuple
import operator
import os
import sys


def _check_macro_pixel(image_src: Image.Image, macro_pixel_size: int) -> None:
    if image_src.size[0] % macro_pixel_size != 0:
        raise ValueError('Cannot use macro pixels of size {} for width {}'.format(macro_pixel_size, image_src.size[0]))
    if image_src.size[1] % macro_pixel_size != 0:
        raise ValueError('Cannot use macro pixels of size {} for height {}'.format(macro_pixel_size, image_src.size[1]))


def _colorize_256_bits(image_dst: Image.Image) -> Image.Image:
    return image_dst.quantize(256)


def _create_dst_image(image_src: Image.Image) -> Tuple[Image.Image, PyAccess]:
    image_dst = Image.new(image_src.mode, (image_src.size[0], image_src.size[1]))
    image_dst_data = image_dst.load()

    return image_dst, image_dst_data


def _do_pixelate(image_src: Image.Image, image_src_data: PyAccess, image_dst_data: PyAccess, size: int) -> None:
    for i in range(0, image_src.size[0] // size):
        for j in range(0, image_src.size[1] // size):
            average_color = _get_average_color(image_src_data, i * size, j * size, size, size)
            _fill_with_color(image_dst_data, average_color, i * size, j * size, size, size)


def _fill_with_color(image_data: PyAccess, average_color: Tuple[int, int, int], i: int, j: int, w: int, h: int) -> None:
    for x in range(i, i + w):
        for y in range(j, j + h):
            image_data[x, y] = average_color


def _get_average_color(image_data: PyAccess, i: int, j: int, w: int, h: int) -> Tuple[int, int, int]:
    average = (0, 0, 0)
    for x in range(i, i + w):
        for y in range(j, j + h):
            average = tuple(map(operator.add, average, image_data[x, y]))
    return tuple([value // (w * h) for value in average])


def _open_src_image(image_path: str) -> Tuple[Image.Image, PyAccess]:
    image_src = Image.open(image_path)
    image_src_data = image_src.load()

    return image_src, image_src_data


def _pixelate(image_path: str, macro_pixel_size: int) -> Image.Image:
    image_src, image_src_data = _open_src_image(image_path)
    image_dst, image_dst_data = _create_dst_image(image_src)

    _check_macro_pixel(image_src, macro_pixel_size)
    _do_pixelate(image_src, image_src_data, image_dst_data, macro_pixel_size)

    return image_dst


def _save_image(image_dst: Image.Image, image_path: str) -> None:
    image_dst.convert('RGB').save(image_path)


def run(image_src_path: str, image_dst_path: str, macro_pixel_size: int) -> None:
    try:
        image_dst = _pixelate(image_src_path, macro_pixel_size)
        image_dst = _colorize_256_bits(image_dst)
        image_dst.show()
        _save_image(image_dst, image_dst_path)
    except ValueError as exception:
        print(exception)

if __name__ == '__main__':
    try:
        run(sys.argv[1], 'pixelated_{}'.format(os.path.basename(sys.argv[1])), int(sys.argv[2]))
    except IndexError:
        print('Usage: {} <image_path> <pixel_size>'.format(sys.argv[0]))
