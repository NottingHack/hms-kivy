# hms-kivy
A collection of kivy based apps for HMS

A sign-in tool for Nottingham Hackspace AGM's and EGM's  
A kiosk for use in the space allowing registration of new RFID cards, Member management of Projects and Boxes

These have been designed to run on a Raspberry Pi with an official 7" touch screen and an attached RC522 RFID reader

## Requirements

This project is using [Poetry](https://python-poetry.org/) to manage the dependencies  
These boil down to Python3, Kivy and [pi-rc522](https://github.com/kevinvalk/pi-rc522.git)  
Once you have installed Poetry 

Inside the cloned repository you can now use poetry to setup the virtual environment and install all the dependencies

    poetry install

Then enter activate the environment with

    poetry shell

Form here you can access run one of the apps

    meeting
    kiosk

Or they can be run outside the env like so

    poetry run meeting

### Testing

Test can be run inside or outside the poetry shell with

    poetry run pytest


## Using Official RPi touch display

If you are using the official Raspberry Pi touch display, you need to configure Kivy to use it as an input source. To do this, edit the file ~/.kivy/config.ini and go to the [input] section. Add this:


    mouse = mouse
    mtdev_%(name)s = probesysfs,provider=mtdev
    hid_%(name)s = probesysfs,provider=hidinput



# **OUT OF DATE**
## Requirements
Kivy Pi OS install
 http://kivypie.mitako.eu

pi-rc522 python library
 https://github.com/kevinvalk/pi-rc522.git

## Client Credentials
Client Credentials can be generated with
```
php artisan passport:client --client
```

## Testing not on a pi
This will run on any device with kivy installed, when pi-rc522 library is not available it will listen for UDP broadcast on port 7861 for RFID string packets

There is a quick script `sendRfid.py` which takes a rfid serial as a command line arg and will broadcast it onto the network

## Testing on a pi
If you need to expose the HMS dev vagrant to you public network add
```
  config.vm.network "public_network", bridge: "en0: Wi-Fi (AirPort)"
```
to your VAGRANT file, updating the bridge: field as needed.

Then `vagrant reload` to restart the box with new setting.
Once the box is up, you can add its IP to the hosts file on the Pi

https://github.com/Himura2la/rc522-serial
https://github.com/DougieLawson/backlight_dimmer