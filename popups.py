from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivymd.uix.snackbar import Snackbar
from kivy.uix.boxlayout import BoxLayout
from dberror import dberror


class ModbusPopup(Popup):
    '''
    Popup da configuração do protocolo MODBUS
    '''
    _info_lb = None
    def __init__(self, server_ip, server_port, **kwargs):
        '''
        Construtor da classe ModbusPopup
        '''
        super().__init__(**kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_porta.text = str(server_port)

    def setInfo(self, message):
        self._info_lb = Label(text=message)
        self.ids.layout.add_widget(self._info_lb)
    
    def clearInfo(self):
        if self._info_lb is not None:
            self.ids.layout.remove_widget (self._info_lb)

class ScanPopup(Popup):
    '''
    Popup da configuração do tempo de varredura
    '''
    def __init__(self, scantime, **kwargs):
        '''
        Construtor da classe ScanPopup
        ''' 
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)

class DataGraphPopup(Popup):
    '''
    Popup do gráfico do fornalha
    '''  
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(line_width = 1.5, color = plot_color)
        self.ids.graph.add_plot(self.plot) 
        self.ids.graph.xmax = xmax
       

class LabeledCheckBoxDataGraph(BoxLayout):
    pass

class HistGraphPopup(Popup):
    '''
    Popup do gráfico de dados historicos e cria os checkbox do grafico
    '''
    def __init__(self, **kwargs):
        super().__init__()
        try:
            for key, value in kwargs.get('tags').items():
                cb = LabeledCheckBoxHistGraph() 
                cb.ids.label.text = key
                cb.ids.label.color = value['color']
                cb.id = key
                td = self.ids.sensores.add_widget(cb)

        except Exception as e:
            Snackbar(text=f"Erro HistGraphPopup:{e.args}", bg_color=(1,0,0,1)).open() 

    # def uncheck_all(self):
    #     """
    #     Desmarca todos os CheckBox
    #     """
    #     try:
    #         for checkbox in self.checkbox_list:
    #             if isinstance(checkbox, LabeledCheckBoxHistGraph):
    #                 checkbox.active = False       
    #     except Exception as e:
    #         Snackbar(text=f"Erro DataRead:{e.args}", bg_color=(1,0,0,1)).open()
    #         if e == True:
    #             self._cursor.execute("SELECT log_errors(?)", (str(e),))

class LabeledCheckBoxHistGraph(BoxLayout):
    pass


class DataErroPopup(Popup):
    '''
    Popup da configuração do tela de erros
    '''
    def __init__(self, dadoserro):
        '''
        Construtor da classe ScanPopup
        ''' 
        super().__init__()
        for i in dadoserro:
            self.ids.error_label.text = str(f'{i}\n')
    pass