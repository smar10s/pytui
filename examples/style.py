from pytui import Text

print(
    Text('coloured text').style({'fg': (0xf7768e), 'bg': (0x1a1b26)}),
    Text('bold text').style({'bold': True}),
    Text('faint text').style({'faint': True}),
    Text('italic text').style({'italic': True}),
    Text('underlined text').style({'underline': True}),
    Text('blinking text').style({'blink': True}),
    Text('negative text').style({'negative': True}),
    Text('crossed text').style({'crossed': True})
)
