from pytui import StyledWindow, Text

# create an initial "screen" to sub-divide
# windows split from this inherit the same style
screen = StyledWindow(0, 0, 50, 25, {'fg': (0xa9b1d6), 'bg': (0x1a1b26)})

# horizontally split into header and footer with remainder for body
(header, body, footer) = screen.hsplit(3, None, 1)

# re-style header and footer
header.setStyle({'bg': (0xa9b1d6), 'fg': (0x1a1b26)})
footer.setStyle({'fg': (0x565f89), 'bg': (0x414868)})

# add some text
header.appendLine('')
header.appendLine('--- Header ---', 'center')
footer.appendLine('--- Footer ---', 'center')

body.appendLine('body')
body.appendLine(
    Text.style('styled inline text', {'fg': (0xf7768e), 'bg': (0x1a1b26)})
)

# draw all final windows
for window in (header, footer, body):
    window.draw()


print("\n")
