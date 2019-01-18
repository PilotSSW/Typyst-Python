Typyst
======
A typewriter service for your Linux system! Have typewriter sounds play with
each keystroke regardless of which application is running!


#### Installing Dependencies ####
You will need python3, pip3, pynput, wave, glob

``` bash
#! For Ubuntu based systems
sudo apt-get install python3 pip3
sudo -H pip3 install pynput glob wave
```

#### Configuration ####
You need to change the location string for the .wav files in initialize()


#### Usage ####
./typyst.py

hit some keys (they echo back out)

hit ESC twice to quit (not sure why)
