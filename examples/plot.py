from pytui import Plot
from math import pi, sin

# create a plot from 0,-1 to 2*pi,1 to capture one full sine wave
plot = Plot(40, 10, 0, -1, 2*pi, 1)

# draw X-axis
plot.line(0, 0, 2*pi, 0)

# draw sine wave
x = 0.0
step = 0.1
while x < 2*pi:
    plot.point(x, sin(x))
    x += step

print(plot.draw())
