from pytui import Window

# create a window at the top left, append lines with different justifications
window = Window(0, 0, 9, 3)
window.append_line('a')
window.append_line('b', 'center')
window.append_line('c', 'right')
window.draw()

print("\n")
