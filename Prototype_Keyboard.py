# pip install pynput
from pynput import keyboard



Blocking_Mode = True

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

if (Blocking_Mode):
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
    print("exit")
else:
    while (True):
        # ...or, in a non-blocking fashion:
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        listener.start()
        print(".")