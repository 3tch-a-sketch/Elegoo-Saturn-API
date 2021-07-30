import socket
import struct

class printer():
    def __init__(self, ip) -> None:
        if ip == "127.0.0.1":
            self.debug = True
        self.ip = ip
        self.port = 3000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.buffSize = 4096
        
    def __sendRecieveSingle__(self,code) -> str: # sends an M-code then recieves a single packet answer
        self.sock.sendto(bytes(code, "utf-8"), (self.ip, self.port))
        output = self.sock.recv(self.buffSize)

        return output

    def __getUniversal__(self,split) -> str:
        output = (str)(self.__sendRecieveSingle__("M99999")).split(" ")[split].split(":")[1] # splits b'ok MAC:00:e0:4c:27:00:2e IP:192.168.1.174 VER:V1.4.1 ID:2e,00,27,00,17,50,53,54 NAME:CBD\r\n' into just a single field

        if not output:
            return "No Response"
        else:
            return output

    def getVer(self) -> str:
        return self.__getUniversal__(3)
        
    def getID(self) -> str:
        return self.__getUniversal__(4)

    def getName(self) -> str:
        return self.__getUniversal__(5).split("\\")[0]

    def __stripFormatting__(self, string) -> str: # trims b'End file list\r\n' to End file list
        string = string[2:]
        string = string[:len(string)-5]
        return string

    def __stripOkFormatting__(self, string) -> str: # trims b' ok End file list\r\n' to End file list
        
        output = string[8:]
        return output

    def __stripSpaceFromBack__(self, string) -> str:
        bIndex = max([i for i, ltr in enumerate(string) if ltr == "b"]) # this returns the last 'B' from the given string. Because the last 'B' is that of the .ctb extension we know that the next char is a space that delimits filename and filesize
        return((string[:bIndex+1],string[bIndex+2:]))

    def getCardFiles(self) -> str:
            self.sock.sendto(bytes("M20", "utf-8"), (self.ip, self.port))
            output = []
            request = self.__stripFormatting__((str)(self.sock.recv(self.buffSize)))

            while request != "End file list":
                if ".ctb" in request:
                    if request != "Begin file list":
                        #output.append(request)
                        output.append(self.__stripSpaceFromBack__(request))

                request = self.__stripFormatting__((str)(self.sock.recv(self.buffSize)))
                
            print(output)
        
    def homeZ(self) -> None:
        self.__sendRecieveSingle__("G28 Z")

    def getZ(self) -> float:
        pos = (float)((str)(self.__sendRecieveSingle__("M114")).split(" ")[4].strip("Z:"))
        return pos

    def jogHard(self,distance) -> None: # uses absolute pos
        self.__sendRecieveSingle__("G0 Z"+ (str)(distance))

    def jogSoft(self,distance) -> bool: # uses absolute pos
        if(distance < 200):
            self.jogHard(distance)
            return True
        else:
            return False

if __name__ == "__main__":
    p = printer("192.168.1.174") # Localhost used to put module into self-test mode
    
    #p.getCardFiles()
    #print((p.__sendRecieveSingle__("M114"))) # gives locations
    #print(p.getZ())
