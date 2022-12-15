from pyModbusTCP.server import DataBank, ModbusServer
import random
from time import sleep


class ServidorMODBUS():
    """
    Classe Servidor Modbus
    """
    
    def __init__(self, host_ip, port):
        """
        Construtor
        """
        self._db = DataBank()
        self._server = ModbusServer(host=host_ip,port=port,no_block=True,data_bank=self._db)

    def run(self):
        """
        Execução do servidor Modbus
        """
        try:

            self._server.start() 
            print("Servidor em execução")
            while True:
                self._db.set_words (1800, [random.randrange (int(0.95*400), int(1.05*400))]) 
                self._db.set_words (1601, [random.randrange (int(0.95*20), int (1.05*20))]) 
                self._db.set_words (1002, [random.randrange(int (0.95*30), int (1.05*30))]) 
                self._db.set_words (1003, [random.randrange(int (0.95*110), int(1.05*110))]) 
                self._db.set_words (1884, [random.randrange (int(0.95*180), int(1.05*180))]) 
                self._db.set_words (1005, [random.randrange (int(0.95*260), int(1.05*260))]) 
                self._db.set_words (1006, [random.randrange(int(0.95*280), int(1.05*280))]) 
                self._db.set_words (1007, [random.randrange (int(0.95*300), int(1.05*300))]) 
                self._db.set_words (1808, [random.randrange (int(0.95*340), int(1.05*340))])
                print ('==========================')
                print (f'Tabela MODBUS')
                print (f'Holding Registers\r\n R1000:{self._db.get_words(1000)} \r\n R2000:{self._db.get_words(2000)}') 
                print (f'Coils \r\n R1000:{self._db.get_bits(1000)}')
                print ('==========================')
                sleep(1)
                
        except Exception as e:
            print("Erro: ",e.args)