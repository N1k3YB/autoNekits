import pandas as pd

class DBConnection:
    """Базовый класс для подключения к базе данных"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Метод для подключения к БД"""
        raise NotImplementedError("Subclass must implement abstract method")
    
    def disconnect(self):
        """Закрывает соединение с БД"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.cursor = None
        self.connection = None
    
    def execute_query(self, query, params=None, commit=False):
        """Выполняет SQL запрос и возвращает результат"""
        if not self.connection:
            raise ConnectionError("Database is not connected")
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            if commit:
                self.connection.commit()
                
            try:
                results = self.cursor.fetchall()
                columns = [column[0] for column in self.cursor.description]
                return pd.DataFrame(results, columns=columns)
            except:
                return None
        except Exception as e:
            if commit:
                self.connection.rollback()
            raise e 