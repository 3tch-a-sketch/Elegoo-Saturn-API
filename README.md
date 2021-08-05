# Elegoo-Saturn-API
As Elegoo doesn't seem to offer any API for the saturn this is a home-made version from snooping traffic from Chitubox with Wireshark. This will also likely work with other printers that use the CBD control board but I'm unable to test this.

## Functions
### getVer
Returns the printers version
### getID
Returns printers UID
### getName 
Returns printers Name (this is not implemented in the saturn and only returns CBD)
### getCardFiles
Returns a list of all the .ctb files on the card
### homeAxis
Homes z-axis
### getAxis
Returns z-axis postion
### jogHard (position)
Jogs to the position given without respecting the softlimits of the machine
### jogSoft (position)
Jogs to the postions given while respecting machine softlimits
### removeCardFile (filename)
Removes file of given name from the card
### startPrinting (filename)
Prints the given file from the card
### printingStatus
Retuns if the machine is printing or not
### printingPercent 
Returns an array of the bytes printed and total bytes
### stopPrinting
Stops printing
### uploadFile (fileNameLocal, FileNameCard)
Uploads the fileNameLocal to the card while naming the file whatever FileNameCard is defaults to fileNameLocal
### Format card
Removes all .ctb files from card

## Installing
Windows
```Python
pip install -r requirements.txt
```
MacOs/ Linux
```Python
pip3 install -r requirements.txt
```

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
