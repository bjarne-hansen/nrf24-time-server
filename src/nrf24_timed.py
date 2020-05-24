import time
import signal
import pigpio
import struct
import sys
import traceback
import pathlib

from datetime import datetime
from systemd import daemon
from threading import Thread
from nrf24 import *
from configparser import ConfigParser


class NRF24TimeServer:

    def __init__(self, config_filename):        
        # Initialize NRF24TimeServer
        self.status('Initalising ...')
        self._running = False
        self._thread = Thread(target=self._run)
        self._config_filename = config_filename
        self._delay = 5

        # Configure signal handlers.
        signal.signal(signal.SIGTERM, self._term_handler)
        signal.signal(signal.SIGHUP, self._reload_handler)


    def start(self):
        self.status('Starting ...')

        # Create NRF24 from configuration.
        try:
            config = ConfigParser()
            config.read(self._config_filename)
            self._nrf, self._pi = NRF24.from_config(config)

            self._delay = config['nrf24_timed'].getint('delay', 5)

            # Start the thread publishing date/time.
            self._running = True
            self._thread.start()

        except Exception as ex:
            self.status('Error. Failed to start.')
            traceback.print_exc() 


    def stop(self):        
        self.status('Stopping ...')

        # Stop the pigpio connection.
        self._pi.stop()

        # Mark  the daemon as stopping.
        daemon.notify(daemon.Notification.STOPPING)
        self._running = False


    def reload(self):
        
        # Tell that we are reloading.
        self.status('Reloading ...')
        print(f'path={pathlib.Path.cwd()}')
        print(f'config={self._config_filename}')

        # Stop the current connection.
        self._pi.stop()

        try:
            # Load the configuration again.
            config = ConfigParser()
            config.read(self._config_filename)

            # Create new objects based on (changed) configuration.
            self._nrf, self._pi = NRF24.from_config(config)

       	    # Tell that we are ready ...
            self.status('Ready ...')
        except Exception as ex:
            status('Error. Failed to reload.')
            traceback.print_exc()


    def status(self, message, log=True):
        daemon.notify(daemon.Notification.STATUS, value=message)
        if log:
            print(message)


    def _reload_handler(self, signal, frame):
        self.reload()


    def _term_handler(self, signal, frame):
        self.stop()


    def _run(self):
        self.status("Ready ...")
        daemon.notify(daemon.Notification.READY)
        
        published = 0
        while self._running:
            if (time.monotonic() - published >= self._delay):
                self.status("Publishing ...", log=False)
                now = datetime.utcnow()
                print(datetime.isoformat(now, timespec='milliseconds'))
                payload = list(struct.pack("<B4sHBBBBBB", 0xfe, bytes('TIME', 'ascii'), now.year, now.month, now.day, now.hour, now.minute, now.second, now.isoweekday()))
                self._nrf.send(payload)
                self.status("Sleeping ...", log=False)
                published = time.monotonic()
            time.sleep(0.5)

        print("Stopped.")


if __name__ == '__main__':
    
    print('nrf24_timed, version 1.0')
    print('Copyright (C) 2020, conspicio.dk. All Rights Reserved')
    print()
    print(f'Current working directory: {pathlib.Path.cwd()}')

    if len(sys.argv) > 1:
        cfg_filename = sys.argv[1]
    else:
        cfg_filename = 'etc/nrf24_timed.ini'
    print(f'Configuration file: {cfg_filename}')
    
    timed = NRF24TimeServer(cfg_filename)
    timed.start()

