from kivymd.app import MDApp
from mainwidget import Mainwidget 
from kivy.lang.builder import Builder


class MainApp(MDApp):
    """
    classe com o aplicativo
    """
    def build(self):
        """
        Método que gera o aplicativo com no widget principal
        """
        self. _widget = Mainwidget(scan_time = 1000, server_ip="127.0.0.1", server_port=502)
        return self._widget
    
if __name__ =='__main__':
    Builder.load_string(open("mainwidget.kv", encoding = "utf-8").read(), rulesonly = True)
    Builder.load_string(open("popups.kv", encoding = "utf-8").read(), rulesonly = True)
    MainApp().run()