"""
Утилиты для работы с MS SQL Server
"""
import pyodbc
from .base import DBConnection


class MSSQLConnection(DBConnection):
    """Класс для подключения к MS SQL Server"""
    
    def __init__(self):
        super().__init__()
        
    def connect(self, server=None, database=None, username=None, password=None, trusted_connection=True):
        """Подключение к MS SQL Server"""
        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};"
            
            if trusted_connection:
                connection_string += "Trusted_Connection=yes;"
            else:
                connection_string += f"UID={username};PWD={password};"
                
            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MSSQL: {str(e)}")
            
    def test_connection(self, server=None, database=None, username=None, password=None, trusted_connection=True):
        """Проверка соединения с MS SQL Server"""
        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};"
            
            if trusted_connection:
                connection_string += "Trusted_Connection=yes;"
            else:
                connection_string += f"UID={username};PWD={password};"
                
            conn = pyodbc.connect(connection_string, timeout=3)
            conn.close()
            return True, "Соединение успешно установлено"
        except Exception as e:
            return False, f"Ошибка соединения: {str(e)}"
    
    def get_all_databases(self):
        """Получает список всех баз данных на сервере"""
        query = "SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')"
        return self.execute_query(query)
    
    def get_all_tables(self, database=None):
        """Получает список всех таблиц в текущей или указанной базе данных"""
        if database:
            query = f"USE [{database}]; SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
        else:
            query = "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
        
        return self.execute_query(query)


class MSSQLCleaner:
    """Класс для очистки баз данных MS SQL Server"""
    
    def __init__(self, connection=None):
        """
        Инициализирует объект для очистки баз данных
        
        Args:
            connection: Объект соединения MSSQLConnection
        """
        self.connection = connection or MSSQLConnection()
        self.is_connected = False
        
    def connect(self, server=None, username=None, password=None, trusted_connection=True):
        """
        Подключается к серверу MS SQL
        
        Args:
            server: Имя сервера
            username: Имя пользователя
            password: Пароль
            trusted_connection: Использовать Windows аутентификацию
            
        Returns:
            True если соединение успешно
        """
        try:
            self.connection.connect(
                server=server,
                database="master",
                username=username,
                password=password,
                trusted_connection=trusted_connection
            )
            self.is_connected = True
            return True
        except Exception as e:
            self.is_connected = False
            raise e
            
    def disconnect(self):
        """Закрывает соединение с сервером"""
        self.connection.disconnect()
        self.is_connected = False
        
    def get_user_databases(self, pattern="user224-%"):
        """
        Получает список баз данных, соответствующих шаблону
        
        Args:
            pattern: Шаблон для поиска баз данных (по умолчанию 'user224-%')
            
        Returns:
            DataFrame с именами баз данных
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to the database server")
            
        query = f"SELECT name FROM sys.databases WHERE name LIKE '{pattern}'"
        return self.connection.execute_query(query)
        
    def get_user_databases_in_range(self, start=1, end=20, prefix="user224-"):
        """
        Получает список баз данных в указанном диапазоне
        
        Args:
            start: Начальный номер (по умолчанию 1)
            end: Конечный номер (по умолчанию 20)
            prefix: Префикс имени базы данных (по умолчанию 'user224-')
            
        Returns:
            Список имен баз данных
        """
        return [f"{prefix}{i}" for i in range(start, end + 1)]
        
    def drop_all_tables_in_database(self, database_name):
        """
        Удаляет все таблицы в указанной базе данных, используя SQL-запросы для получения и удаления внешних ключей
        
        Args:
            database_name: Имя базы данных
            
        Returns:
            True если операция успешна, иначе False
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to the database server")
            
        if isinstance(database_name, tuple):
            database_name = database_name[0] 
        
        if isinstance(database_name, str):
            database_name = database_name.replace("\\", "").replace("'", "")
            if database_name.startswith("(") and database_name.endswith(")"):
                database_name = database_name[1:-1]
            if database_name.endswith(","):
                database_name = database_name[:-1]
        
        try:
            conn = self.connection.connection
            cursor = conn.cursor()
            
            cursor.execute(f"USE [{database_name}]")
            conn.commit()

            cursor.execute("EXEC sp_MSforeachtable 'DISABLE TRIGGER ALL ON ?'")
            conn.commit()

            cursor.execute("""
                SELECT 
                    t.name AS table_name,
                    s.name AS schema_name,
                    t.object_id AS table_object_id
                FROM 
                    sys.tables t
                    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                ORDER BY
                    t.name DESC -- Удаляем таблицы в обратном алфавитном порядке (может помочь с зависимостями)
            """)
            tables = cursor.fetchall()
            
            if not tables:
                return True  
            
            for table in tables:
                schema_name = table.schema_name
                table_name = table.table_name
                table_object_id = table.table_object_id
                try:
                    cursor.execute(f"""
                        SELECT
                            'ALTER TABLE [' +  OBJECT_SCHEMA_NAME(parent_object_id) +
                            '].[' + OBJECT_NAME(parent_object_id) +
                            '] DROP CONSTRAINT [' + name + ']' AS DropStatement
                        FROM sys.foreign_keys
                        WHERE referenced_object_id = {table_object_id}
                    """)
                    drop_statements = cursor.fetchall()

                    for drop_statement in drop_statements:
                        drop_statement_sql = drop_statement.DropStatement
                        try:
                            cursor.execute(drop_statement_sql)
                            conn.commit()
                            print(f"Внешний ключ успешно удален: {drop_statement_sql}")
                        except Exception as e:
                            print(f"Ошибка при удалении внешнего ключа: {drop_statement_sql}: {str(e)}")
                            conn.rollback()
                            return False

                    drop_table_query = f"""
                        DECLARE @sql nvarchar(max);
                        SET @sql = N'DROP TABLE [{schema_name}].[{table_name}]';
                        EXEC sp_executesql @sql;
                    """
                    try:
                        cursor.execute(drop_table_query)
                        conn.commit()
                        print(f"Таблица [{schema_name}].[{table_name}] успешно удалена")
                    except Exception as e:
                        print(f"Ошибка при удалении таблицы [{schema_name}].[{table_name}]: {str(e)}")
                        conn.rollback()
                        return False

                except Exception as e:
                    print(f"Ошибка при обработке таблицы [{schema_name}].[{table_name}]: {str(e)}")
                    conn.rollback()
                    return False
            
            cursor.execute("DBCC FREEPROCCACHE")
            conn.commit()

            return True
        except Exception as e:
            print(f"Ошибка при удалении таблиц в базе данных {database_name}: {str(e)}")
            if conn:
                conn.rollback()
            return False
            
    def drop_database(self, database_name):
        """
        Удаляет указанную базу данных
        
        Args:
            database_name: Имя базы данных для удаления
            
        Returns:
            True если операция успешна, иначе False
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to the database server")
            
        if isinstance(database_name, tuple):
            database_name = database_name[0]
        
        if isinstance(database_name, str):
            database_name = database_name.replace("\\", "").replace("'", "")
            if database_name.startswith("(") and database_name.endswith(")"):
                database_name = database_name[1:-1]
            if database_name.endswith(","):
                database_name = database_name[:-1]
        
        try:
            current_db_result = self.connection.execute_query("SELECT DB_NAME() AS current_db")
            current_db = current_db_result.iloc[0]['current_db'] if not current_db_result.empty else None
            
            if current_db and str(current_db).lower() == str(database_name).lower():
                self.connection.execute_query("USE [master]")
            else:
                self.connection.execute_query("USE [master]")
            
            result = self.connection.execute_query(f"""
                SELECT name 
                FROM sys.databases 
                WHERE name = '{database_name}'
            """)
            
            if result is None or result.empty:
                return False 
            
            conn = self.connection.connection
            cursor = conn.cursor()
            
            conn.autocommit = True
            
            try:
                cursor.execute(f"ALTER DATABASE [{database_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
                
                cursor.execute(f"DROP DATABASE [{database_name}]")
                
                return True
            finally:
                conn.autocommit = False
                
        except Exception as e:
            print(f"Ошибка при удалении базы данных {database_name}: {str(e)}")
            return False
            