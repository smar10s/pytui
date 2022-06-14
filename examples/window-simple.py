from pytui import Window

# create a window at the top left, append lines with different justifications
window = Window(0, 0, 9, 3)
window.appendLine('a')
window.appendLine('b', 'center')
window.appendLine('c', 'right')
window.draw()

print("\n")
