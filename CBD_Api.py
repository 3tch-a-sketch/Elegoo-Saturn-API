import socket

class printer():
    def __init__(self, ip) -> None:
        if ip == "127.0.0.1":
            self.debug = True
        self.ip = ip
        self.port = 3000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        
    def __sendRecieveSingle__(self,code) -> str: # sends an M-code then recieves a single packet answer
        self.sock.sendto(bytes(code, "utf-8"), (self.ip, self.port))
        output = self.sock.recv(4096)

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


if __name__ == "__main__":
    p = printer("192.168.1.174") # Localhost used to put module into self-test mode
    
    print(p.getVer())
    print(p.getID())
    print(p.getName())
