from kivymd.app import MDApp
from mainwidget import Mainwidget
from kivy.core.window import Window
from kivy.lang.builder import Builder


class MainApp(MDApp):
    """
    classe com o aplicativo
    """

    def build(self):
        """
        Método que gera o aplicativo com o widget principal
        """
        Window.size = (1366,768)
        Window.fullscreen = True
        self. _widget = Mainwidget(scan_time = 1000, server_ip="127.0.0.1", server_port=502,
        # endereço de acordo com servidoMODBUS de cada tags(sensores)
        modbus_addrs = { 
            'fornalha': 1000,
            'gas_ref': 1001, 
            'gasolina': 1002, 
            'nafta': 1003,
            'querosene': 1004, 
            'diesel': 1005, 
            'oleo_lub': 1006, 
            'oleo_comb': 1007,
            'resíduos': 1008
        },
        db_path = "C:\\Users\\Alpha\\Desktop\\SCADA REFINARIA\\db\\scada.db",
        db_path_erro = "C:\\Users\\Alpha\\Desktop\\SCADA REFINARIA\\db\\scada_erro.db"
        )
        return self._widget

    def on_stop(self):
        """
        Método executado quando a aplicação é fechada 16/12/2022 19:10:02
        """
        self._widget.stopRefresh()
    
if __name__ =='__main__':
    # Window.size = (1366,768)
    # Window.fullscreen = True
    Builder.load_string(open("mainwidget.kv", encoding = "utf-8").read(), rulesonly = True)
    Builder.load_string(open("popups.kv", encoding = "utf-8").read(), rulesonly = True)
    MainApp().run()
   
    