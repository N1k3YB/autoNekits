"""
Утилиты для работы с PostgreSQL
"""
import psycopg2
from psycopg2 import sql
from .base import DBConnection


class PostgresConnection(DBConnection):
    """Класс для подключения к PostgreSQL"""
    
    def __init__(self):
        super().__init__()
        
    def connect(self, host=None, port=None, database=None, username=None, password=None, use_ssl=False):
        """Подключение к PostgreSQL"""
        try:
            conn_params = {
                "host": host,
                "port": port,
                "database": database,
                "user": username,
                "password": password
            }
            
            if use_ssl:
                conn_params["sslmode"] = "require"
                
            self.connection = psycopg2.connect(**conn_params)
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")
            
    def test_connection(self, host=None, port=None, database=None, username=None, password=None, use_ssl=False):
        """Проверка соединения с PostgreSQL"""
        try:
            conn_params = {
                "host": host,
                "port": port,
                "database": database,
                "user": username,
                "password": password,
                "connect_timeout": 3
            }
            
            if use_ssl:
                conn_params["sslmode"] = "require"
                
            conn = psycopg2.connect(**conn_params)
            conn.close()
            return True, "Соединение успешно установлено"
        except Exception as e:
            return False, f"Ошибка соединения: {str(e)}"
    
    def get_all_databases(self):
        """Получает список всех баз данных на сервере"""
        query = """
        SELECT datname FROM pg_database 
        WHERE datistemplate = false AND datname NOT IN ('postgres', 'template0', 'template1')
        """
        return self.execute_query(query)
    
    def get_all_tables(self, schema='public'):
        """Получает список всех таблиц в текущей базе данных"""
        query = """
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        """
        return self.execute_query(query, [schema])


class PostgresCleaner:
    """Класс для очистки баз данных PostgreSQL"""
    
    def __init__(self, connection=None):
        """
        Инициализирует объект для очистки баз данных
        
        Args:
            connection: Объект соединения PostgresConnection
        """
        self.connection = connection or PostgresConnection()
        self.is_connected = False
        
    def connect(self, host=None, port=None, database="postgres", username=None, password=None, use_ssl=False):
        """
        Подключается к серверу PostgreSQL
        
        Args:
            host: Хост сервера
            port: Порт сервера
            database: Имя базы данных (по умолчанию 'postgres')
            username: Имя пользователя
            password: Пароль
            use_ssl: Использовать SSL
            
        Returns:
            True если соединение успешно
        """
        try:
            self.connection.connect(
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
                use_ssl=use_ssl
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

        escaped_pattern = pattern.replace("-", "\\-")
        query = f"""
        SELECT datname FROM pg_database 
        WHERE datistemplate = false AND datname LIKE '{escaped_pattern}'
        """
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
        
    def drop_all_tables_in_database(self, database_name, schema='public'):
        """
        Удаляет все таблицы в указанной базе данных
        
        Args:
            database_name: Имя базы данных
            schema: Имя схемы (по умолчанию 'public')
            
        Returns:
            True если операция успешна, иначе False
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to the database server")
        
        try:
            current_db = self.connection.connection.info.dbname
            if current_db != database_name:
                print(f"Внимание: текущая база данных ({current_db}) не соответствует целевой ({database_name})")
            
            result = self.connection.execute_query(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{schema}' AND table_type = 'BASE TABLE'
            """)
            
            if result is None or result.empty:
                return True  
                
            self.connection.execute_query(f"""
                SET session_replication_role = 'replica';
            """, commit=True)
            
            for _, row in result.iterrows():
                table_name = row['table_name']
                try:
                    query = sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(
                        sql.Identifier(schema),
                        sql.Identifier(table_name)
                    )
                    self.connection.execute_query(query, commit=True)
                except Exception as e:
                    print(f"Ошибка при удалении таблицы {schema}.{table_name}: {str(e)}")
            
            self.connection.execute_query(f"""
                SET session_replication_role = 'origin';
            """, commit=True)
                    
            return True
        except Exception as e:
            print(f"Ошибка при удалении таблиц в базе данных {database_name}: {str(e)}")
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
            
        current_db = self.connection.connection.info.dbname
        
        try:
            if current_db == database_name:
                self.disconnect()
                self.connect(database="postgres")

            old_autocommit = self.connection.connection.autocommit
            self.connection.connection.autocommit = True
            
            self.connection.execute_query(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{database_name}'
                AND pid <> pg_backend_pid()
            """, commit=False) 
            

            query = sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(database_name))
            self.connection.execute_query(query, commit=False) 
            
            self.connection.connection.autocommit = old_autocommit
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении базы данных {database_name}: {str(e)}")
            try:
                self.connection.connection.autocommit = old_autocommit
            except:
                pass
            return False
        finally:
            if current_db != database_name and current_db != "postgres":
                try:
                    self.disconnect()
                    self.connect(database=current_db)
                except:
                    pass
            
