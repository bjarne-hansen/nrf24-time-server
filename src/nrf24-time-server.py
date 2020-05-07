#!/usr/bin/env python
import struct
from NRF24 import NRF24
import pigpio
import time
from datetime import datetime
from dateutil import tz
import signal
import os
import sys
import daemon
import argparse
import psutil
import fcntl


class TimePublisher:

    def __init__(self, hostname=None, delay=5,
                 ce_pin=25,
                 channel=1,
                 crc_bytes=2,
                 local_address="DTP01",
                 remote_address="DTCLN"):

        # pigpio object for accessing the pigpiod daemon.
        # See http://abyz.me.uk/rpi/pigpio/index.html
        self.pi = None

        # NRF24 object for NRF24L01 comminication using the pigpiod daemon.
        self.nrf = None

        # Always publish date/time information in UTC.
        self.timezone = tz.gettz("UTC")

        # Hostname of the raspberry pi running the pigpiod daemon.
        # Default is None meaning local host.
        self.hostname = hostname

        # Delay between publishing date/time information. Default is 5 seconds.
        self.delay = delay

        # CE pin of the NRF24L01 module. Default is 25. See wiring information in the README.md file.
        self.ce = ce_pin

        # RF24 channel. Default 1 (2400 Mhz)
        self.channel = channel

        # Number of bytes for cyclic redundancy check. Default 2
        self.crc_bytes = crc_bytes

        # Local address of the date/time publisher. Default "DTP01".
        # The local address can be changed, if you have more date/time publishing servers.
        self.local_address = local_address

        # The address of the receiving client. Default "DTCLN".
        # Ideally this should not be changed. If you need to change this, make sure to change all the clients
        # subscribing to date/time information as well.
        self.remote_address = remote_address

        # Payload size. Must correspond to the payload size being sent.
        # Not configurable. See the start() method below.
        self.payload_size = 10

    def reload(self, sig, frame):
        print("Reloading nrf24-timed configuration ...")

    def stop(self, sig, frame):
        print("\nStopping nrf24-timed ...")
        self.pi.spi_close(self.nrf.get_spi_handle())
        self.pi.stop()
        print("Stopped.")
        sys.exit(0)

    def hello(self, sig, frame):
        print("Hello from nrf24-timed ...")

    def init(self):

        if self.hostname is None:
            self.pi = pigpio.pi()
        else:
            self.pi = pigpio.pi(self.hostname)

        self.nrf = NRF24(self.pi, ce=self.ce)
        self.nrf.set_channel(self.channel)                   # Default: 76
        self.nrf.set_data_rate(NRF24.RF24_250KBPS)           # Default: RF24_1MBPS
        self.nrf.set_payload_size(self.payload_size)         # Default: 32 (max)
        self.nrf.set_crc_bytes(self.crc_bytes)               # Default: 2

        self.nrf.set_local_address(self.local_address)       # RX P1
        self.nrf.set_remote_address(self.remote_address)	 # TX, RX P0

        print("\nCONFIGURATION:")
        print("--------------")
        print(f"  Hostname: {self.hostname}")
        print(f"  Delay   : {self.delay}")
        print(f"  CE GPIO : {self.ce}")
        print(f"  Channel : {self.channel}")
        print(f"  Payload : {self.payload_size}")
        print(f"  CRC     : {self.crc_bytes}")
        print(f"  RX addr : {self.local_address}")
        print(f"  TX addr : {self.remote_address}")
        print("--------------")

        self.nrf.show_registers()

    def start(self):
        print("nrf24-timed daemon, Copyright 2019, Bjarne Hansen, All Rights Reserved.")
        print("Start nrf24-timed ...")

        # Initialize the date/time publishing daemon.
        self.init()

        while True:
            # Get current timestamp
            now = datetime.now(self.timezone)

            # Create NRF24L01 payload with identification and year, month, day, hours, minutes, seconds
            # Big-endian: "tim" (3), short (2), byte (1), byte (1), byte (1), byte (1), byte (1), 10 bytes in total.
            payload = struct.pack(">3shbbbbb", b"tim", now.year, now.month, now.day, now.hour, now.minute, now.second)
            self.nrf.send(payload)
            print(now, payload)
            time.sleep(self.delay)


def run_time_publisher(detach, hostname, delay):

    publisher = TimePublisher(hostname, delay)

    context = daemon.DaemonContext()
    context.signal_map = {signal.SIGTERM: publisher.stop,
                          signal.SIGINT: publisher.stop,
                          signal.SIGHUP: publisher.reload,
                          signal.SIGUSR1: publisher.hello}

    context.umask = 0o022

    context.pidfile = PIDFile("/var/run/nrf24-timed.pid")

    if not os.path.exists('/var/opt/nrf24-timed'):
        os.makedirs('/var/opt/nrf24-timed')

    if detach:
        context.detach_process = True
        context.working_directory = '/var/opt/nrf24-timed'
        context.stdout = open('/var/log/nrf24-timed.out', 'a')
        context.stderr = open('/var/log/nrf24-timed.err', 'a')
    else:
        context.detach_process = False
        context.working_directory = os.getcwd()
        context.stdin = sys.stdin
        context.stdout = sys.stdout
        context.stderr = sys.stderr

    try:
        with context:
            publisher.start()
    except (Exception) as ex:
        print(f"Exception during execution of daemon: {ex} ", file=sys.stderr)
        sys.exit(1)


class PIDFileException(Exception):
    pass


class PIDFile:
    def __init__(self, path, timeout=5):
        self.path = path
        self.timeout = timeout
        self.pid_file = None

    def __enter__(self):
        self._acquire()

    def __exit__(self, *_exc):
        self._release()

    def _acquire(self):

        with open(self.path, "a+") as self.pid_file:

            # Try to obtain exclusive lock on PID file.
            has_lock = False
            start = time.time()
            while (time.time() - start) < self.timeout:
                try:
                    fcntl.flock(self.pid_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    has_lock = True
                    break
                except:
                    has_lock = False

            if not has_lock:
                raise PIDFileException(f"Failed to obtain exclusive lock on {self.path} in {self.timeout} seconds.")

            # Read first line of PID file to get PID of running daemon, if any.
            self.pid_file.seek(0)
            line = self.pid_file.readline().strip()

            # Parse the PID in the PID file.
            try:
                pid = int(line)
            except:
                pid = -1

            # Check if the PID in the PID file corresponds to a running process.
            if pid != -1:
                for p in psutil.process_iter():
                    # Get the PID of the next process in list of running processes.
                    try:
                        ppid = p.pid
                    except:
                        ppid = -1

                    if ppid == pid:
                        raise PIDFileException(f"Daemon with PID {pid} is already running.")

            # Update PID file with PID of this process.
            pid = os.getpid()
            self.pid_file.truncate()
            self.pid_file.write(f"{pid}\n")
            self.pid_file.flush()

    def _release(self):

        #try:
        #    fcntl.flock(self.pid_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        #except Exception as ex:
        #    print(f"Exception while unlocking PID file {self.path}: {ex}", file=sys.stderr)

        try:
            os.remove(self.path)
        except Exception as ex:
            print(f"Exception while deleting PID file {self.path}: {ex}", file=sys.stderr)


if __name__ == "__main__":
    # Classic file locations for daemons.
    # /etc/nrf24-timed.conf
    # /var/log/nrf24-timed.log
    # /var/log/nrf24-timed.out
    # /var/log/nrf24-timed.err
    # /var/run/nrf24-timed.pid
    # /var/opt/nrf24-timed/...

    # Set up argument parser.
    argp = argparse.ArgumentParser(add_help=False)
    argp.add_argument("-?", "--help", help="Display help.", action="store_true")
    argp.add_argument("-d", "--daemonize", help="Daemonize process to run in the background detached from the TTY (default: false).", action="store_true")
    argp.add_argument("-c", "--config", type=str, help="Path to configuration file (default: none)", default=None)
    argp.add_argument("-h", "--hostname", type=str, help="Hostname of Raspberry PI running the pigpiod daemon (default: local computer).", default=None)
    argp.add_argument("-s", "--seconds", type=int, help="Seconds between publishing time (default: 5 seconds).", default=5)

    # Parse command line arguments.
    args = argp.parse_args()

    # If help was requested, print the help text and exit.
    if args.help:
        argp.print_help()
        sys.exit(0)

    run_time_publisher(args.daemonize, args.hostname, args.seconds)

    # hostname
    # seconds / delay

    # ce_pin                17
    # channel               1
    # crc_bytes             2
    # data_rate             250KBPS, 1MBPS, 2MBPS
    # local_address         "DTP01"
    # remote_address        "DTCLN"
    # payload_size          10 (fixed)
