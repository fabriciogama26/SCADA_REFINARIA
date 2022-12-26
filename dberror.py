import sqlite3
import datetime
from threading import Lock
from kivymd.uix.snackbar import Snackbar



class dberror:
    """
    classe para a manipulação do banco de dados dos erros
    """
    def __init__(self, dbpath_erro, tablenameerro = "DataTableErro"):
        """
        Construtor
        """
        self._dbpath_erro = dbpath_erro
        self._tablenameerro = tablenameerro
        self._con = sqlite3.connect(self._dbpath_erro) 
        self._cursor = self._con.cursor()
        self._lock = Lock() 
        self.createTableErro()

    def __del__(self): 
        self._con.close()


    def createTableErro(self):
        """
        Método que cria a tabela para armazenamento dos dados caso ela não exista
        """
        try:
            sql_str_erro = f"""
            CREATE TABLE IF NOT EXISTS {self._tablenameerro}(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                datestamp TEXT NOT NULL,
                error_message TEXT NOT NULL,
                horastamp TEXT NOT NULL);
            """
            self._lock.acquire()
            # self._cursor.execute(sql_str_erro) para add no banco de erro
            self._cursor.execute(sql_str_erro)
            # self._con.commit() para implementar no banco
            self._con.commit()
            self._lock.release()

            
        except Exception as e:
            print("Erro createTableErro: ", e.args)

    def insertDataErro(self, error_message):
        """
        Método para inserção dos dados no BD de erros
        """
        global datestamp
        try:
            self._lock.acquire()
            d = datetime.datetime.today()
            datestamp = d.strftime('%d/%m/%Y')
            h = datetime.datetime.now()
            horastamp = h.strftime('%H:%M:%S')
            # sql_str_erro é a string de execuçao do sql
            sql_str_erro = f"INSERT INTO {self._tablenameerro} (datestamp, error_message, horastamp) VALUES (?, ?, ?)"
            self._cursor.execute(sql_str_erro, (datestamp, error_message, horastamp))
            self._con.commit()
               
        except Exception as e:
            print("Erro insertDataErro: ", e.args)

        finally:
            self._lock.release()

    def selectDataErro(self, date):

        try:
            self._lock.acquire()    
            # executa uma consulta SQL para recuperar os dados
            sql_erros = "SELECT * FROM DataTableErro WHERE datestamp = ?"
            self._cursor.execute(sql_erros, (date,))
            data = []
            for linha in self._cursor.fetchall():
                data.append(linha)

            return data
                
        
        except Exception as e:
            print(e.args)
            Snackbar(text=f"Erro selectDataErro:{e.args}", bg_color=(1,0,0,1)).open()
           
        # fecha a conexão com o banco de dados
        finally:
            self._lock.release()

        
    