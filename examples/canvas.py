from pytui import Canvas


def drawOctant(canvas: Canvas, cx: int, cy: int, x: int, y: int) -> None:
    canvas.set(cx+x, cy+y)
    canvas.set(cx-x, cy+y)
    canvas.set(cx+x, cy-y)
    canvas.set(cx-x, cy-y)
    canvas.set(cx+y, cy+x)
    canvas.set(cx-y, cy+x)
    canvas.set(cx+y, cy-x)
    canvas.set(cx-y, cy-x)


# bresenham's circle
def drawCircle(canvas: Canvas, cx: int, cy: int, r: int) -> None:
    x = 0
    y = r
    d = 3 - 2 * r

    drawOctant(canvas, cx, cy, x, y)

    while y >= x:
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6
        drawOctant(canvas, cx, cy, x, y)


# characters are taller than wide
canvas = Canvas(20, 10)

# draw circle at center
drawCircle(canvas, canvas.width // 2, canvas.height // 2, 10)

print(canvas.draw())
