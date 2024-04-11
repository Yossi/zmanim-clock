# Zmanim Clock
This was intended to be a clock that shows sha'ah zmanit.
It does that, but along the way it picked up some more features.
* regular clock with date
* parsha, day of the week, hebrew date
* list of times from chabad.org
* (optional) two hour weather forcast using minutecast (requires [api key](https://developer.accuweather.com/minutecast-api/apis))
* (optional) page number display
    * (even more optional) IR remote control of page numbers

## Hardware List
This list is just what I used, you should be able to stray from it as makes sense for your case.
* Raspberry Pi Zero W (needs to be W for wifi) and micro sd card
* Screen with HDMI input
* HDMI cable with mini HDMI (for the Pi Zero end) or a mini HDMI adaptor
* (optional, but quite helpful for debugging) USB to TTL cable
* (optional, for page number display) Keyboard with some way to connect it to the microUSB ports on the Pi Zero (maybe there's a way to have this work over bluetooth? have not explored)
* (optional, cheaper and better than the keyboard) Cheap junk ir remote and sensor. These can be had for less than 2 bucks from the usual places. Try to get a controller that has all the numbers 0-9, +, -, and backspace buttons. Doesn't have to be exact, you will be assigning these things to buttons later, so as long as there are at least 13 buttons its fine. Try to get a sensor that works on 3.3v, but if all you can find is 5v it can be worked with too. Recommend buying several since "cheap junk" doesnt do justice for how poorly made these things can be.

## Setup on computer
### Install Raspberry Pi OS
On your computer get [Raspberry Pi Imager](https://www.raspberrypi.com/software/)  
`sudo apt  install rpi-imager`  
`rpi-imager`  
Click [Choose OS] and then on Raspberry Pi OS (other). Then choose Raspberry Pi OS Lite (32-bit).

Needs 32-bit for the Pi Zero W, ~~Zero 2 can use 64-bit~~ [Tested a Zero 2 and while it does run the 64bit os, this clock doesnt work on it (error: XDG_RUNTIME_DIR is invalid or not set in the environment.). Actually needs 32bit os to work right now]. You want the Lite version, no need for all the extra bloat from a desktop environment.

Then choose the sd card and write to it. You may want to click on the gear and change some settings ahead of time to save you some bother later. 
* set hostname to whatever
* enable ssh with password authentication for now (later this can be made to work only with keys)
* set a password (leave username as pi. will be a hassle otherwise)
* configure wifi (later more networks can be added)
* configure timezone

### Move files to SD card
These files will be going to /rootfs/home/pi/ :  
* clock.py 
* NotoSansHebrew.ttf  
* requirements.txt  
* weather.py (can skip if not doing weather)  
* zmanim.py  

* Edit settings.py.example to contain the zipcode to be used for chabad.org (required) and if you will be using minutecast put in your api key and your gps coordinates.  
Save as settings.py & copy to card.

* Edit zman_clock.service.example to have the resolution of the target screen. Remove "--weather" from the end of the long line if you will not be using minutecast.  
Save as zman_clock.service & copy to card.

* (optional) If you have a server you can already ssh into, you can make the Pi do a reverse proxy to it and it becomes MUCH easier to work with it. Don't need any port forwarding on networks you dont fully control (like at shul). If you want to go down this route, edit reverse_proxy.service.example line 9 at the end. This will make it so you can ssh to your server and then `ssh pi@localhost -p22222` to reach the Pi wherever it may be.  
Save as reverse_proxy.service & copy to card.

### (optional) Edit config.txt if you will be using a USB to TTL cable and/or an IR reciever
Edit /bootfs/config.txt  
* For USB to TTL, at the bottom, last line, add `enable_uart=1` on it's own line.  
* For IR, add the line `dtoverlay=gpio-ir,gpio_pin=17`

While you're in this folder, make sure firstrun.sh exists. If it doesn't, all your preconfigured settings (user, password, wifi, etc.) will be absent.

## Setup Hardware at the Raspberry Pi
Eject SD card from computer and put it in the Pi.  
Connect HDMI between the Pi and your screen. Make sure the screen is on before the Pi turns on or it might not read the correct resolution.  
### (optional) Connect IR receiver and/or USB to TTL
![Pi GPIO Pins](pins.png)  
(If needed, solder some header pins on your board. Take out the sd card and unplug everything first)  

Connect the IR data line to pin 11 (GPIO 17). Ground to a ground pin, and VCC+ to a 3.3v pin (preferably).  

For USB to TTL, connect the green wire to pin 10 (GPIO15) and the white wire to pin 8 (GPIO14). Black wire goes to a ground pin. The red wire can either power the whole Pi through one of the 5v pins (pin 2 or 4) or can be left hanging and you power the Pi through the microUSB port like normal. (DO NOT USE BOTH POWER OPTIONS AT THE SAME TIME!)

## Power on the Pi for the first time
The Pi will do some stuff then reboot itself.  
You will want to connect to the Pi somehow. If you are lucky, you can ssh right in. If less lucky, you might need to connect a keyboard and fiddle with it that way. 
The best way is to use the USB to TTL cable. `sudo screen /dev/ttyUSB0 115200` will connect you directly to the Pi. (If this starts showing garbled text it might be because more then one instance is running. `sudo ./kill_screen.sh` will clear them all out so you can start fresh.)  
You should now be in a position to `ls` the home directory on the Pi and see all the files you put there earlier.
### Make sure network is up
`ping 8.8.8.8`   
If it isn't, use `sudo raspi-config`
* Choose `1 System Options` -> `S1 Wireless LAN`   
* Choose your country.
* Enter your wifi network name (SSID) and password
* Hit < Finish >
### Make sure the time is right
`date`  
If it has wrong timezone, use `sudo raspi-config`
* Choose `5 Localization Options` -> `L2 Timezone`
* Follow the menus to your timezone

## (Optional) Get reverse proxy working
Make sure you can SSH to your server from the Pi. Accept new fingerprint, or whatever is needed. Exit back out to the Pi.
### Setup passwordless login
On the Pi `ssh-keygen -t rsa`, takes some time on the underpowered Pi. When it's done, save the key to the default location. Leave the passphrase empty. Send the pub key to the server with `ssh-copy-id -p <your port> you@yourdomain.tld`. 
### Setup reverse proxy service
`sudo cp reverse_proxy.service /etc/systemd/system`  
`sudo systemctl daemon-reload`  
`sudo systemctl enable reverse_proxy.service`  
`sudo systemctl start reverse_proxy.service`
### Switch over to SSH through your server instead of USB to TTL
SSH to your server. `ssh pi@localhost -p22222` You will probably want to set up passwordless login in this direction too. Follow instructions from above. My assumption here is you know what you are doing and aren't going to trip over yourself if you have some special setup. Once this is working you can go one step further and do the same thing from your local computer like this `ssh -o 'ProxyCommand=ssh -p <your port> -W localhost:22222 you@yourdomain.tld' pi@localhost`

## Get zmanim clock working
`sudo apt -y install libsdl2-2.0-0 libsdl2-ttf-2.0-0 libegl-dev entr`  
`python -m venv venv`  
`venv/bin/pip install -r requirements.txt`
### Setup service to start clock automatically on boot
`sudo cp zman_clock.service /etc/systemd/system`  
`sudo systemctl daemon-reload`  
`sudo systemctl enable zman_clock.service`  
`sudo systemctl start zman_clock.service`
## (Optional) Setup IR stuff
If you haven't already done this while the SD card was in the computer, edit `sudo nano /boot/firmware/config.txt`  
Add the line `dtoverlay=gpio-ir,gpio_pin=17`. Reboot.
Also make sure your IR sensor is attached.
### Map the scancodes that the IR remote is sending to keycodes
`sudo apt-get install ir-keytable`  
`sudo ir-keytable -p all`  
`sudo ir-keytable -t`  
Now point the remote at the sensor and push a button. Note what protocol your remote speaks. All buttons on the remote will use the same protocol. The list of possibilities was displayed earlier when you activated them all with the `-p all` command.  
Also note the scancode each key emits. Specifically you want the scancodes for the keys that are going to be assigned to the numbers (`0-9`) as well as `+`, `-` and `backspace`. Remember, just because something is printed on the remote doesn't mean the button has to be assigned to that thing. Use common sense and maybe a permanent marker as needed.  
Put the protocol and the scancodes into the correct places in `ir_remote_keymap.toml`.  
If you want, to can also assign the remaining keys on the remote to whatever, but this clock will ignore them. See [this link](https://peppe8o.com/download/txt/Zir-keytable%20available%20keycodes.txt) for what's available. Usually, the correct ones are those keys starting with the "KEY_" prefix.
### Test that ir_remote_keymap.toml file is good.
`sudo ir-keytable -c`  
`sudo ir-keytable -w ir_remote_keymap.toml`  
`sudo ir-keytable -r` This should show all the current scancode to KEY_ mappings.  
`sudo ir-keytable -t` (Optional) Run this and push some buttons to see it read them correctly.
### Install this .toml file in the right place
`sudo cp ir_remote_keymap.toml /etc/rc_keymaps/`  
Open for editing `sudo nano /etc/rc_maps.cfg`  
Go down to the driver table and add a line `* * ir_remote_keymap.toml` (First and second column are just a `*`)  
Save and exit.
Make sure `sudo ir-keytable -a /etc/rc_maps.cfg -s rc0` returns happy looking things now. If it's loading extra protocols it wont hurt anything but you can put a stop to that by commenting/removing everything else in the driver table mentioned above.
