from pytui import Window, Plot
from random import randrange

# create an initial "screen" to sub-divide
screen = Window(0, 0, 50, 25)

# horizontally split into 1 line tall header and footer with remainder for body
(header, body, footer) = screen.hsplit(1, None, 1)
# vertically split body into 20% left and 80% right
(left, right) = body.vsplit(0.2)

# add some header/footer text
header.appendLine('--- Header ---', 'center')
footer.appendLine('--- Footer ---', 'center')

# create a random plot, show points left and plot right
plot = Plot(body.width, body.height, 0, 0, 100, 100)
(px, py) = (0, 0)
for x in range(100):
    y = randrange(int(plot.miny), int(plot.maxy))
    plot.line(px, py, x, y)
    (px, py) = (x, y)
    left.appendLine(f'{x}, {y}')

right.setContent(plot.draw())

# draw all final windows
for window in (header, footer, left, right):
    window.draw()

print("\n")
