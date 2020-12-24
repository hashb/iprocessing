# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

import io
import math

from PIL import Image, ImageDraw, ImageFont

from ..utils import Color, distance
from .base import Backend

DEFAULT_FONT_NAMES = (
    "arial.ttf",
    "Arial.ttf",
    "NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf",
    "/System/Library/Fonts/SFNSDisplay.ttf",
    "/Library/Fonts/Arial.ttf",
)


class PILBackend(Backend):
    # Specific to this class:

    def __init__(self, *args, **kwargs):
        self.widget = None
        super().__init__(*args, **kwargs)

    def initialize(self, **kwargs):
        self.matrix = []
        self.kwargs = kwargs
        self.font_size = kwargs.get("font_size", 24)
        self.mode = kwargs.get("mode", "RGB")
        self.format = kwargs.get("format", "jpeg")  # or "png", "gif", "jpeg"
        self.font = None
        for font_string_name in DEFAULT_FONT_NAMES:
            try:
                self.font = ImageFont.truetype(font_string_name, self.font_size)
                break
            except OSError:
                continue

        if self.mode == "RGBA" and self.format == "jpeg":
            print("WARNING: mode='RGBA' is not compatible with format='jpeg'")
            print("WARNING: switching mode to 'RGB'")
            self.mode = "RGB"
            kwargs["mode"] = "RGB"

        self.image = Image.new(
            self.mode,
            size=(int(self.width * self._scale), int(self.height * self._scale)),
        )
        self.draw = ImageDraw.Draw(self.image)

    def update_dimensions(self, width, height, scale):
        if width != self.width or height != self.height or self._scale != scale:
            self.width = width
            self.height = height
            self._scale = scale
            self.initialize(**self.kwargs)

    # Canvas API:

    def to_png(self):
        fp = io.BytesIO()
        self.image.save(fp, format=self.format)
        return fp.getvalue()

    def get_widget(self):
        from ipywidgets import Image

        if self.widget is None:
            self.widget = Image(value=self.to_png())
            self.widget.layout.margin = "auto"

        return self.widget

    def update_watchers(self):
        if self.widget:
            self.widget.value = self.to_png()

    def flush(self):
        pass

    def take_picture(self):
        return self.image

    # High-level API:

    def get_color(self, color):
        if isinstance(color, Color):
            return color.to_tuple()
        elif color != "":
            return color
        else:
            return None

    def get_style(self, style):
        if style == "fill":
            return self.get_color(self.fill_style)
        elif style == "stroke":
            return self.get_color(self.stroke_style)

    def p(self, x, y):
        for matrix in self.matrix:
            for transform in reversed(matrix):
                if transform[0] == "translate":
                    x += transform[1]
                    y += transform[2]
                elif transform[0] == "rotate":
                    dist = distance(0, 0, x, y)
                    angle2 = math.atan2(-x, y)
                    angle = transform[1]
                    x = dist * math.cos(angle2 + angle + math.pi / 2)
                    y = dist * math.sin(angle2 + angle + math.pi / 2)
        return x * self._scale, y * self._scale

    def draw_lines(self, points, stroke_style=None):
        self.stroke_style = stroke_style
        for i in range(len(points)):
            if i < len(points) - 2:
                self.draw_line(
                    points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]
                )

    def draw_line(self, x1, y1, x2, y2):
        p1x, p1y = self.p(x1, y1)
        p2x, p2y = self.p(x2, y2)
        self.draw.line(
            (p1x, p1y, p2x, p2y), fill=self.get_style("stroke"), width=self.line_width
        )

    def clear(self):
        # self.fill_style = "white"
        self.draw_rect(0, 0, self.width, self.height)

    def text(self, t, x, y):
        self.draw.text(self.p(x - 1, y - 1), t, fill="black", font=self.font)
        self.draw.text(self.p(x - 1, y + 1), t, fill="black", font=self.font)
        self.draw.text(self.p(x + 1, y + 1), t, fill="black", font=self.font)
        self.draw.text(self.p(x + 1, y - 1), t, fill="black", font=self.font)
        self.draw.text(self.p(x, y), t, fill=self.get_style("fill"), font=self.font)

    def pushMatrix(self):
        self.matrix.append([])

    def popMatrix(self):
        self.matrix.pop()

    def scale(self, x, y):
        pass

    def resetScale(self):
        pass

    def draw_rect(self, x, y, width, height):
        p1x, p1y = self.p(x, y)
        p2x, p2y = self.p(x + width, y)
        p3x, p3y = self.p(x + width, y + height)
        p4x, p4y = self.p(x, y + height)

        self.draw.polygon(
            (p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y),
            fill=self.get_style("fill"),
            outline=self.get_style("outline"),
        )

    def draw_ellipse(self, x, y, radiusX, radiusY):
        p1x, p1y = self.p(x, y)
        p2x, p2y = self.p(x + radiusX * 2, y)
        p3x, p3y = self.p(x + radiusX * 2, y + radiusY * 2)
        p4x, p4y = self.p(x, y + radiusY * 2)

        self.draw.polygon(
            (p1x, p1y, p2x, p3y, p3x, p3y, p4x, p4y),
            fill=self.get_style("fill"),
            outline=self.get_style("stroke"),
            #            width=self.line_width,
        )

    def draw_arc(self, x, y, width, height, startAngle, endAngle):
        # p1x, p1y = self.p(x, y)
        # p2x, p2y = self.p(x + width,
        #                  y + height)

        self.draw_line(x, y, x + width, y)

        # self.draw_ellipse(x, y, width/2, height/2)
        # self.draw_rect(x, y, width/2, height/2)

        # self.draw.arc(
        #    (p1x, p1y, p2x, p2y),
        #    startAngle * 180/math.pi,
        #    endAngle * 180/math.pi,
        #    fill=self.get_style("fill"),
        #    width=self.line_width,
        # )

    def beginShape(self):
        self.points = []

    def endShape(self):
        self.draw.polygon(
            self.points, fill=self.get_style("fill"), outline=self.get_style("stroke")
        )

    def vertex(self, x, y):
        self.points.append(self.p(x, y))

    def translate(self, x, y):
        self.matrix[-1].append(("translate", x, y))

    def rotate(self, angle):
        self.matrix[-1].append(("rotate", angle))