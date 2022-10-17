import signal
import os
from time import sleep
from pytui import Window, Keyboard, InputPrompt, shutdown


# ensure ctrl+c restores terminal state before messing with it
signal.signal(signal.SIGINT, lambda signal, frame: shutdown())


# handler quits on 'quit', ignores all other input
def on_enter(buffer: str, tokens: list[str]) -> None:
    if buffer == 'quit':
        os.kill(os.getpid(), signal.SIGINT)


# create new input prompt using 10x10 window that will scroll if necessary
prompt = InputPrompt(Window(0, 0, 10, 10), Keyboard(), on_enter)
prompt.listen()


# spin until quit
while True:
    sleep(1)
