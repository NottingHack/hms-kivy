# hms-kivy
A collection of kivy based apps for HMS

A sign-in tool for Nottingham Hackspace AGM's and EGM's  
A kiosk for use in the space allowing registration of new RFID cards, Member management of Projects and Boxes

These have been designed to run on a Raspberry Pi with an official 7" touch screen and an attached RC522 RFID reader

## Requirements

This project is using [Poetry](https://python-poetry.org/) to manage the dependencies  
These boil down to Python3, Kivy and [pi-rc522](https://github.com/kevinvalk/pi-rc522.git)  

Note on Raspberry Pi need to install kivy source deps first https://kivy.org/doc/stable/installation/installation-rpi.html#install-source-rpi


Once you have installed Poetry 

Inside the cloned repository you can now use poetry to setup the virtual environment and install all the dependencies

    poetry install

Then enter activate the environment with

    poetry shell

Form here you can access run one of the apps

    meeting
    kiosk
    rfid

Or they can be run outside the env like so

    poetry run meeting

### Testing

Test can be run inside or outside the poetry shell with

    poetry run pytest


### Using Official RPi touch display

If you are using the official Raspberry Pi touch display, you need to configure Kivy to use it as an input source. To do this, edit the file ~/.kivy/config.ini and go to the [input] section. Add this:


    mouse = mouse
    mtdev_%(name)s = probesysfs,provider=mtdev
    hid_%(name)s = probesysfs,provider=hidinput


Also recommend setting the keyboard mode in the [kivy]

    keyboard_mode = systemanddock


### Client Credentials
With in HMS you need to generate a Client Credentials with the following command

    php artisan passport:client --client

The details of which can then be entered into the setting panel/file

## Apps

### kiosk

The main Kiosk app for use with in the space

### meeting

This is the original AGM Meeting check in from hms-meeting

### rfid

This is a cli helper for presenting RFID tags over UDP, its used in development when not running on a Pi where pi-rc522 is available

commands are `present` or `remove`  
`present` requires a RFID UID parameter


## Testing on a pi
If you need to expose the HMS dev vagrant to you public network add
```
  config.vm.network "public_network", bridge: "en0: Wi-Fi (AirPort)"
```
to your VAGRANT file, updating the bridge: field as needed.

Then `vagrant reload` to restart the box with new setting.
Once the box is up, you can add its IP to the hosts file on the Pi


#### Notes / TODO
https://github.com/Himura2la/rc522-serial
https://github.com/DougieLawson/backlight_dimmer