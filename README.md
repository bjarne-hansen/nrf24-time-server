# Raspberry Pi Time Publishing Daemon

## Background
Several constrained IoT devices are too simple to be connected to the 
Internet to get the current date/time via NTP.

This module is a daemon that allows (for example) a Raspberry Pi, which can
easily be connected to the Internet and synchronize date and time using NTP, to
publish the current date/time information via a NRF24L01 module.

IoT devices with a NRF24L01 transceiver, that is within range of the 
Raspberry PI can then listen on the fixed address "DTCLI" and receive
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

The fastest approach on a Raspberry Pi running raspbian is to install using apt:

    sudo apt-get update
    sudo apt-get install pigpio python-pigpio python3-pigpio 

### nrf24_timed

The nrf24_timed is a systemd service written in Python and depends on the 
**pigpio**, **nrf24**, and **systemd** modules.

The service code is in **src/nrf24_timed.py** file, the systemd service file
is in **nrf24_timed.service**, and the configuration file can be found in
**etc/nrf24_timed.ini**.

A small bash shell script installing the service on a Raspberry Pi is included in
the **install** file.

Before executing the install script make sure you have Python >= 3.6, pip, and
virtualenv installed. Make sure you are connected to the internet, as the
install script will download and install ependencies using pip.

The install file will install the service in the following directories:
/usr/local/bin/nrf24_timed
/usr/local/etc
/usr/local/lib/systemd/system

Inside the /usr/local/bin/nrf24_timed a virtual environment **venv** will be
created.

The install script will **not** start the service automatically, but will show
the status of the service.

After installation the service can be started, stopped, and motitored using the
standard systemctl and journalctl commands.
	
	$ systemctl status nrf24_timed
	$ systemctl start nrf24_timed
	$ systemctl reload nrf24_timed
	$ systemctl restart nrf24_timed
	$ systemctl stop nrf24_timed

	$ journalctl --unit nrf24*

The 'reload' command will send a SIGHUP signal asking the service to reload
its configuration from /usr/local/etc/nrf24_timed.ini (default).

Configuration for **pigpio**, **nrf24**, and the **nrf24_timed** service can
be found in the **etc/nrf24_timed.ini** file.

The data broadcast via NRF24 will be a binary payload pack'ed using the 
protocol format "\<B4sHBBBBBB".

	B:   Fixed protocol marker 0xfe
	4s:  Fixed string signature "TIME"
	H:   year    
        B:   month  
        B:   day     
        B:   hour   
        B:   minute 
        B:   second
        B:   weekday (Monday is 1 and Sunday is 7)

Constrained IoT devices will be able to listen for the


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

## Examples

	to de described


