import pymcprotocol
#----------------------------------------------------------------------
class SLMP_PLC():
    def __init__(self, ipv4:str, port:int):
        self.client = self.__startConnection(ipv4, port)
    #------------------------------------------------------------------
    def __del__(self):
        if self.client != None:
            (self.client).close()
    #------------------------------------------------------------------
    def __startConnection(self, ipv4:str, port:int)-> pymcprotocol:
        try:
            client = pymcprotocol.Type3E()
            client.connect(ipv4, port)
        except:
            return None
        return client
    #------------------------------------------------------------------
    def readPlc(self, begining:int, batch:int=1)-> list:
        try:
            return (self.client).batchread_bitunits(headdevice=f"M{begining}",
                                                        readsize=batch)
        except:
            return []
    #------------------------------------------------------------------
    def activeAddress(self, address:int)-> bool:
        try:
            (self.client).batchwrite_bitunits(headdevice=f"M{address}",
                                                values=[1])
        except:
            return False
        return True
    #------------------------------------------------------------------
    def deactiveAddress(self, address:int)-> bool:
        try:
            (self.client).batchwrite_bitunits(headdevice=f"M{address}",
                                                values=[0])
        except:
            return False
        return True   
#----------------------------------------------------------------------