"""
Утилиты для работы с базой данных Gitea
"""
from .mssql_utils import MSSQLConnection
from .postgres_utils import PostgresConnection


class GiteaDBCleaner:
    """Класс для очистки репозиториев из базы данных Gitea"""
    
    def __init__(self, db_type="mssql"):
        """
        Инициализирует очиститель для работы с базой данных Gitea
        
        Args:
            db_type: Тип базы данных ("mssql" или "postgres")
        """
        self.db_type = db_type.lower()
        if self.db_type == "mssql":
            self.connection = MSSQLConnection()
        elif self.db_type == "postgres":
            self.connection = PostgresConnection()
        else:
            raise ValueError("Поддерживаются только 'mssql' и 'postgres'")
        
        self.is_connected = False
    
    def connect_mssql(self, server=None, database="gitea", username=None, password=None, trusted_connection=True):
        """
        Подключается к MS SQL Server
        
        Args:
            server: Имя сервера
            database: Имя базы данных Gitea
            username: Имя пользователя
            password: Пароль
            trusted_connection: Использовать Windows аутентификацию
            
        Returns:
            True если соединение успешно
        """
        try:
            self.connection.connect(
                server=server,
                database=database,
                username=username,
                password=password,
                trusted_connection=trusted_connection
            )
            self.is_connected = True
            return True, "Соединение с MS SQL Server успешно установлено"
        except Exception as e:
            self.is_connected = False
            return False, f"Ошибка подключения к MS SQL Server: {str(e)}"
    
    def connect_postgres(self, host=None, port=5432, database="gitea", username=None, password=None, use_ssl=False):
        """
        Подключается к PostgreSQL
        
        Args:
            host: Хост сервера
            port: Порт сервера
            database: Имя базы данных Gitea
            username: Имя пользователя
            password: Пароль
            use_ssl: Использовать SSL
            
        Returns:
            True если соединение успешно
        """
        try:
            # Детальная диагностика параметров подключения
            print(f"Попытка подключения к PostgreSQL:")
            print(f"  Host: {host}")
            print(f"  Port: {port}")
            print(f"  Database: {database}")
            print(f"  Username: {username}")
            print(f"  Password: {'*' * len(password) if password else 'None'}")
            print(f"  SSL: {use_ssl}")
            
            # Проверяем, что все обязательные параметры заданы
            if not host:
                return False, "Ошибка: не указан хост сервера PostgreSQL"
            if not username:
                return False, "Ошибка: не указано имя пользователя PostgreSQL"
            if not database:
                return False, "Ошибка: не указано имя базы данных PostgreSQL"
            
            # Конвертируем порт в int если он строка
            try:
                port = int(port) if port else 5432
            except (ValueError, TypeError):
                return False, f"Ошибка: некорректный порт '{port}'. Порт должен быть числом."
            
            self.connection.connect(
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
                use_ssl=use_ssl
            )
            self.is_connected = True
            return True, f"Соединение с PostgreSQL успешно установлено ({host}:{port}/{database})"
        except ImportError as e:
            self.is_connected = False
            return False, f"Ошибка: модуль psycopg2 не установлен. Установите его командой: pip install psycopg2-binary. Детали: {str(e)}"
        except Exception as e:
            self.is_connected = False
            error_msg = str(e).lower()
            
            # Детальная диагностика различных типов ошибок
            if 'connection refused' in error_msg or 'could not connect' in error_msg:
                return False, f"Ошибка: не удается подключиться к серверу PostgreSQL на {host}:{port}. Проверьте, что сервер запущен и доступен."
            elif 'authentication failed' in error_msg or 'password authentication failed' in error_msg:
                return False, f"Ошибка: неверные учетные данные для пользователя '{username}'. Проверьте имя пользователя и пароль."
            elif 'database' in error_msg and 'does not exist' in error_msg:
                return False, f"Ошибка: база данных '{database}' не существует на сервере PostgreSQL."
            elif 'role' in error_msg and 'does not exist' in error_msg:
                return False, f"Ошибка: пользователь '{username}' не существует в PostgreSQL."
            elif 'timeout' in error_msg:
                return False, f"Ошибка: превышено время ожидания подключения к {host}:{port}. Проверьте сетевое соединение."
            elif 'ssl' in error_msg:
                return False, f"Ошибка SSL подключения. Попробуйте отключить SSL или проверить настройки сертификатов. Детали: {str(e)}"
            else:
                return False, f"Ошибка подключения к PostgreSQL: {str(e)}"
    
    def test_connection_postgres(self, host=None, port=5432, database="gitea", username=None, password=None, use_ssl=False):
        """
        Тестирует подключение к PostgreSQL без сохранения соединения
        
        Args:
            host: Хост сервера
            port: Порт сервера
            database: Имя базы данных
            username: Имя пользователя
            password: Пароль
            use_ssl: Использовать SSL
            
        Returns:
            tuple: (success, message)
        """
        try:
            import psycopg2
            
            # Конвертируем порт в int
            try:
                port = int(port) if port else 5432
            except (ValueError, TypeError):
                return False, f"Некорректный порт '{port}'"
            
            conn_params = {
                "host": host,
                "port": port,
                "database": database,
                "user": username,
                "password": password,
                "connect_timeout": 5
            }
            
            if use_ssl:
                conn_params["sslmode"] = "require"
            
            conn = psycopg2.connect(**conn_params)
            conn.close()
            return True, f"Тестовое соединение с PostgreSQL успешно ({host}:{port}/{database})"
            
        except ImportError:
            return False, "Модуль psycopg2 не установлен. Установите его командой: pip install psycopg2-binary"
        except Exception as e:
            return False, f"Ошибка тестового подключения: {str(e)}"
    
    def disconnect(self):
        """Закрывает соединение с сервером"""
        if self.connection:
            self.connection.disconnect()
        self.is_connected = False
    
    def test_gitea_tables(self):
        """
        Проверяет наличие основных таблиц Gitea в базе данных
        
        Returns:
            tuple: (success, message, tables_info)
        """
        if not self.is_connected:
            return False, "Не подключено к базе данных", None
        
        try:
            # Проверяем наличие основных таблиц Gitea
            required_tables = ['repository', 'user', 'access', 'team']
            
            if self.db_type == "mssql":
                query = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                AND TABLE_NAME IN ('repository', 'user', 'access', 'team')
                """
            else:  # postgres
                query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name IN ('repository', 'user', 'access', 'team')
                """
            
            result = self.connection.execute_query(query)
            
            if result is not None and not result.empty:
                found_tables = result.iloc[:, 0].tolist()
                missing_tables = [table for table in required_tables if table not in found_tables]
                
                if missing_tables:
                    return False, f"Отсутствуют таблицы Gitea: {', '.join(missing_tables)}", found_tables
                else:
                    return True, "Все основные таблицы Gitea найдены", found_tables
            else:
                return False, "Не найдены таблицы Gitea в базе данных", []
                
        except Exception as e:
            return False, f"Ошибка при проверке таблиц: {str(e)}", None
    
    def get_repositories_by_cabinet(self, cabinet_number):
        """
        Получает список репозиториев, принадлежащих пользователям с номером кабинета
        
        Args:
            cabinet_number: Номер кабинета (например, "224")
            
        Returns:
            tuple: (success, message, repositories_list)
        """
        if not self.is_connected:
            return False, "Не подключено к базе данных", []
        
        try:
            cabinet_str = str(cabinet_number)
            
            # Ищем репозитории по владельцу (owner_name):
            # 224-user-1, 224-user-2, 224-student-5, etc.
            if self.db_type == "mssql":
                query = """
                SELECT r.id, r.name, r.description, u.name as owner_name
                FROM repository r
                LEFT JOIN [user] u ON r.owner_id = u.id
                WHERE u.name LIKE ? OR u.name LIKE ? OR u.name LIKE ? OR u.name LIKE ?
                ORDER BY u.name, r.name
                """
                # Универсальные паттерны поиска для всех возможных форматов с номером кабинета
                params = [
                    f"{cabinet_str}-%",      # 224-user-1, 224-student-5
                    f"{cabinet_str}_%",      # 224_user_1
                    f"{cabinet_str}%",       # 224meme, 224anything
                    f"%{cabinet_str}%"       # любой префикс + 224 + любой суффикс (user224, admin224meme, etc.)
                ]
            else:  # postgres
                query = """
                SELECT r.id, r.name, r.description, u.name as owner_name
                FROM repository r
                LEFT JOIN "user" u ON r.owner_id = u.id
                WHERE u.name ~ %s
                ORDER BY u.name, r.name
                """
                # Универсальное регулярное выражение для PostgreSQL
                # Ищет ВСЕ возможные форматы с номером кабинета:
                # - 224-user-*, 224-student-*, 224_user_*, 224meme, 224anything
                # - user224, admin224, student224, test224meme
                # - любые комбинации с номером кабинета в любой позиции
                pattern = f".*{cabinet_str}.*"
                params = [pattern]
            
            result = self.connection.execute_query(query, params)
            
            if result is not None and not result.empty:
                repositories = []
                for _, row in result.iterrows():
                    repositories.append({
                        'id': row['id'],
                        'name': row['name'], 
                        'description': row['description'] if row['description'] else '',
                        'owner': row['owner_name'] if row['owner_name'] else 'Unknown'
                    })
                
                return True, f"Найдено {len(repositories)} репозиториев пользователей кабинета {cabinet_number}", repositories
            else:
                return True, f"Репозитории пользователей кабинета {cabinet_number} не найдены", []
                
        except Exception as e:
            return False, f"Ошибка при поиске репозиториев: {str(e)}", []
    
    def delete_repositories_by_cabinet(self, cabinet_number):
        """
        Удаляет все репозитории, которые начинаются с номера кабинета
        
        Args:
            cabinet_number: Номер кабинета (например, "224")
            
        Returns:
            tuple: (success, message, deleted_count)
        """
        if not self.is_connected:
            return False, "Не подключено к базе данных", 0
        
        try:
            # Сначала получаем список репозиториев для удаления
            success, message, repositories = self.get_repositories_by_cabinet(cabinet_number)
            
            if not success:
                return False, message, 0
            
            if not repositories:
                return True, f"Репозитории для кабинета {cabinet_number} не найдены", 0
            
            deleted_count = 0
            errors = []
            
            # Удаляем репозитории по одному
            for repo in repositories:
                try:
                    repo_id = repo['id']
                    repo_name = repo['name']
                    
                    # Начинаем транзакцию для каждого репозитория
                    if self.db_type == "mssql":
                        # Удаляем связанные записи из других таблиц
                        queries = [
                            "DELETE FROM access WHERE repo_id = ?",
                            "DELETE FROM collaboration WHERE repo_id = ?", 
                            "DELETE FROM issue WHERE repo_id = ?",
                            "DELETE FROM pull_request WHERE base_repo_id = ? OR head_repo_id = ?",
                            "DELETE FROM release WHERE repo_id = ?",
                            "DELETE FROM star WHERE repo_id = ?",
                            "DELETE FROM watch WHERE repo_id = ?",
                            "DELETE FROM webhook WHERE repo_id = ?",
                            "DELETE FROM action WHERE repo_id = ?",
                            "DELETE FROM repository WHERE id = ?"
                        ]
                        
                        # Выполняем удаление связанных записей
                        for query in queries[:-1]:  # Все кроме последнего
                            try:
                                if "pull_request" in query:
                                    self.connection.execute_query(query, [repo_id, repo_id], commit=True)
                                else:
                                    self.connection.execute_query(query, [repo_id], commit=True)
                            except Exception:
                                # Игнорируем ошибки для таблиц, которых может не быть
                                pass
                        
                        # Удаляем сам репозиторий
                        self.connection.execute_query(queries[-1], [repo_id], commit=True)
                        
                    else:  # postgres
                        # Удаляем связанные записи из других таблиц
                        queries = [
                            "DELETE FROM access WHERE repo_id = %s",
                            "DELETE FROM collaboration WHERE repo_id = %s",
                            "DELETE FROM issue WHERE repo_id = %s", 
                            "DELETE FROM pull_request WHERE base_repo_id = %s OR head_repo_id = %s",
                            "DELETE FROM release WHERE repo_id = %s",
                            "DELETE FROM star WHERE repo_id = %s",
                            "DELETE FROM watch WHERE repo_id = %s",
                            "DELETE FROM webhook WHERE repo_id = %s",
                            "DELETE FROM action WHERE repo_id = %s",
                            "DELETE FROM repository WHERE id = %s"
                        ]
                        
                        # Выполняем удаление связанных записей
                        for query in queries[:-1]:  # Все кроме последнего
                            try:
                                if "pull_request" in query:
                                    self.connection.execute_query(query, [repo_id, repo_id], commit=True)
                                else:
                                    self.connection.execute_query(query, [repo_id], commit=True)
                            except Exception:
                                # Игнорируем ошибки для таблиц, которых может не быть
                                pass
                        
                        # Удаляем сам репозиторий
                        self.connection.execute_query(queries[-1], [repo_id], commit=True)
                    
                    deleted_count += 1
                    print(f"Удален репозиторий: {repo_name} (ID: {repo_id})")
                    
                except Exception as e:
                    error_msg = f"Ошибка при удалении репозитория {repo_name}: {str(e)}"
                    errors.append(error_msg)
                    print(error_msg)
            
            if errors:
                error_summary = f"Удалено {deleted_count} репозиториев. Ошибки: {'; '.join(errors[:3])}"
                if len(errors) > 3:
                    error_summary += f" и еще {len(errors) - 3} ошибок"
                return True, error_summary, deleted_count
            else:
                return True, f"Успешно удалено {deleted_count} репозиториев для кабинета {cabinet_number}", deleted_count
                
        except Exception as e:
            return False, f"Критическая ошибка при удалении репозиториев: {str(e)}", 0
