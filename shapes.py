## FRONT MATTER FOR DRAWING/SAVING IMAGES, ETC

from PIL import Image as PILImage

# some test colors
COLORS = {
    "red": (255, 0, 0),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "green": (0, 100, 0),
    "lime": (0, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "yellow": (255, 230, 0),
    "purple": (179, 0, 199),
    "pink": (255, 0, 255),
    "orange": (255, 77, 0),
    "brown": (66, 52, 0),
    "grey": (152, 152, 152),
}


def new_image(width, height, fill=(240, 240, 240)):
    return {
        "height": height,
        "width": width,
        "pixels": [fill for r in range(height) for c in range(width)],
    }


def flat_index(image, x, y):
    assert 0 <= x < image["width"] and 0 <= y < image["height"]
    return (image["height"] - 1 - y) * image["width"] + x


def get_pixel(image, x, y):
    return image["pixels"][flat_index(image, x, y)]


def set_pixel(image, x, y, c):
    assert (
        isinstance(c, tuple)
        and len(c) == 3
        and all((isinstance(i, int) and 0 <= i <= 255) for i in c)
    )
    if 0 <= x < image["width"] and 0 <= y < image["height"]:
        image["pixels"][flat_index(image, x, y)] = c


def save_color_image(image, filename, mode="PNG"):
    out = PILImage.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


## SHAPES!


class Shape:
    # All subclasses MUST implement the following:
    #
    # __contains__(self, p) returns True if point p is inside the shape
    # represented by self
    #
    # note that "(x, y) in s" for some instance of Shape
    # will be translated automatically to "s.__contains__((x, y))"
    #
    # s.center should give the (x,y) center point of the shape
    #
    # draw(self, image, color) should mutate the given image to draw the shape
    # represented by self on the given image in the given color
    #
    def __contains__(self, p):
        raise NotImplementedError("Subclass of Shape didn't define __contains__")

    def draw(self, image, color):
        for x in range(image['width']):
            for y in range(image['height']):
                if (x, y) in self: 
                    set_pixel(image, x, y, color)


class Circle(Shape):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
    
    def __contains__(self, p):
        assert isinstance(p, tuple) and len(p) == 2
        return sum((i-j)**2 for i, j in zip(self.center, p)) <= self.radius**2


class Rectangle(Shape):
    def __init__(self, lower_left, width, height):
        self.lower_left = lower_left
        self.width = width
        self.height = height

    @property
    def center(self):
        return (self.lower_left[0] + self.width//2, self.lower_left[1] + self.height//2)
    
    @center.setter
    def center(self, value):
        self.lower_left = (value[0] - self.width//2, value[1] - self.height//2)
    
    def __contains__(self, p):
        px, py = p
        llx, lly = self.lower_left
        return (
            llx <= px <= llx+self.width
            and lly <= py <= lly+self.height
        )
    
class Square(Rectangle):
    def __init__(self, lower_left, side_length):
        Rectangle.__init__(self, lower_left, side_length, side_length)


if __name__ == "__main__":
    out_image = new_image(500, 500)

    shapes = [
        (Circle((100, 100), 30), COLORS['purple']),
        (Rectangle((200, 300), 70, 20), COLORS['blue']),
        (Square((150, 400), 40), COLORS['green']),
    ]

    for shape, color in shapes:
        shape.draw(out_image, color)

    save_color_image(out_image, "test.png")
