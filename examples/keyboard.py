import signal
import os
from time import sleep
from pytui import Keyboard, shutdown


def listener(c: str) -> None:
    if c == 'q':
        print('quiting')
        # exit() will just end the thread, kill whole process, interrupt sleep
        os.kill(os.getpid(), signal.SIGINT)
    else:
        print(f'{c} - press q to quit')


keyboard = Keyboard()

# ensure ctrl+c restores terminal state before messing with it
signal.signal(signal.SIGINT, lambda signal, frame: shutdown())

# attach our listener
keyboard.listen(listener)

# do something until 'q' interrupts
while True:
    sleep(1)

shutdown()
