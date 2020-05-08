import time
import signal
from datetime import datetime
from systemd import daemon
from threading import Thread

_run = True

class NRF24TimeServer:

    def __init__(self):
        self.status("Initalising ...")
        self._running = False
        self._thread = Thread(target=self._run)
        self._delay = 5.0

        signal.signal(signal.SIGTERM, self._term_handler)
        signal.signal(signal.SIGHUP, self._reload_handler)
    
    def start(self):
        self.status("Starting ...")        
        self._running = True
        self._thread.start()

    def stop(self):
        self.status("Stopping ...")
        daemon.notify(daemon.Notification.STOPPING)
        self._running = False
        

    def reload(self):
        self.status("Reloading ...")
        # TODO: Reload configuration
        self.status("Ready ...")

    def status(self, message, log=True):
        daemon.notify(daemon.Notification.STATUS, value=message)
        if log:
            print(message)
        
    def _reload_handler(self, signal, frame):
        self.reload()        

    def _term_handler(self, signal, frame):
        self.stop()

    def _run(self):

        daemon.notify(daemon.Notification.READY)
        self.status("Ready ...")
        published = 0
        while self._running:
            if (time.monotonic() - published >= self._delay):
                self.status("Publishing ...", log=False)
                now = datetime.now()
                print(datetime.isoformat(datetime.now(),timespec='milliseconds'))
                self.status("Sleeping ...", log=False)
                published = time.monotonic()
            time.sleep(0.5)

        print("Stopped.")



if __name__ == '__main__':
    timed = NRF24TimeServer()
    timed.start()
