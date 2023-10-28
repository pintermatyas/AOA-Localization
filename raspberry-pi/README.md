# Angle of Arrival real-time positioning processed on a Raspberry Pi

This folder contains all the files required for the positioning to work on the Raspberry Pi.

Configuration steps:

1. Turn on the Wi-Fi Access Point on the Raspberry Pi.
2. Configure the EVK-ODIN-W2 modules with the following AT script:
```
AT+UWSC=0,0,1
AT+UWSC=0,2,"<Wi-Fi SSID>"
AT+UWSC=0,5,2
AT+UWSC=0,8,"<Wi-Fi Password>"
AT+UWSC=0,100,2
AT+UWSC=0,107,0
AT+UWSC=0,300,0
AT+UWSC=0,301,1
AT+UWSCA=0,1
AT+UWSCA=0,3
AT+UDDRP=0,"udp://<UDP Server IP>:<UDP Server Port>",2
AT+UMSM=1
AT+UMRS=1000000,2,8,1,1,0
AT&W
AT+CPWROFF
```
If the configuration was done correctly, the EVK-ODIN-W2 module should connect to the Wi-Fi after boot. It should blink purple right after turning it on and then it should start blinking blue when it successfully connected to the Wi-Fi AP.

3. Install the dependencies with ```pip install -r requirements.txt```
4. The script should be started with ```python init.py``` command.
5. If you want to follow the tag real time on the Android application, connect to the Raspberry Pi's Access Point and start the application.

# Logging

The logs of the application can be found in ```logs/output.log``` file.

# Network Topology

    +----------------+                      +----------------+          +----------------+
    |  EVK-ODIN-W2   |---->---+             |                |Port      |                |
    +----------------+        |             |                |9903      |                |
                              |             |                |<---------|                |
    +----------------+        |             |                |          |                |
    |  EVK-ODIN-W2   |---->---+         Port|                |          |                |
    +----------------+        |         9901|                |          |                |
                              |------------>|  Raspberry Pi  |          |     Phone(s)   |
    +----------------+        |             |                |          |                |
    |  EVK-ODIN-W2   |---->---+             |                |      Port|                |
    +----------------+        |             |                |      9902|                |
                              |             |                |--------->|                |
    +----------------+        |             |                |          |                |
    |  EVK-ODIN-W2   |---->---+             |                |          |                |
    +----------------+                      +----------------+          +----------------+

EVK-ODIN-W2 devices connect to the AP of the Raspberry Pi and stream their UDP messages to \<raspberry-default-gateway\>:9901.

The Raspberry Pi processes these UDP messages and sends out the processed data to the connected phone(s) based on a subscription service using \<phone-ip\>:9902.

Phones can subscribe and unsubscribe from getting the processed data each time it's available by sending an UDP message containing "Subscribe" or "Unsubscribe" to \<raspberry-default-gateway\>:9903. Subscribing and unsubscribing happens automatically whenever the application gets opened or closed.
