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

Phones can subscribe and unsubscribe from getting the processed data each time it's available by sending an UDP message containing "Subscribe" or "Unsubscribe" to \<raspberry-default-gateway\>:9903