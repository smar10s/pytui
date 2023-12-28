from PIL import Image   # pip install pillow
from pytui import PixelCanvas


width = 64
height = 64

image = Image.effect_mandelbrot((width, height), (-0.7436, 0.1306, -0.7426, 0.1316), 100)
data = list(image.convert('RGB').getdata())

canvas = PixelCanvas(width, height)
canvas.set_data(data)

print(canvas.draw())
