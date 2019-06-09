# coding: utf-8

from PIL import Image, ImageDraw, ImageColor

DEFAULT_PIXEL_SIZE = 5

COLOR_WHITE = ImageColor.getrgb('white')
COLOR_BLACK = ImageColor.getrgb('black')
COLOR_RED = ImageColor.getrgb('red')
COLOR_GREEN = ImageColor.getrgb('green')
COLOR_GRAY = ImageColor.getrgb('gray')
COLOR_BROWN = ImageColor.getrgb('brown')


class Point:
    x = None
    y = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'<{__class__.__name__} {self.x},{self.y}>'

    def pos(self):
        return self.x, self.y

    def mul(self, amount):
        x = self.x * amount
        y = self.y * amount
        return Point(x, y)

    def move(self, diff_x=0, diff_y=0):
        return Point(self.x + diff_x, self.y + diff_y)


class TTDTile:
    x = None
    y = None
    tile_type = None
    render_color = COLOR_BLACK

    def __init__(self, tile_type, x, y):
        self.x = int(x)
        self.y = int(y)
        self.tile_type = tile_type

    def __repr__(self):
        return f'<{__class__.__name__} [{self.x},{self.y}]>'

    def render(self, ttdmap, drawable):
        raise NotImplementedError


class TTDMap:
    size_x = None
    size_y = None
    pixel_size = 2
    background_color = COLOR_WHITE
    tiles = []

    def __init__(self, pixel_size=DEFAULT_PIXEL_SIZE):
        self.pixel_size = pixel_size

    def get_center_offset(self):
        # left part of sub-tile-pixel of real Y axe
        offset_x = self.pixel_size
        # distance between real axes of two tiles in neighborhood
        offset_x += (self.size_x - 1) * 2 * self.pixel_size

        offset_y = self.pixel_size

        return offset_x, offset_y

    def _load_tiles_from_file(self, fd):
        for line in fd.readlines():
            chunks = line.strip().split(';')
            tile_type = chunks[0]

            if tile_type == 'rail':
                tile = RailTile(*chunks)
            elif tile_type == 'station':
                tile = StationTile(*chunks)
            elif tile_type == 'tunnel':
                tile = TunnelTile(*chunks)
            elif tile_type == 'bridge':
                tile = BridgeTile(*chunks)

            yield tile

        fd.close()

    def load_from_file(self, filename):
        """Read content of file and create generator of tiles to create stupid
        lazy loading"""
        fd = open(filename)

        map_size = fd.readline().strip().split(';')
        self.size_x = int(map_size[0])
        self.size_y = int(map_size[1])

        self.tiles = self._load_tiles_from_file(fd)


    def render(self, filename='map.png'):
        width = (
            (self.size_x - 1)
            + (self.size_y - 1)
        ) * 2 * self.pixel_size + 2 * self.pixel_size

        img_dimension = width, width
        img = Image.new(size=img_dimension, mode='RGB',
                color=self.background_color)
        drawable = ImageDraw.Draw(img)

        for tile in self.tiles:
            tile.render(self, drawable)

        img.save(filename, 'PNG')


class RailTile(TTDTile):
    directions = set()

    def __init__(self, tile_type, x, y, directions):
        self.x = int(x)
        self.y = int(y)
        self.tile_type = tile_type
        self.directions = set(directions)

    def __repr__(self):
        directions = ''.join(self.directions)
        return f'<{__class__.__name__} [{self.x},{self.y}] = {directions}>'

    def render(self, ttdmap, drawable):
        ret = []

        if 'x' in self.directions:
            ret.append(
                (Point(-1, 1),
                 Point(1, -1)))
        if 'y' in self.directions:
            ret.append(
                (Point(-1, -1),
                 Point(1, 1)))
        if 'n' in self.directions:
            ret.append(
                (Point(-1, -1),
                 Point(1, -1)))
        if 's' in self.directions:
            ret.append(
                (Point(-1, 1),
                 Point(1, 1)))
        if 'w' in self.directions:
            ret.append(
                (Point(-1, -1),
                 Point(-1, 1)))
        if 'e' in self.directions:
            ret.append(
                (Point(1, -1),
                 Point(1, 1)))

        pixel_size = ttdmap.pixel_size

        for line in ret:
            point_from = line[0].mul(pixel_size)
            point_to = line[1].mul(pixel_size)

            diff_x = 2 * pixel_size * (self.y - self.x)
            diff_y = 2 * pixel_size * (self.y + self.x) - 4 * pixel_size

            # tile position offset
            point_from = point_from.move(diff_x, diff_y)
            point_to = point_to.move(diff_x, diff_y)

            # map centering offset
            point_from = point_from.move(*ttdmap.get_center_offset())
            point_to = point_to.move(*ttdmap.get_center_offset())

            # actual drawing
            points = (point_from.pos(), point_to.pos())
            drawable.line(points, fill=self.render_color, width=pixel_size)


class StationTile(TTDTile):
    direction = None
    render_color = COLOR_RED

    def __init__(self, tile_type, x, y, direction):
        self.x = int(x)
        self.y = int(y)
        self.tile_type = tile_type
        self.direction = direction

    def __repr__(self):
        return f'<{__class__.__name__} [{self.x},{self.y}] = {direction}>'

    def render(self, ttdmap, drawable):
        ret = []

        if 'x' in self.direction:
            ret.append(
                (Point(-1, 1),
                 Point(1, -1)))
        if 'y' in self.direction:
            ret.append(
                (Point(-1, -1),
                 Point(1, 1)))

        pixel_size = ttdmap.pixel_size

        for line in ret:
            point_from = line[0].mul(pixel_size)
            point_to = line[1].mul(pixel_size)

            diff_x = 2 * pixel_size * (self.y - self.x)
            diff_y = 2 * pixel_size * (self.y + self.x) - 4 * pixel_size

            # tile position offset
            point_from = point_from.move(diff_x, diff_y)
            point_to = point_to.move(diff_x, diff_y)

            # map centering offset
            point_from = point_from.move(*ttdmap.get_center_offset())
            point_to = point_to.move(*ttdmap.get_center_offset())

            # actual drawing
            points = (point_from.pos(), point_to.pos())
            drawable.line(points, fill=self.render_color, width=pixel_size)

class BridgeTile(StationTile):
    render_color = COLOR_BROWN

class TunnelTile(StationTile):
    render_color = COLOR_GRAY

