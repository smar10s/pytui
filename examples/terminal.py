from pytui import Terminal, Plot
from math import pi, sin

terminal = Terminal()
terminal.fullscreen()

plot = Plot(terminal.getColumns(), terminal.getLines()-1, 0, -1, 2*pi, 1)

# draw X-axis
plot.line(0, 0, 2*pi, 0)

# draw sine wave
x = 0.0
step = 0.01
while x < 2*pi:
    plot.point(x, sin(x))
    x += step

print(plot.draw())

terminal.reset()
