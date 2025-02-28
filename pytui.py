from __future__ import annotations
from typing import Callable, Self
import sys
import math
import re
import os
import threading
import tty
import termios


# capture state at import time so multiple instances can reset to the same
termattrs = termios.tcgetattr(sys.stdin)


class Canvas:
    """A canvas where each "pixel" is a braille code.

    Computer graphics style origin at top left.

    Shamelessy based on https://github.com/asciimoo/drawille but faster.
    """

    BRAILLE_CODES = (
        (0x01, 0x08),
        (0x02, 0x10),
        (0x04, 0x20),
        (0x40, 0x80)
    )

    def __init__(self, cols: int, rows: int) -> None:
        """Creates new canvas.

        Args:
            cols: Canvas width in characters (2x as many points).
            rows: Canvas height in characters (4x as many points).
        """
        self.cols = cols        # size in characters
        self.rows = rows
        self.width = cols * 2   # size in braille points
        self.height = rows * 4
        self.codes = [0]*(cols*rows)

    def set(self, x: int, y: int) -> None:
        """Sets a braille point.

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        (col, row) = (x//2, y//4)
        if row >= 0 and col >= 0 and row < self.rows and col < self.cols:
            self.codes[row*self.cols + col] |= self.BRAILLE_CODES[y % 4][x % 2]

    def line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draws a line between two braille points.

        Args:
            x1: Start X coordinate.
            y1: Start Y coordinate.
            x2: End X coordinate.
            y2: End Y coordinate.
        """
        xd = x2 - x1
        yd = y2 - y1
        steps = int(max(abs(xd), abs(yd)))
        for i in range(0, steps):
            x = round(x1 + (xd / steps * i))
            y = round(y1 + (yd / steps * i))
            self.set(x, y)

    def draw_row(self, row: int) -> str:
        i = row * self.cols
        chars = [chr(0x2800 + self.codes[i + x]) for x in range(self.cols)]
        return ''.join(chars)

    def draw(self) -> str:
        """Returns the canvas as text."""
        return "\n".join([self.draw_row(row) for row in range(self.rows)])


class Plot:
    """A cartesian plane with origin at bottom left.

    Coordinate range is independent from display dimensions.
    """

    def __init__(
        self,
        cols: int,
        rows: int,
        minx: float,
        miny: float,
        maxx: float,
        maxy: float
    ) -> None:
        """Creates a new plot for a given display size and coordinate range.

        Args:
            cols: Plot width in characters.
            rows: Plot heigh in characters.
            minx: Starting X value.
            miny: Starting Y value.
            maxx: Ending X value.
            maxy: Ending Y value.
        """
        self.canvas = Canvas(cols, rows)
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def translate(self, v: float, a: float, b: float, s: float) -> int:
        return round((v - a) / (b - a) * s)

    def translatexy(self, x: float, y: float) -> tuple[int, int]:
        # flip y to match common plots
        cx = self.translate(x, self.minx, self.maxx, self.canvas.width - 1)
        cy = self.translate(y, self.maxy, self.miny, self.canvas.height - 1)
        return (cx, cy)

    def point(self, x: float, y: float) -> None:
        """Draws a point.

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        self.canvas.set(*self.translatexy(x, y))

    def line(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """Draws a line between two coordinate points.

        Args:
            x1: Start X coordinate.
            y1: Start Y coordinate.
            x2: End X coordinate.
            y2: End Y coordinate.
        """
        self.canvas.line(*self.translatexy(x1, y1), *self.translatexy(x2, y2))

    def draw(self) -> str:
        """Returns plot as text."""
        return self.canvas.draw()


class PixelCanvas:
    """A canvas where each "pixel" is a unicode half block element.

    Computer graphics style origin at top left.
    """

    def __init__(
        self,
        width: int,
        height: int,
        background: tuple[int, int, int] = (0, 0, 0)
    ) -> None:
        """Creates new canvas.

        Args:
            width: Canvas width in "pixels" (characters).
            height: Canvas height in "pixels" (characters*2).
            background: The default pixel color as (R,G,B) tuple.
        """
        self.width = width
        self.height = height
        self.data = [background]*(width*height)

    def set_data(self, data: list[tuple[int, int, int]]) -> None:
        """Sets the entire canvas from a width*height wide list."""
        self.data = data

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        """Sets a pixel.

        Args:
            x: X coordinate.
            y: Y coordinate.
            color: Pixel color as (R,G,B) tuple.
        """
        self.data[(y * self.width) + x] = color

    def draw(self) -> str:
        """Returns the canvas as text."""
        lines = []
        for y in range(self.height):
            if 0 == y % 2:
                line = ''
                for x in range(self.width):
                    top = self.data[(y * self.width) + x]
                    bottom = self.data[((y+1) * self.width) + x]
                    line += Text('▀').style({'fg': top, 'bg': bottom})
                lines.append(line)
        return "\n".join(lines)


class Terminal:
    """Utility methods for terminal interaction."""

    def flush(self) -> None:
        """Flushes output."""
        sys.stdout.flush()

    def write(self, string: str) -> None:
        """Writes string to output buffer."""
        sys.stdout.write(string)

    def clear(self) -> None:
        """Clears the terminal."""
        self.write("\x1b[2J")

    def set_cursor(self, x: int, y: int) -> None:
        """Sets the cursor position for next write.

        Args:
            x: Cursor column.
            y: Cursor row.
        """
        self.write("\x1b[%d;%dH" % (y + 1, x + 1))

    def hide_cursor(self) -> None:
        """Hides cursor."""
        self.write("\x1b[?25l")

    def show_cursor(self) -> None:
        """Shows cursor."""
        self.write("\x1b[?25h")

    def reset_colors(self) -> None:
        """Resets background and foreground colors."""
        self.write("\x1b[0m")

    def fullscreen(self) -> None:
        """Clears the screen, hides the cursor and moves it to the top left."""
        self.clear()
        self.hide_cursor()
        self.set_cursor(0, 0)

    def reset(self) -> None:
        """Resets colors and shows the cursor."""
        self.reset_colors()
        self.show_cursor()

    def get_size(self) -> os.terminal_size:
        return os.get_terminal_size()

    def get_columns(self) -> int:
        """Returns current terminal width."""
        return self.get_size().columns

    def get_lines(self) -> int:
        """Returns current terminal height."""
        return self.get_size().lines


class Window:
    """A rectangle of text positioned somewhere on the screen.

    Content can be set directly or appended or prepended, scrolling up or
    down respectively.

    Windows can also be vertically or horizontally partitioned into new ones
    for more complex layouts.
    """

    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        """Creates a new window.

        Args:
            x: Starting row.
            y: Starting line.
            w: Width.
            h: Height.
        """
        self.terminal = Terminal()
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.buffer: list[str] = []

    def create(self, x, y, w, h) -> Self:
        return type(self)(x, y, w, h)

    def clear(self) -> None:
        """Clears the content of this window."""
        self.buffer = []

    def justify_line(self, line: str, justify: str = 'left') -> str:
        length = len(Text(line).strip_ansi())
        if length > self.width:
            raise Exception(f'line ({length}) too wide, max ({self.width})')

        width = self.width + (len(line) - length)  # make up for ansi codes
        if 'left' == justify:
            return line.ljust(width)
        elif 'right' == justify:
            return line.rjust(width)
        else:
            return line.center(width)

    def append_line(self, line: str, justify: str = 'left') -> None:
        """Appends a line, scrolling if necessary.

        Args:
            line: Line to append.
            justify: Justification, either left, right or center. Default left.

        Raises:
            Exception if the line is wider than the window.
        """
        if len(self.buffer) >= self.height:     # scroll up
            self.buffer = self.buffer[1:]
        self.buffer.append(self.justify_line(line, justify))

    def append_text(self, text: str, justify: str = 'left') -> None:
        """Appends any text string, scrolling and wrapping as necessary.

        Args:
            text: Text to append. Wraps if wider than window. May be styled.
            justify: Justification, either left, right or center. Default left.

        """
        for line in Text(text).wrap(self.width):
            self.append_line(line, justify)

    def prepend_line(self, line: str, justify: str = 'left') -> None:
        """Prepends a line, scrolling if necessary.

        Args:
            line: Line to prepend.
            justify: Justification, either left, right or center. Default left.

        Raises:
            Exception if the line is wider than the window.
        """
        if len(self.buffer) >= self.height:     # scroll down
            self.buffer = self.buffer[:-1]
        self.buffer.insert(0, self.justify_line(line, justify))

    def prepend_text(self, text: str, justify: str = 'left') -> None:
        """Prepends any text string, scrolling and wrapping as necessary.

        Args:
            text: Text to prepend. Wraps if wider than window. May be styled.
            justify: Justification, either left, right or center. Default left.

        """
        for line in Text(text).wrap(self.width):
            self.prepend_line(line, justify)

    def draw_line(self, line: str) -> None:
        self.terminal.write(line)

    def draw(self) -> None:
        """Writes current buffer to terminal (but does not flush.)"""
        for i in range(self.height):
            self.terminal.set_cursor(self.x, self.y + i)
            have = i < len(self.buffer)
            self.draw_line(self.buffer[i] if have else ''.ljust(self.width))

    def update_buffer(self, buffer: list[str]) -> None:
        """Updates current buffer.

        Buffer must be of the correct dimensions.
        """
        self.buffer = buffer

    def update_content(self, content: str) -> None:
        """Updates buffer from multiline string."""
        self.update_buffer(list(map(self.justify_line, content.splitlines())))

    def splitrange(self, total: int, *args) -> list[int]:
        available = total
        values = []

        for i in args:
            if isinstance(i, float):
                i = int(total * i)

            if isinstance(i, int):
                if available - i < 0:
                    raise Exception('not enough room to split')
                values.append(i)
                available -= i
            elif i is None:
                values.append(-1)
            else:
                raise Exception(f'invalid split point type {type(i)}')

        if available == 0 and values.count(-1) == 0:
            return values

        if -1 not in values:
            values.append(-1)

        blanks = values.count(-1)

        if available < blanks:
            raise Exception('not enough room to split')

        # overflow into the last available spot
        last_blank = max(i for i, w in enumerate(values) if w == -1)
        values[last_blank] = math.ceil(available/blanks)

        # fill the remaining
        return [available//blanks if x == -1 else x for x in values]

    def hsplit(self, *args) -> list[Self]:
        """Horizontally splits this window into two or more new windows.

        Args:
            *args: One or more ints, floats or None. Ints are interpreted as
                number of characters, floats as percentage, None as the
                equally distributed remainder, if any. None is implied as the
                last argument if not explicitly included otherwise (i.e. any
                unaccounted for remainder is returned with a last window.)
                Examples:
                (0.2)        Returns windows sized (20%, 80%).
                (0.2, None)  Equivalent to above.
                (0.2, 0.8)   Equivalent to above.
                (10)         Returns windows sized (10, any remainder)
                (1, None, 1) Returns windows sized (1, any remainder, 1)
                (1, None, None, 1) Like above, but with remainder distributed
                    between two windows: (1, remainder, remainder, 1)
                (1, 0.2)     Returns windows sized (1, 20% of original, any
                    remainder)
        """
        windows = []
        y = self.y
        for height in self.splitrange(self.height, *args):
            windows.append(self.create(self.x, y, self.width, height))
            y += height
        return windows

    def vsplit(self, *args) -> list[Self]:
        """Vertically splits this window into two or more new windows.

        Args:
            *args: One or more ints, floats or None. Ints are interpreted as
                number of characters, floats as percentage, None as the
                equally distributed remainder, if any. None is implied as the
                last argument if not explicitly included otherwise (i.e. any
                unaccounted for remainder is returned with a last window.)
                Examples:
                (0.2)        Returns windows sized (20%, 80%).
                (0.2, None)  Equivalent to above.
                (0.2, 0.8)   Equivalent to above.
                (10)         Returns windows sized (10, any remainder)
                (1, None, 1) Returns windows sized (1, any remainder, 1)
                (1, None, None, 1) Like above, but with remainder distributed
                    between two windows: (1, remainder, remainder, 1)
                (1, 0.2)     Returns windows sized (1, 20% of original, any
                    remainder)
        """
        windows = []
        x = self.x
        for width in self.splitrange(self.width, *args):
            windows.append(self.create(x, self.y, width, self.height))
            x += width
        return windows


class StyledWindow(Window):
    """A window with ANSI style applied to content."""

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        style: dict = {}
    ) -> None:
        """Creates a new styled window.

        Args:
            x:      Starting row.
            y:      Starting line.
            w:      Width.
            h:      Height.
            style:  A dictionary of style options. See Text.style for details.
        """
        super().__init__(x, y, w, h)
        self.style = style

    def create(self, x, y, w, h) -> StyledWindow:
        return type(self)(x, y, w, h, self.style)

    def update_style(self, style: dict) -> None:
        self.style = style

    def draw_line(self, line: str) -> None:
        ansi_style = Text('').style(self.style, '')
        line = ansi_style + line.replace("\x1b[0m", "\x1b[0m" + ansi_style)
        self.terminal.write(line)
        self.terminal.reset_colors()


class Text:
    """Utility class for dealing with ANSI text."""

    def __init__(self, string: str) -> None:
        """Creates a new text instance.

        Args:
            string: A string.
        """
        self.string = string

    def strip_ansi(self) -> str:
        """Strips any ANSI codes from the input string."""
        pattern = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return pattern.sub('', self.string)

    def split_rgb(self, c: int) -> tuple[int, int, int]:
        return ((c >> 16) & 0x0000ff, (c >> 8) & 0x0000ff, c & 0x0000ff)

    def rgb(self, c) -> tuple[int, int, int]:
        if type(c) is int:
            return self.split_rgb(c)
        return c

    def style(self, options: dict, terminator: str = "\x1b[0m") -> str:
        """Applies an ANSI style to the string.

        Args:
            options:    A dictionary of style options. Available:
                fg and bg
                    foreground and background color, as RGB int (0x102030)
                    or separate values in a tuple ((0x10, 0x20, 0x30))
                bold
                faint
                italic
                underline
                blink
                negative
                crossed
            terminator: A style terminator. Defaults to ANSI color reset.

        Returns:
            String with ANSI codes.
        """
        string = self.string
        codes = []
        if 'fg' in options:
            codes.append("\x1b[38;2;%d;%d;%dm" % self.rgb(options['fg']))
        if 'bg' in options:
            codes.append("\x1b[48;2;%d;%d;%dm" % self.rgb(options['bg']))
        if 'bold' in options and options['bold']:
            codes.append("\033[1m")
        if 'faint' in options and options['faint']:
            codes.append("\033[2m")
        if 'italic' in options and options['italic']:
            codes.append("\033[3m")
        if 'underline' in options and options['underline']:
            codes.append("\033[4m")
        if 'blink' in options and options['blink']:
            codes.append("\033[5m")
        if 'negative' in options and options['negative']:
            codes.append("\033[7m")
        if 'crossed' in options and options['crossed']:
            codes.append("\033[9m")
        return ''.join(codes) + string + terminator if codes else string

    def wrap(self, width: int) -> list[str]:
        """Wraps a string by breaking it into 'width' character wide lines.

        The string may include ANSI style codes as applied by style().
        YMMV with other codes or ANSI strings.

        Args:
            width: The size at which to wrap the string and create a new line.

        Returns:
            A list of strings, each being at most 'width' characters long.
        """
        string = self.string
        terminator = '\x1b[0m'
        lines = []  # list of 'width' wide lines
        line = ''   # current line
        style = ''  # current style
        i = 0       # current index
        length = 0  # current line length

        def add_line() -> None:
            lines.append(line + (terminator if line[-4:] != terminator else ''))

        while i < len(string):
            if string[i:i+len(terminator)] == terminator:   # clear style
                style = ''
                line += terminator
                i += len(terminator)
            elif string[i] in ('\033', '\x1b'):             # add style
                k = string[i:].find('m')
                code = string[i:i+k+1]
                style += code
                line += code
                i += len(code)
            elif string[i] == '\n':                         # break at newline
                add_line()
                line = style
                length = 0
                i += 1
            else:                                           # add character
                line += string[i]
                i += 1
                length += 1
                if length >= width:                         # break line
                    add_line()
                    line = style
                    length = 0
                    if string[i] == '\n':                   # swallow next if newline
                        i += 1
        if length:
            add_line()                                      # add any remainder
        return lines


class Keyboard:
    """A non-blocking key dispatcher.

    Uses Python threading and some terminal shenanigans to simulate something
    like an event based keyboard listener.

    Limitations are many but include inability to read modifier keys like
    ctrl/alt. Shift can be read as uppercase/row.
    """
    UP = 'up'
    DOWN = 'down'
    RIGHT = 'right'
    LEFT = 'left'
    UNKNOWN = 'unknown'
    BACKSPACE = '\x7f'
    ENTER = '\x0a'
    TAB = '\x09'

    def __init__(self) -> None:
        """Creates a new keyboard instance that listeners can be attached to.
        """
        self.thread = None
        self.listeners: list[Callable[[str], None]] = []

    def disable_line_buffering(self) -> None:
        tty.setcbreak(sys.stdin)

    def reset(self) -> None:
        """Resets stdin to the state captured at module load time."""
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termattrs)

    def read_ansi(self) -> str:
        # already read '\x1b', read '[' and interpret next
        sys.stdin.read(1)
        c = sys.stdin.read(1)
        if '\x41' == c:
            return self.UP
        elif '\x42' == c:
            return self.DOWN
        elif '\x43' == c:
            return self.RIGHT
        elif '\x44' == c:
            return self.LEFT
        else:
            return self.UNKNOWN

    def read(self) -> None:
        while True:
            c = sys.stdin.read(1)
            if '\x1b' == c:
                c = self.read_ansi()
            for fn in self.listeners:
                fn(c)

    def add_listener(self, fn: Callable[[str], None]) -> None:
        """Adds a new keyboard listener to be invoked when a key has been
        pressed.

        Args:
            fn: A callback function that accepts a character or magic string
                (arrow keys.)
        """
        self.listeners.append(fn)

    def listen(self, fn: Callable[[str], None] | None = None) -> None:
        """Starts listening for keyboard input in a separate thread,
        optionally registering a callback first.

        Args:
            fn: An optional callback function. See add_listener.
        """
        if fn:
            self.add_listener(fn)
        if not self.thread:
            self.disable_line_buffering()
            threading.Thread(target=self.read, daemon=True).start()


def shutdown():
    """A shutdown function that restores terminal state and exits."""
    Terminal().reset()
    Keyboard().reset()
    sys.exit(0)
