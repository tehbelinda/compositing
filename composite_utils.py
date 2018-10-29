#!/usr/bin/env python

from PIL import Image
from PIL import ImageChops
from PIL import ImageDraw
from PIL import ImageFont


FONT_COLOR = (255, 255, 255)
FONT_BACKGROUND_COLOR = (0, 0, 0)
FONT_FILE = "BebasNeue.otf"
FONT_ENCODING = "utf8"
FONT_SIZE = 48
FONT_LINE_HEIGHT = 33
INITIAL_LINE_HEIGHT_OFFSET = -(FONT_SIZE - FONT_LINE_HEIGHT) * 2 / 3


def get_text_width(text):
    """Get Text Width.

    :param text: String of text.
    :return: Pixel width of text.
    """

    font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
    return font.getsize(text)[0]

def draw_text(draw, point, text):
    """Draw Text.

    :param draw: ImageDraw object.
    :param point: Tuple of (x, y) top left location of where to draw the text.
    :param text: The text to draw.
    """

    text = text.decode(FONT_ENCODING)
    font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
    draw.text(point, text, font=font, fill=FONT_COLOR)

def split_text_into_lines(size, text):
    """Split Text Into Lines.

    :param size: Tuple of (width, height).
    :param text: String of text.
    :return: Array of strings of text.
    """

    lines = []
    line = []
    words = text.split()
    cur_height = 0
    while cur_height < size[1]:
        for word in words:
            new_line = " ".join(line + [word])
            # Add word if it still fits within the row.
            if get_text_width(new_line) <= size[0]:
                line.append(word)
            # Otherwise finish the line and check if we can start a new row of words.
            else:
                lines.append(line)
                cur_height += FONT_LINE_HEIGHT
                if cur_height >= size[1]:
                    break
                line = [word]
    # Add final line if there is one.
    if line:
        lines.append(line)
    lines = [" ".join(line) for line in lines if line]
    return lines

def draw_text_lines(draw, size, lines):
    """Draw Text Lines.

    :param draw: ImageDraw object.
    :param size: Tuple of (x, y) of size of overall image.
    :param lines: Array of strings of text to draw on to the image.
    """

    cur_y = INITIAL_LINE_HEIGHT_OFFSET
    for line in lines:
        words = line.split()
        line_without_spaces = "".join(words)
        line_without_spaces_width = get_text_width(line_without_spaces)
        # To justify the words we need to calculate the width of each space, which is the remaining
        # width divided by the number of spaces.
        space_width = (size[0] - line_without_spaces_width) / (len(words) - 1.0)

        # Draw in each word followed by the space.
        cur_x = 0
        for word in words[:-1]:
            draw_text(draw, (cur_x, cur_y), word)
            word_width = get_text_width(word)
            cur_x += word_width + space_width

        # Draw in final word.
        last_word_width = get_text_width(words[-1])
        last_word_x = size[0] - last_word_width
        draw_text(draw, (last_word_x, cur_y), words[-1])

        cur_y += FONT_LINE_HEIGHT

def composite(image, text):
    """Composite.

    :param image: Image filename or file pointer.
    :param text: String of text.
    :return: Final image.
    """

    base = Image.open(image)

    # Create text as image.
    lines = split_text_into_lines(base.size, text)
    text_img = Image.new("RGB", base.size, color=FONT_BACKGROUND_COLOR)
    text_draw = ImageDraw.Draw(text_img)
    draw_text_lines(text_draw, base.size, lines)

    # Composite text image on base image.
    return ImageChops.multiply(base, text_img)
