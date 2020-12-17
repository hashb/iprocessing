# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from .color_data import COLORS


class Color:
    def __init__(self, red, green=None, blue=None, alpha=None):
        self.name = None
        if isinstance(red, str):
            if red.startswith("#"):
                # encoded hex color
                red, green, blue, alpha = self.hex_to_rgba(red)
            else:
                # color name
                self.name = red
                hex_string = COLORS.get(red, "#00000000")
                red, green, blue, alpha = self.hex_to_rgba(hex_string)
        elif isinstance(red, (list, tuple)):
            if len(red) == 3:
                red, green, blue = red
                alpha = 255
            else:
                red, green, blue, alpha = red

        self.red = red
        if green is not None:
            self.green = green
        else:
            self.green = red
        if blue is not None:
            self.blue = blue
        else:
            self.blue = red
        if alpha is not None:
            self.alpha = alpha
        else:
            self.alpha = 255

    def hex_to_rgba(self, hex_string):
        r_hex = hex_string[1:3]
        g_hex = hex_string[3:5]
        b_hex = hex_string[5:7]
        if len(hex_string) > 7:
            a_hex = hex_string[7:9]
        else:
            a_hex = "FF"
        return int(r_hex, 16), int(g_hex, 16), int(b_hex, 16), int(a_hex, 16)

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return self.to_hexcode()

    def __repr__(self):
        return "<Color%s>" % (self.to_tuple(),)

    def to_tuple(self):
        return (int(self.red), int(self.green), int(self.blue), int(self.alpha))

    def to_hexcode(self):
        return "#%02X%02X%02X%02X" % self.to_tuple()


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point(%s,%s)" % (self.x, self.y)


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return "Line(%s,%s)" % (self.p1, self.p2)
