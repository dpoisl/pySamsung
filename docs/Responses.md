Some guesses about the meaning of various response messages:

| Type | Payload                | Description                        |
| ---- | ---------------------- | ---------------------------------- |
|    2 | \n\x00\x01\x00\x00\x00 | Currently Showing TV               |
|    2 | \n\x00\x18\x00\x00\x00 | Showing INFO Menu, Channel List,   |
|      |                        | SmartHUB or Guide                  |
|    2 | \n\x00\x0c\x00\x00\x00 | Showing TTX                        |
|    2 | \n\x00\x02\x00\x00\x00 | Showing Menu, Tools Menu,          |
|      |                        | Source Menu, E-Manual, etc.        |
|    4 | \n\x00\x04\x00\x00\x00 | Timeshift startet                  |


There seems to be a bitmask involved:
00000000 00000001   in tv
00000001 10000000   in overlay
00000000 11000000   in ttx
00000000 00000010   menu
00000000 00000100   timeshift?
