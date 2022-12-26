from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, DataGraphPopup, HistGraphPopup, DataErroPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from kivymd.uix.snackbar import Snackbar
from time import sleep
from datetime import datetime
import random
from timeseriesgraph import TimeSeriesGraph
from dbhandler import bdHandler
from dberror import dberror
from kivy_garden.graph import LinePlot


class Mainwidget(BoxLayout):
    """
    widget principal da aplicação
    """
    _updateThread = None
    _updateWidgets = True
    # tags são sensores de campo
    _tags = {}
    _max_points = 20
    _dadoerro = []

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
        self._hgraph = HistGraphPopup(tags=self._tags)
        self._derror = DataErroPopup(self._dadoerro)
        self._db = bdHandler(kwargs.get('db_path'),self._tags)
        self._dberro = dberror(kwargs.get('db_path_erro'))   
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
            Snackbar(text=f"Erro startDataRead:{e.args}", bg_color=(1,0,0,1)).open()
            
          

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
                self._db.insertData(self._meas)
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
    
    def getDataDB(self):
        """
        Método que coleta as informações da interface fornecidas pelo usuário 
        e requisita a busca no BD
        """
        try:
            init_t = self.parseDTString(self._hgraph.ids.txt_init_time.text) 
            final_t = self.parseDTString(self._hgraph.ids.txt_final_time.text)
            cols = []
            for sensor in self._hgraph.ids.sensores.children:
                if sensor.ids.checkbox.active: 
                    cols.append(sensor.id)

            if init_t is None or final_t is None or len(cols) == 0:
                return

            cols.append('timestamp')
            
            dados = self._db.selectData(cols, init_t, final_t)

            if dados is None or len(dados['timestamp']) == 0:
                return

            self._hgraph.ids.graph.clearPlots()
            # cria as linhas do grafico para cada tags selecionada
            for key, value in dados.items():
                if key == "timestamp":
                    continue
                p = LinePlot(line_width = 1.5, color = self._tags[key]['color'])
                p.points = [(x, value[x]) for x in range(0, len(value))] 
                self._hgraph.ids.graph.add_plot(p)
            self._hgraph.ids.graph.xmax = len(dados [cols [0]])
            # converte as strings "%Y-%m-%d %H:%M:%S.%f" no banco de dados para objetos do tipo datetime
            self._hgraph.ids.graph.update_x_labels([datetime.strptime(x,"%Y-%m-%d %H:%M:%S.%f") for x in dados['timestamp']])

        except Exception as e:
            Snackbar(text=f"Erro getDataDB:{e.args}", bg_color=(1,0,0,1)).open()

    def parseDTString(self, datetime_str):
        """
        Método que converte a string inserida pelo usuário para o formato utilizado na busca dos dados no BD"
        """
        try:
            d = datetime.strptime(datetime_str,'%d/%m/%Y %H:%M:%S')
            return d.strftime("%Y-%m-%d %H:%M:%S")

        except Exception as e:
            pdts = (f"Erro parseDTString:{e.args}")
            self._dberro.insertDataErro(pdts)
            Snackbar (text=(f"{pdts}"), bg_color=(1,0,0,1)).open()
    
    def getDataDBErro(self):
        """
        Método que coleta as informações da interface fornecidas pelo usuário 
        e requisita a busca no BD de erros
        """
        try:
            datas = self.parseDTStringErro(self._derror.ids.txt_data_erro.text)

            if datas is None:
                return

            data = self._dberro.selectDataErro(datas)


            if data is None:
                return

            for i in data:
                self._dadoerro.append(str(f'{i}\n'))

            self._derror.ids.error_label.text = str(self._dadoerro)

        except Exception as e:
            print("Erro: ",e.args)
            Snackbar(text=f"Erro getDataDBErro:{e.args}", bg_color=(1,0,0,1)).open()

    def parseDTStringErro(self, datetime_str_erro):
        """
        Método que converte a string inserida pelo usuário para o formato utilizado na busca dos dados de erro"
        """
        try:
            d = datetime.strptime(datetime_str_erro,'%d/%m/%Y')
            return d.strftime("%d/%m/%Y")

        except Exception as e:
            pdts = (f"Erro parseDTStringErro:{e.args}")
            self._dberro.insertDataErro(pdts)
            Snackbar (text=(f"{pdts}"), bg_color=(1,0,0,1)).open()
        