import socket
from time import sleep
from datetime import datetime as dt
import os
from queue import Queue

class Printer():
    def __init__(self, ip) -> None:
        if ip == "127.0.0.1":
            self.debug = True
        self.ip = ip
        self.port = 3000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sock.settimeout(20)
        self.buffSize = 4096
        self.jobs = Queue()
        
    def __sendRecieveSingle__(self,code,buffSize=-1) -> str: # sends an M-code then recieves a single packet answer
        self.sock.sendto(bytes(code, "utf-8"), (self.ip, self.port))
        if buffSize == -1:
            buffSize = self.buffSize
        output = self.sock.recv(buffSize)

        return output

    def __sendRecieveSingleNice__(self,code, buffSize=-1) -> str: # sends an M-code then recieves a single packet answer
        if buffSize == -1:
            buffSize = self.buffSize
        output = self.__stripFormatting__(self.__sendRecieveSingle__(code,buffSize))
        return output#.decode('utf-8')

    def __getUniversal__(self,split) -> str:
        output = (str)(self.__sendRecieveSingle__("M99999")).split(" ")[split].split(":")[1] # splits b'ok MAC:00:e0:4c:27:00:2e IP:192.168.1.174 VER:V1.4.1 ID:2e,00,27,00,17,50,53,54 NAME:CBD\r\n' into just a single field

        if not output:
            return "No Response"
        else:
            return output

    def getVer(self) -> str:
        """Returns the printers version

        Returns:
            str: Version
        """
        return self.__getUniversal__(3)
        
    def getID(self) -> str:
        """Returns Printers UID

        Returns:
            str: UID
        """
        return self.__getUniversal__(4)

    def getName(self) -> str:
        """Gets the printers Name

        Returns:
            str: Name
        """
        return self.__getUniversal__(5).split("\\")[0]

    def __stripFormatting__(self, string) -> str: # trims b'End file list\r\n' to End file list
        string = (string.decode("utf-8"))
        string = string.rstrip()
        return string

    def __stripSpaceFromBack__(self, string) -> str:
        bIndex = max([i for i, ltr in enumerate(string) if ltr == "b"]) # this returns the last 'B' from the given string. Because the last 'B' is that of the .ctb extension we know that the next char is a space that delimits filename and filesize
        return((string[:bIndex+1],string[bIndex+2:]))

    def getCardFiles(self) -> list:
        """Returns the list of CTB files on the storage

        Returns:
            list: (filename, size)
        """
        self.sock.sendto(bytes("M20", "utf-8"), (self.ip, self.port))
        output = []
        request = self.__stripFormatting__((self.sock.recv(self.buffSize)))

        while request != "End file list":
            if ".ctb" in request:
                if request != "Begin file list" and self.__stripSpaceFromBack__(request)[1] != 0: # this prevents deleted files from appearing
                    #output.append(request)
                    output.append(self.__stripSpaceFromBack__(request))

            request = self.__stripFormatting__((self.sock.recv(self.buffSize)))
            
        return(output)
    
    def homeAxis(self) -> None:
        """Homes Z axis
        """
        self.__sendRecieveSingle__("G28 Z")

    def getAxis(self) -> float:
        """Gets current Axis position

        Returns:
            float: current Z pos
        """
        pos = (float)((str)(self.__sendRecieveSingle__("M114")).split(" ")[4].strip("Z:"))
        return pos

    def jogHard(self,distance) -> None: # uses absolute pos
        """Jogs without checking machine softlimits (not recommmended)

        Args:
            distance (float): absolute position to move to
        """
        self.__sendRecieveSingle__("G0 Z"+ (str)(distance))

    def jogSoft(self,distance) -> str: # uses absolute pos
        """Jogs after checking machine softlimits

        Args:
            distance (float): absolute position to move to

        Returns:
            str: If move possible
        """
        if(distance < 200 or distance < 1):
            self.jogHard(distance)
            return "Complete"
        else:
            return "Distance too great or other error"

    def removeCardFile(self,filename) -> str:
        """Removes specified file from storage

        Args:
            filename (str): filename to remove including extension

        Returns:
            str: If is action complete
        """
        return (str)(self.__sendRecieveSingleNice__("M30 "+filename))

    def startPrinting(self,filename) -> str:
        """Starts printing from storage

        Args:
            filename (str): what do you think? Must include extension

        Returns:
            str: If is action complete
        """
        return self.__sendRecieveSingleNice__(f"M6030 '{filename}'")
    
    def printingStatus(self) -> str:
        """Returns if the machine is printing

        Returns:
            str: Machine State
        """
        string = self.__sendRecieveSingleNice__("M27")
        if string == "Error:It's not printing now!":
            return "Not Printing"
        elif string.split()[0] == "SD":
            return "Printing"
        else:
            return "Not Printing"

    def printingPercent(self) -> list:
        """Returns the percentage of the print in bytes complete (not massively accurate)

        Returns:
            list: [completed, total]
        """
        string = self.__sendRecieveSingleNice__("M27")
        return string.split()[3].split("/")

    def stopPrinting(self) -> str:
        """Stops current print

        Returns:
            str: If completed
        """
        return self.__sendRecieveSingleNice__("M33")


    # upload structure
    # M28 [filename]
    # send data in 1280 chunks
    # M4012 I1 T[total bytes sent]
    # M29
    # all of this is encoded

    def uploadFile(self,fileNameLocal,fileNameCard="") -> str:
        """Uploads file to storage

        Args:
            fileNameLocal (str): local filename including extension
            fileNameCard (str, optional): filename on storage including extension. Defaults to same as local filename.

        Returns:
            str: If completed
        """
        if fileNameCard == "": fileNameCard = fileNameLocal
        
        # start transmission
        m28 = self.__sendRecieveSingleNice__(f"M28 {fileNameCard}")
        if m28 != "ok N:0":
            return f"M28 Error: {m28}"
        
        l=os.stat(fileNameLocal).st_size

        f=open(fileNameLocal,'rb')
        remain=l
        offs=0
        retr=0
        print('Length:',l)
        #
        while remain > 0:
            dd=f.read(1280)
            #print(dd,len(dd),offs)
            remain=remain-len(dd)
            dc=bytearray(offs.to_bytes(length=4, byteorder='little'))
            cxor=0
            for c in dd: cxor=cxor ^ c
            for c in dc: cxor=cxor ^ c
            dc.append(cxor)
            dc.append(0x83)
            #print('chk:',binascii.hexlify(bytearray(dc)).decode('ascii'),offs,cxor)
            offs=offs+len(dd)

            #udp_send(dd+dc)
            #s=udp_gettxt(forever=True)
            self.sock.sendto(dd+dc, (self.ip,self.port))
            s = self.sock.recv(self.buffSize)
            #print(s)
            print(retr,remain,end='   \r')
            #print('chk:',binascii.hexlify(bytearray(dc)).decode('ascii'),offs,cxor)
            
        
        #sleep(0.1)
        m4012 = self.__sendRecieveSingleNice__(f"M4012 I1 T{l}")
        if m4012.split()[0] != "ok":
            return f"Size Verify Error: {m4012}"

        return self.__sendRecieveSingleNice__("M29")

    def formatCard(self):
        """Formats storage
        """
        for file in self.getCardFiles():
            self.removeCardFile(file[0])

    def startJobPrint(self) -> str:
        """Starts a job from the jobs queue
        
        Returns:
            str: result
        """
        if self.jobs.not_empty:
            return self.startPrinting(self.jobs.get())
        else:
            return "Queue empty"


if __name__ == "__main__":
        p = Printer("192.168.1.174")

        print(p.getCardFiles())


    
    
