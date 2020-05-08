# Raspberry Pi Time Publishing Daemon

## Background
Several constrained IoT devices are too simple to be connected to the 
Internet to get the current date/time via NTP.

This module is a daemon that allows (for example) a Raspberry Pi, which can
easily be connected to the Internet and synchronize date and time using NTP, to
publish the current date/time information via a NRF24L01 module.

IoT devices with a NRF24L01 transceiver, that is within range of the 
Raspberry PI can then listen on the fixed address "DTCLN" and receive
the current year, month, day, hour, minute, second, and weekday.

Such client may subscribe to the current date/time information on each 
"reboot", or they may store the date/time information in a RTC and then
synchronize periodically to maintain a relatively precise notion of the 
current time.

The date/time daemon publishes the current date/time information every 5 
seconds per default.

The Time Publishing Daemon is written in Python and uses the **pigpiod** deamon
that allows easy access to the GPIO pins of the Raspberry PI.  Please refer to
http://abyz.me.uk/rpi/pigpio/pigpiod.html for more information on the pigpiod
daemon.

## Installing

### pigpiod

The pigpiod daemon, which is a prerequisite, can be downloaded and installed
using instructions found here: http://abyz.me.uk/rpi/pigpio/download.html

The fastest approach is to install using apt.

    sudo apt-get update
    sudo apt-get install pigpio python-pigpio python3-pigpio 

### Hardware

The default wiring for the Raspberry PI and the NRF24L01 module for a Raspberry
PI Zero Wireless is:

    NRF24L01
    PIN side
    +---+----------------------
    |       *    *
    +---+
    |7|8|   purple |   -
    +-+-+
    |5|6|   green  |  blue
    +-+-+
    |3|4|   yellow | orange
    +-+-+   
    |1|2|   black  |  red
    +-+-+----------------------

        NRF24L01                PI ZW
    -------------------------------------
    PIN DESC  COLOR           PIN  GPIO
    1   GND   black   <--->   6     -
    2   3.3V  red     <--->   1     - 
    3   CE    yellow  <--->   22    25
    4   CSN   orange  <--->   24     8
    5   SCKL  green   <--->   23    11   
    6   MOSI  blue    <--->   19    10 
    7   MISO  purple  <--->   21     9 
    8   IRQ           <--->   N/C   - 

I tend to always use the same colouring of the connecting cables as this helps
me to easily keep track of the wiring, and the above color coding seems to be
popular on a number of sites having articles about NRF24L01 transceivers.

### Software

The `NRF24.py` code included here is based on code found here: 
https://raspberrypi.stackexchange.com/questions/77290/nrf24l01-only-correctly-retrieving-status-and-config-registers

The original copyright holder, which is the same author as for the pigpiod daemon, has adviced
me that the NRF24.py code can be considered Public Domain, and be amended and distributed for any
purpose whatsoever.

The `pigpio.py` code is taken from the python-pigpio/python3-pigpio distribution.

The ``rf24-time-server.py`` can run as a daemon publishing date/time information
every 5 seconds.

The payload is packed with 10 bytes using format ">3shbbbbb":
* Signature "tim" (3 chars)
* Year (short, 2 bytes)
* Month (byte, 1 byte)
* Day (byte, 1 byte)
* Hours (byte, 1 byte)
* Minutes (byte, 1 byte)
* Seconds (byte, 1 byte)

The pid file is stored at: ``/var/run/nrf24-timed.pid``

The stdout is redirected to (daemon): ``/var/log/nrf24-timed.out``

The stderr is redirected to (daemon): ``/var/log/nrf24-timed.err``

The daemon can be started using the command line:

    usage: nrf24-time-server.py [-?] [-d] [-c CONFIG] [-h HOSTNAME] [-s SECONDS]

    optional arguments:
      -?, --help            Display help.
      -d, --daemonize       Daemonize process to run in the background detached
                            from the TTY (default: false).
      -c CONFIG, --config CONFIG
                            Path to configuration file (default: none)
      -h HOSTNAME, --hostname HOSTNAME
                            Hostname of Raspberry PI running the pigpiod daemon
                            (default: local computer).
      -s SECONDS, --seconds SECONDS
                            Seconds between publishing time (default: 5 seconds).

The daemon should be started using sudo.

A ``nrf24-time-client`` example running on an Arduino Nano can be found at:
https://github.com/bjarne-hansen/nrf24-time-client

This software is published under a "Zero Clause BSD" license. Please refer to the LICENSE file.


