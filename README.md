# hms-kivy
A collection of kivy based apps for HMS

A sign-in tool for Nottingham Hackspace AGM's and EGM's  
A kiosk for use in the space allowing registration of new RFID cards, Member management of Projects and Boxes

These have been designed to run on a Raspberry Pi with an official 7" touch screen and an attached RC522 RFID reader


# **OUT OF DATE**
## Requrments
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

