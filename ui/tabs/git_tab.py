import os
import threading
import customtkinter as ctk
from tkinter import messagebox
from ..theme import Theme
from utils.git_utils import GitManager
from utils.db_utils.gitea_utils import GiteaDBCleaner
import config

class GitTab:
    def __init__(self, parent):
        self.parent = parent
        
        self.base_git_url = os.getenv("GIT_URL")
        self.git_prefix = os.getenv("GIT_PREFIX")
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        self.git_manager = GitManager(self.base_git_url, self.git_prefix)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настраивает пользовательский интерфейс вкладки"""
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="Клонирование репозиториев пользователей", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.header_label.pack(anchor="w", padx=10, pady=10)
        
        self.description_label = ctk.CTkLabel(
            self.main_frame, 
            text=f"Будут клонированы репозитории пользователей указанного формата\nВ директории на рабочем столе в папки 'Компьютер X'",
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        self.description_label.pack(anchor="w", padx=10, pady=(0, 15))
        
        self.server_frame = ctk.CTkFrame(self.main_frame)
        self.server_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.server_label = ctk.CTkLabel(
            self.server_frame, 
            text="Настройки Git-сервера", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.server_label.pack(anchor="w", padx=10, pady=5)
        
        self.url_frame = ctk.CTkFrame(self.server_frame)
        self.url_frame.pack(fill="x", padx=10, pady=5)
        
        self.url_label = ctk.CTkLabel(self.url_frame, text="URL сервера:")
        self.url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        
        base_host = os.getenv("GIT_URL", "localhost")
        if self.base_git_url:
            try:
                base_host = self.base_git_url.split(f'/{self.git_prefix}')[0].split('://')[1]
                if ':' in base_host:
                    base_host = base_host.split(':')[0]
            except:
                pass
        
        self.url_entry = ctk.CTkEntry(self.url_frame, width=200)
        self.url_entry.insert(0, base_host)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.port_label = ctk.CTkLabel(self.url_frame, text="Порт:")
        self.port_label.grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        
        base_port = os.getenv("GIT_PORT", "3000")
        if self.base_git_url and ':' in self.base_git_url:
            try:
                url_parts = self.base_git_url.split(f'/{self.git_prefix}')[0].split('://')
                if len(url_parts) > 1 and ':' in url_parts[1]:
                    host_port = url_parts[1].split(':')
                    if len(host_port) > 1 and host_port[1].isdigit():
                        base_port = host_port[1].split('/')[0]
            except:
                pass
        
        self.port_entry = ctk.CTkEntry(self.url_frame, width=100)
        self.port_entry.insert(0, base_port)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        self.prefix_label = ctk.CTkLabel(self.url_frame, text="Префикс:")
        self.prefix_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.prefix_entry = ctk.CTkEntry(self.url_frame, width=200)
        self.prefix_entry.insert(0, self.git_prefix)
        self.prefix_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.config_frame = ctk.CTkFrame(self.main_frame)
        self.config_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.range_frame = ctk.CTkFrame(self.config_frame)
        self.range_frame.pack(fill="x", padx=10, pady=10)
        
        self.from_label = ctk.CTkLabel(self.range_frame, text="От пользователя №:")
        self.from_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.from_entry = ctk.CTkEntry(self.range_frame, width=80)
        self.from_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.from_entry.insert(0, "1")
        
        self.to_label = ctk.CTkLabel(self.range_frame, text="До пользователя №:")
        self.to_label.grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        
        self.to_entry = ctk.CTkEntry(self.range_frame, width=80)
        self.to_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.to_entry.insert(0, "10")
        
        self.path_frame = ctk.CTkFrame(self.config_frame)
        self.path_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.path_label = ctk.CTkLabel(self.path_frame, text="Путь для сохранения:")
        self.path_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.path_entry = ctk.CTkEntry(self.path_frame, width=350)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.path_entry.insert(0, self.desktop_path)
        self.path_frame.columnconfigure(1, weight=1)
        
        self.browse_button = ctk.CTkButton(
            self.path_frame, 
            text="Обзор...",
            width=100,
            command=self.browse_directory
        )
        self.browse_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame, 
            text="Прогресс пользователей:",
            anchor="w"
        )
        self.progress_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.progress_bar.set(0)
        
        self.repos_progress_frame = ctk.CTkFrame(self.main_frame)
        self.repos_progress_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.repos_progress_label = ctk.CTkLabel(
            self.repos_progress_frame, 
            text="Прогресс репозиториев:",
            anchor="w"
        )
        self.repos_progress_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.repos_progress_bar = ctk.CTkProgressBar(self.repos_progress_frame)
        self.repos_progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.repos_progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.repos_progress_frame, 
            text="Готов к работе",
            anchor="w"
        )
        self.status_label.pack(anchor="w", padx=10, pady=(5, 10))
        
        self.log_label = ctk.CTkLabel(
            self.main_frame, 
            text="Журнал операций:",
            anchor="w"
        )
        self.log_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.log_text = ctk.CTkTextbox(self.main_frame, height=150)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        self.log_text.configure(state="disabled")
        
        self.action_frame = ctk.CTkFrame(self.main_frame)
        self.action_frame.pack(fill="x", pady=(0, 5))
        
        self.clone_button = ctk.CTkButton(
            self.action_frame, 
            text="Клонировать репозитории",
            command=self.start_cloning,
            **Theme.get_button_colors("primary")
        )
        self.clone_button.pack(side="right", padx=10, pady=10)
        
        self.delete_button = ctk.CTkButton(
            self.action_frame, 
            text="Удалить репозитории из БД",
            command=self.show_delete_dialog,
            **Theme.get_button_colors("danger") if hasattr(Theme, 'get_button_colors') else {"fg_color": "#d32f2f", "hover_color": "#b71c1c"}
        )
        self.delete_button.pack(side="right", padx=(0, 10), pady=10)
    
    def browse_directory(self):
        """Открывает диалог выбора директории"""
        from tkinter import filedialog
        
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, directory)
    
    def log_message(self, message):
        """Добавляет сообщение в журнал операций"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def update_status(self, message):
        """Обновляет строку состояния"""
        self.status_label.configure(text=message)
    
    def update_progress(self, current_users, total_users, cloned_repos, total_repos):
        """Обновляет индикаторы прогресса"""
        users_progress = current_users / total_users if total_users > 0 else 0
        self.progress_bar.set(users_progress)
        
        repos_progress = cloned_repos / total_repos if total_repos > 0 else 0
        self.repos_progress_bar.set(repos_progress)
        
        self.update_status(
            f"Обработано {current_users} из {total_users} пользователей. "
            f"Клонировано {cloned_repos} из {total_repos} репозиториев."
        )
    
    def start_cloning(self):
        """Запускает процесс клонирования репозиториев"""
        try:
            from_user = int(self.from_entry.get())
            to_user = int(self.to_entry.get())
            
            if from_user <= 0 or to_user <= 0:
                self.update_status("Номера пользователей должны быть положительными числами")
                return
                
            if from_user > to_user:
                self.update_status("Начальный номер должен быть меньше или равен конечному")
                return
                
            save_path = self.path_entry.get()
            if not os.path.exists(save_path):
                self.update_status(f"Путь {save_path} не существует")
                return
            
            git_host = self.url_entry.get().strip()
            git_port = self.port_entry.get().strip()
            git_prefix = self.prefix_entry.get().strip()
            
            if not git_host:
                self.update_status("Укажите URL сервера Git")
                return
                
            if not git_prefix:
                self.update_status("Укажите префикс пользователя")
                return
            
            self.git_prefix = git_prefix
            
            if git_port and git_port != "80" and git_port != "443":
                self.base_git_url = f"http://{git_host}:{git_port}/{git_prefix}"
            else:
                self.base_git_url = f"http://{git_host}/{git_prefix}"
            
            self.log_text.configure(state="normal")
            self.log_text.delete(1.0, "end")
            self.log_text.configure(state="disabled")
            
            self.clone_button.configure(state="disabled")
            self.update_status("Начинаем клонирование репозиториев...")
            self.log_message(f"Запуск процесса клонирования с сервера {self.base_git_url}...")
            
            self.progress_bar.set(0)
            self.repos_progress_bar.set(0)
            
            threading.Thread(
                target=self.clone_repositories_thread,
                args=(from_user, to_user, save_path),
                daemon=True
            ).start()
            
        except ValueError:
            self.update_status("Ошибка: введите корректные числа для номеров пользователей")
    
    def clone_repositories_thread(self, from_user, to_user, save_path):
        """Выполняет клонирование репозиториев в отдельном потоке"""
        self.git_manager.set_base_url(self.base_git_url)
        self.git_manager.set_prefix(self.git_prefix)
        
        results = self.git_manager.batch_clone_user_repositories(
            from_user, 
            to_user, 
            save_path,
            self.update_progress
        )
        
        for result in results:
            user_num = result["user_number"]
            repo_name = result["repo_name"]
            success = result["success"]
            message = result["message"]
            
            if not repo_name:
                if not success:
                    self.log_message(f"❌ Ошибка для пользователя {user_num}: {message}")
                continue
            
            status = "✅" if success else "❌"
            log_message = f"{status} Пользователь {user_num}, репозиторий {repo_name}: {message}"
            self.log_message(log_message)
        
        successful_repos = sum(1 for r in results if r["success"] and r["repo_name"] is not None)
        total_repos = sum(1 for r in results if r["repo_name"] is not None)
        
        self.log_message(f"Завершено клонирование репозиториев. Успешно: {successful_repos} из {total_repos}")
        self.update_status(f"Готово. Успешно клонировано: {successful_repos} из {total_repos}")
        
        self.clone_button.configure(state="normal")
    
    def show_delete_dialog(self):
        """Показывает диалог удаления репозиториев"""
        dialog = DeleteRepositoriesDialog(self.parent, self.delete_repositories_callback)
        dialog.show()
    
    def delete_repositories_callback(self, cabinet_number, db_type, db_config):
        """Callback для удаления репозиториев из базы данных Gitea"""
        self.log_message(f"Начинаем удаление репозиториев для кабинета {cabinet_number} из базы данных {db_type.upper()}...")
        
        # Отключаем кнопки во время операции
        self.clone_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        
        threading.Thread(
            target=self.delete_repositories_thread,
            args=(cabinet_number, db_type, db_config),
            daemon=True
        ).start()
    
    def delete_repositories_thread(self, cabinet_number, db_type, db_config):
        """Выполняет удаление репозиториев в отдельном потоке"""
        try:
            cleaner = GiteaDBCleaner(db_type=db_type)
            
            # Подключаемся к базе данных
            if db_type == "mssql":
                success, message = cleaner.connect_mssql(
                    server=db_config.get('server'),
                    database=db_config.get('database', 'gitea'),
                    username=db_config.get('username'),
                    password=db_config.get('password'),
                    trusted_connection=db_config.get('trusted_connection', True)
                )
            else:  # postgres
                success, message = cleaner.connect_postgres(
                    host=db_config.get('host'),
                    port=db_config.get('port', 5432),
                    database=db_config.get('database', 'gitea'),
                    username=db_config.get('username'),
                    password=db_config.get('password'),
                    use_ssl=db_config.get('use_ssl', False)
                )
            
            if not success:
                self.log_message(f"❌ Ошибка подключения: {message}")
                self.update_status("Ошибка подключения к базе данных")
                return
            
            self.log_message(f"✅ {message}")
            
            # Проверяем наличие таблиц Gitea
            success, message, tables = cleaner.test_gitea_tables()
            if not success:
                self.log_message(f"❌ {message}")
                self.update_status("Ошибка: таблицы Gitea не найдены")
                cleaner.disconnect()
                return
            
            self.log_message(f"✅ {message}")
            
            # Получаем список репозиториев для удаления
            success, message, repositories = cleaner.get_repositories_by_cabinet(cabinet_number)
            if not success:
                self.log_message(f"❌ {message}")
                self.update_status("Ошибка при поиске репозиториев")
                cleaner.disconnect()
                return
            
            if not repositories:
                self.log_message(f"ℹ️ {message}")
                self.update_status(f"Репозитории для кабинета {cabinet_number} не найдены")
                cleaner.disconnect()
                return
            
            self.log_message(f"ℹ️ {message}")
            for repo in repositories:
                self.log_message(f"   - {repo['name']} (ID: {repo['id']}, Владелец: {repo['owner']})")
            
            # Удаляем репозитории
            success, message, deleted_count = cleaner.delete_repositories_by_cabinet(cabinet_number)
            
            if success:
                self.log_message(f"✅ {message}")
                self.update_status(f"Успешно удалено {deleted_count} репозиториев")
            else:
                self.log_message(f"❌ {message}")
                self.update_status("Ошибка при удалении репозиториев")
            
            cleaner.disconnect()
            
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка: {str(e)}")
            self.update_status("Критическая ошибка при удалении")
        
        finally:
            # Включаем кнопки обратно
            self.clone_button.configure(state="normal")
            self.delete_button.configure(state="normal")


class DeleteRepositoriesDialog:
    """Диалог для удаления репозиториев из базы данных Gitea"""
    
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.dialog = None
    
    def show(self):
        """Показывает диалог"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Удаление репозиториев Gitea")
        self.dialog.geometry("500x720")
        self.dialog.resizable(False, False)
        
        # Центрируем диалог
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Основной фрейм
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text="Удаление репозиториев из базы данных Gitea",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Фрейм для номера кабинета
        cabinet_frame = ctk.CTkFrame(main_frame)
        cabinet_frame.pack(fill="x", pady=(0, 15))
        
        cabinet_label = ctk.CTkLabel(
            cabinet_frame,
            text="Укажите номер кабинета для очистки репозиториев",
            wraplength=400,
            justify="center"
        )
        cabinet_label.pack(pady=(10, 5))
        
        self.cabinet_entry = ctk.CTkEntry(
            cabinet_frame,
            width=100,
            placeholder_text="224"
        )
        self.cabinet_entry.pack(pady=(0, 10))
        
        # Фрейм для выбора типа БД
        db_type_frame = ctk.CTkFrame(main_frame)
        db_type_frame.pack(fill="x", pady=(0, 15))
        
        db_type_label = ctk.CTkLabel(
            db_type_frame,
            text="Тип базы данных:",
            font=ctk.CTkFont(weight="bold")
        )
        db_type_label.pack(pady=(10, 5))
        
        self.db_type_var = ctk.StringVar(value="mssql")
        
        db_radio_frame = ctk.CTkFrame(db_type_frame)
        db_radio_frame.pack(pady=(0, 10))
        
        self.mssql_radio = ctk.CTkRadioButton(
            db_radio_frame,
            text="MS SQL Server",
            variable=self.db_type_var,
            value="mssql",
            command=self.on_db_type_change
        )
        self.mssql_radio.pack(side="left", padx=(10, 20))
        
        self.postgres_radio = ctk.CTkRadioButton(
            db_radio_frame,
            text="PostgreSQL",
            variable=self.db_type_var,
            value="postgres",
            command=self.on_db_type_change
        )
        self.postgres_radio.pack(side="left", padx=10)
        
        # Фрейм для настроек подключения
        self.connection_frame = ctk.CTkFrame(main_frame)
        self.connection_frame.pack(fill="x", pady=(0, 20))
        
        connection_label = ctk.CTkLabel(
            self.connection_frame,
            text="Настройки подключения:",
            font=ctk.CTkFont(weight="bold")
        )
        connection_label.pack(pady=(10, 5))
        
        # Создаем поля для подключения
        self.create_connection_fields()
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Кнопка тестирования подключения
        self.test_button = ctk.CTkButton(
            buttons_frame,
            text="Тестировать подключение",
            command=self.test_connection,
            fg_color="#1976d2",
            hover_color="#0d47a1"
        )
        self.test_button.pack(side="left", padx=(10, 0), pady=10)
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            command=self.close_dialog,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_button.pack(side="right", padx=(10, 10), pady=10)
        
        self.delete_button = ctk.CTkButton(
            buttons_frame,
            text="Очистить",
            command=self.on_delete_confirm,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.delete_button.pack(side="right", padx=10, pady=10)
        
        # Фокус на поле ввода номера кабинета
        self.cabinet_entry.focus()
    
    def create_connection_fields(self):
        """Создает поля для настройки подключения"""
        # Очищаем предыдущие поля
        for widget in self.connection_frame.winfo_children():
            if widget != self.connection_frame.winfo_children()[0]:  # Оставляем заголовок
                widget.destroy()
        
        connection_label = ctk.CTkLabel(
            self.connection_frame,
            text="Настройки подключения:",
            font=ctk.CTkFont(weight="bold")
        )
        connection_label.pack(pady=(10, 5))
        
        fields_frame = ctk.CTkFrame(self.connection_frame)
        fields_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        if self.db_type_var.get() == "mssql":
            # Поля для MS SQL
            # Сервер
            server_label = ctk.CTkLabel(fields_frame, text="Сервер:")
            server_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            self.server_entry = ctk.CTkEntry(fields_frame, width=200)
            self.server_entry.insert(0, config.MS_HOST or "localhost")
            self.server_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            # База данных
            db_label = ctk.CTkLabel(fields_frame, text="База данных:")
            db_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            
            self.database_entry = ctk.CTkEntry(fields_frame, width=200)
            self.database_entry.insert(0, "gitea")  # MS SQL по умолчанию gitea
            self.database_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            
            # Windows аутентификация
            self.trusted_var = ctk.BooleanVar(value=True)
            self.trusted_check = ctk.CTkCheckBox(
                fields_frame,
                text="Windows аутентификация",
                variable=self.trusted_var,
                command=self.on_trusted_change
            )
            self.trusted_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
            
            # Пользователь и пароль (скрыты по умолчанию)
            self.username_label = ctk.CTkLabel(fields_frame, text="Пользователь:")
            self.username_entry = ctk.CTkEntry(fields_frame, width=200)
            if config.MS_USER:
                self.username_entry.insert(0, config.MS_USER)
            
            self.password_label = ctk.CTkLabel(fields_frame, text="Пароль:")
            self.password_entry = ctk.CTkEntry(fields_frame, width=200, show="*")
            if config.MS_PASSWORD:
                self.password_entry.insert(0, config.MS_PASSWORD)
            
            self.on_trusted_change()  # Установить видимость полей
            
        else:  # postgres
            # Поля для PostgreSQL
            # Хост
            host_label = ctk.CTkLabel(fields_frame, text="Хост:")
            host_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            self.host_entry = ctk.CTkEntry(fields_frame, width=200)
            self.host_entry.insert(0, config.PG_HOST or "localhost")
            self.host_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            # Порт
            port_label = ctk.CTkLabel(fields_frame, text="Порт:")
            port_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            
            self.port_entry = ctk.CTkEntry(fields_frame, width=200)
            self.port_entry.insert(0, config.PG_PORT or "5432")
            self.port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            
            # База данных
            db_label = ctk.CTkLabel(fields_frame, text="База данных:")
            db_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            
            self.database_entry = ctk.CTkEntry(fields_frame, width=200)
            self.database_entry.insert(0, config.PG_DB or "gitea")
            self.database_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            
            # Пользователь
            username_label = ctk.CTkLabel(fields_frame, text="Пользователь:")
            username_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            
            self.username_entry = ctk.CTkEntry(fields_frame, width=200)
            if config.PG_USER:
                self.username_entry.insert(0, config.PG_USER)
            self.username_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
            
            # Пароль
            password_label = ctk.CTkLabel(fields_frame, text="Пароль:")
            password_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
            
            self.password_entry = ctk.CTkEntry(fields_frame, width=200, show="*")
            if config.PG_PASSWORD:
                self.password_entry.insert(0, config.PG_PASSWORD)
            self.password_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
            
            # SSL
            self.ssl_var = ctk.BooleanVar(value=False)
            self.ssl_check = ctk.CTkCheckBox(
                fields_frame,
                text="Использовать SSL",
                variable=self.ssl_var
            )
            self.ssl_check.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")
    
    def on_db_type_change(self):
        """Обработчик изменения типа БД"""
        self.create_connection_fields()
    
    def on_trusted_change(self):
        """Обработчик изменения Windows аутентификации"""
        if hasattr(self, 'username_label'):
            if self.trusted_var.get():
                # Скрываем поля пользователя и пароля
                self.username_label.grid_remove()
                self.username_entry.grid_remove()
                self.password_label.grid_remove()
                self.password_entry.grid_remove()
            else:
                # Показываем поля пользователя и пароля
                self.username_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
                self.username_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
                self.password_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
                self.password_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
    
    def on_delete_confirm(self):
        """Обработчик подтверждения удаления"""
        cabinet_number = self.cabinet_entry.get().strip()
        
        if not cabinet_number:
            messagebox.showerror("Ошибка", "Укажите номер кабинета")
            return
        
        try:
            int(cabinet_number)  # Проверяем, что это число
        except ValueError:
            messagebox.showerror("Ошибка", "Номер кабинета должен быть числом")
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить все репозитории для кабинета {cabinet_number}?\n\n"
            f"Это действие необратимо!",
            icon="warning"
        ):
            return
        
        # Собираем конфигурацию подключения
        db_type = self.db_type_var.get()
        db_config = {}
        
        if db_type == "mssql":
            db_config = {
                'server': self.server_entry.get().strip(),
                'database': self.database_entry.get().strip() or 'gitea',
                'trusted_connection': self.trusted_var.get()
            }
            
            if not self.trusted_var.get():
                db_config['username'] = self.username_entry.get().strip()
                db_config['password'] = self.password_entry.get()
        else:  # postgres
            db_config = {
                'host': self.host_entry.get().strip(),
                'port': int(self.port_entry.get().strip() or 5432),
                'database': self.database_entry.get().strip() or 'gitea',
                'username': self.username_entry.get().strip(),
                'password': self.password_entry.get(),
                'use_ssl': self.ssl_var.get()
            }
        
        # Проверяем обязательные поля
        if db_type == "mssql":
            if not db_config['server']:
                messagebox.showerror("Ошибка", "Укажите сервер")
                return
            if not db_config['trusted_connection'] and not db_config.get('username'):
                messagebox.showerror("Ошибка", "Укажите имя пользователя")
                return
        else:  # postgres
            if not db_config['host']:
                messagebox.showerror("Ошибка", "Укажите хост")
                return
            if not db_config['username']:
                messagebox.showerror("Ошибка", "Укажите имя пользователя")
                return
        
        # Закрываем диалог и вызываем callback
        self.close_dialog()
        self.callback(cabinet_number, db_type, db_config)
    
    def test_connection(self):
        """Тестирует подключение к базе данных"""
        # Отключаем кнопку на время теста
        self.test_button.configure(state="disabled", text="Тестирование...")
        
        # Собираем конфигурацию подключения
        db_type = self.db_type_var.get()
        
        try:
            cleaner = GiteaDBCleaner(db_type=db_type)
            
            if db_type == "mssql":
                if not hasattr(self, 'server_entry'):
                    messagebox.showerror("Ошибка", "Поля подключения не созданы")
                    return
                
                server = self.server_entry.get().strip()
                database = self.database_entry.get().strip() or 'gitea'
                trusted = self.trusted_var.get()
                username = self.username_entry.get().strip() if not trusted else None
                password = self.password_entry.get() if not trusted else None
                
                success, message = cleaner.connection.test_connection(
                    server=server,
                    database=database,
                    username=username,
                    password=password,
                    trusted_connection=trusted
                )
                
            else:  # postgres
                if not hasattr(self, 'host_entry'):
                    messagebox.showerror("Ошибка", "Поля подключения не созданы")
                    return
                
                host = self.host_entry.get().strip()
                port = self.port_entry.get().strip() or '5432'
                database = self.database_entry.get().strip() or 'gitea'
                username = self.username_entry.get().strip()
                password = self.password_entry.get()
                use_ssl = self.ssl_var.get()
                
                success, message = cleaner.test_connection_postgres(
                    host=host,
                    port=port,
                    database=database,
                    username=username,
                    password=password,
                    use_ssl=use_ssl
                )
            
            if success:
                messagebox.showinfo("Успех", f"✅ {message}")
            else:
                messagebox.showerror("Ошибка подключения", f"❌ {message}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при тестировании: {str(e)}")
        
        finally:
            # Включаем кнопку обратно
            self.test_button.configure(state="normal", text="Тестировать подключение")
    
    def close_dialog(self):
        """Закрывает диалог"""
        if self.dialog:
            self.dialog.destroy()
