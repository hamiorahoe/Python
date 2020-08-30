import json
from pynput import mouse, keyboard
from time import time
import os


OUTPUT_FILENAME = 'btn_positions'

#declare mouse listener globally so that keyboard on release can stop it
mouse_listener = None
#declare start time globally so calback functions can reference it 
start_time = None
#Keep track of unreleased keys to prevent over-reporting press events
unreleased_keys = []

class EventType():
    KEYDOWN = 'keyDown'
    KEYUP = 'keyUp'
    CLICK = 'click'

class recorder():
    #store all input events
    input_events = []
    #set target globally
    _target = None
    def write(self):
        print(json.dumps(self.input_events))

        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(
            script_dir,
            '..', 
            'Recordings', 
            '{}.json'.format(OUTPUT_FILENAME)
        )
        with open(filepath, 'r') as openFile:
            data = json.load(openFile)
            print('********Data: {}***********'.format(data))
            for index, item in enumerate(data):
                try:
                    if not (item['btn'] == self._target):
                        self.input_events.append(item)
                except TypeError:
                    print("error")
        openFile.close()

        with open(filepath, 'w') as jsonFile:
            print(filepath)
            json.dump(self.input_events, jsonFile, indent=4)
        jsonFile.close()
        if(not jsonFile.closed):
            print('not closed')




    def elapsed_time(self):
        global start_time
        return time() - start_time

    def record_event(self, event_type, event_time, button, pos=None):
        self.input_events = []
        self.input_events.append({
            'btn' : self._target,
            'info' : {
            'time' : event_time,
            'type' : event_type,
            'button' : str(button),
            'pos' : pos
        }})
        if event_type == EventType.CLICK:
            print('{0} on {1} pos {2} at {3}'.format(event_type, button, pos, event_time))
        else:
            print('{0} on {1} at {2}'.format(event_type, button, event_time))
    """ 
    def on_press(key):
        #only record first key press event until that key has been released
        global unreleased_keys
        if key in unreleased_keys:
            return
        else:
            unreleased_keys.append(key) 

        try:
            record_event(EventType.KEYDOWN, elapsed_time(), key.char)
        except AttributeError:
            record_event(EventType.KEYDOWN, elapsed_time(), key)

    def on_release(key):
        #mark key as no longer pressed
        global unreleased_keys
        try:
            unreleased_keys.remove(key)
        except ValueError:
            print('ERROR {0} not in unreleased_keys'.format(key))


        try:
            record_event(EventType.KEYUP, elapsed_time(), key.char)
        except AttributeError:
            record_event(EventType.KEYUP, elapsed_time(), key)

        if key == keyboard.Key.esc:
            #stop mouse listener
            global mouse_listener
            mouse_listener.stop()
            #stop listener
            raise keyboard.Listener.StopException """

    def on_click(self, x,y,button,pressed):
        if not pressed:
            self.record_event(EventType.CLICK, self.elapsed_time(), button, {"x" : x, "y" : y})
            mouse_listener.stop()

        
    def runListeners(self, target):

        self._target = target
        #Collect mouse input events
        global mouse_listener
        mouse_listener = mouse.Listener(on_click=self.on_click)
        mouse_listener.start()
        mouse_listener.wait()
        global start_time
        start_time = time()
        mouse_listener.join()
    """ 
        with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
            listener.join() """

