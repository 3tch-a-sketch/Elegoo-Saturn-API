# Elegoo-Saturn-API
As Elegoo doesn't seem to offer any API for the saturn this is a home-made version from snooping traffic from Chitubox with Wireshark. This will also likely work with other printers that use the CBD control board but I'm unable to test this.

## Example
```python
from CBD_Api import Printer

if __name__ == "__main__":
    p = Printer("192.168.1.1")

    p.uploadFile("demo.ctb")

    p.softJog(150)

    print(p.getCardFiles())

    p.startPrinting(p.getCardFiles()[0][0])
```
