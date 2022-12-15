from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, DataGraphPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from kivymd.uix.snackbar import Snackbar
from time import sleep
from datetime import datetime
import random
from timeseriesgraph import TimeSeriesGraph


class Mainwidget(BoxLayout):
    """
    widget principal da aplicação
    """
    _updateThread = None
    _updateWidgets = True
    # tags são sensores de campo
    _tags = {}
    _max_points = 20

    def __init__(self, **kwargs):
        """
        Construtor do widget principal
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self._serverIP = kwargs.get ('server_ip')
        self._serverPort = kwargs.get ('server_port')
        self._modbusPopup = ModbusPopup(self._serverIP,self._serverPort) 
        self._scanPopup = ScanPopup(self._scan_time)
        self._modbusClient = ModbusClient (host=self._serverIP, port=self._serverPort)
        self._meas = {}
        self._meas['timestamp'] = None 
        self._meas['values'] = {}
        # key são as tags(sensores) do modbus_addrs
        for key,value in kwargs.get('modbus_addrs').items():
            if key == 'fornalha':
                plot_color = (1,0,0,1)
            else:
                plot_color = (random.random(), random.random(), random.random(),1) 
            self._tags[key] = {'addr': value, 'color':plot_color}
        self._graph = DataGraphPopup(self._max_points, self._tags['fornalha']['color'])
                    
    def startDataRead(self, ip, port):
        """
        Método utilizado para a configuração do IP e porta do servidor MODBUS e 
        inicializar uma thread para a leitura dos dados e atualização da interface 
        gráfica
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        try:
            Window.set_system_cursor("wait") 
            self._modbusClient.open() 
            Window.set_system_cursor("arrow")
            if self._modbusClient.is_open:
                self._updateThread = Thread(target=self.updater) 
                self._updateThread.start()
                self.ids.img_con.source ='imgs\conectado.png'
                self._modbusPopup.dismiss()
                Snackbar(text=f"Conexão realizada com sucesso!", bg_color=(0,1,0,1)).open()
            else:
                self._modbusPopup.setInfo("Falha na conexão com o servidor")

        except Exception as e:
            Snackbar(text=f"Erro DataRead:{e.args}", bg_color=(1,0,0,1)).open()

    def updater(self):
        """
        Método que invoca as rotinas de leitura dos dados, atualização da interface e 
        inserção dos dados no Banco de dados
        """
        try:
            while self._updateWidgets: 
                # ler os dados MODBUS
                self.readData() 
                # atualizar a interface
                self.updateGUI()
                # inserir os dados no BD 
                sleep(self._scan_time/1000) 

        except Exception as e:
            self._modbusClient.close()
            Snackbar(text=f"Erro updater:{e.args}", bg_color=(1,0,0,1)).open()

    def readData(self):
        """
        Método para a leitura dos dados por meio do protocolo MODBUS
        """
        self._meas['timestamp'] = datetime.now()
        for key, value in self._tags.items():
            # read_holding_registers(value['addr'],1)[0] retorna tupla por isso [0] 
            # para ler a primeira posiçao de um unico valor
            self._meas['values'][key] = self._modbusClient.read_holding_registers(value['addr'],1)[0]
    
    def updateGUI(self):
        """
        Método para atualização da interface grafica a partir dos dados lidos
        """
        # Atualização dos labels das temperaturas 
        for key,value in self._tags.items():
            # Por id das TempLabel ser o mesmo nome das key no modbus_addrs basta chamar as key para atualiza-las
            self.ids[key].text = str(self._meas['values'][key]) + ' °C'

        #Atualização do nível do termômetro
        self.ids.lb_temp.size = (self.ids.lb_temp.size[0],self._meas['values']['fornalha']/450*self.ids.termometro.size[1])

        #Atualização do gráfico
        self._graph.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['fornalha']),0)
        
    def stopRefresh(self):
        """
        Método para fechar o updateWidgets quando fechado o app
        """
        self._updateWidgets = False
