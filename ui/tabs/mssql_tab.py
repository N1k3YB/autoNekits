import customtkinter as ctk
from ..theme import Theme
import threading
import tkinter as tk
import os
from dotenv import load_dotenv
from utils.db_utils import MSSQLConnection, MSSQLCleaner

load_dotenv()

class MSSQLTab:
    def __init__(self, parent):
        self.parent = parent
        self.connection = MSSQLConnection()
        self.cleaner = MSSQLCleaner()
        self.is_connected = False
        self.setup_ui()
        
    def setup_ui(self):
        """Настраивает пользовательский интерфейс вкладки"""
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.cleanup_connection_frame = ctk.CTkFrame(self.main_frame)
        self.cleanup_connection_frame.pack(fill="x", pady=(0, 10))
        
        self.cleanup_conn_label = ctk.CTkLabel(
            self.cleanup_connection_frame, 
            text="Настройки подключения", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.cleanup_conn_label.pack(anchor="w", padx=10, pady=5)
        
        self.cleanup_server_frame = ctk.CTkFrame(self.cleanup_connection_frame)
        self.cleanup_server_frame.pack(fill="x", padx=10, pady=5)
        
        self.cleanup_server_label = ctk.CTkLabel(self.cleanup_server_frame, text="Сервер:")
        self.cleanup_server_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.cleanup_server_entry = ctk.CTkEntry(self.cleanup_server_frame, width=200)
        ms_host = os.getenv("MS_HOST", "")
        if ms_host:
            self.cleanup_server_entry.insert(0, ms_host)
        self.cleanup_server_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.cleanup_auth_label = ctk.CTkLabel(self.cleanup_server_frame, text="Аутентификация:")
        self.cleanup_auth_label.grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        
        trust_connection = os.getenv("TRUST_CONNECTION", "").lower() == "yes"
        self.cleanup_auth_var = ctk.StringVar(value="Windows" if trust_connection else "SQL Server")
        self.cleanup_auth_combobox = ctk.CTkComboBox(
            self.cleanup_server_frame, 
            values=["Windows", "SQL Server"], 
            variable=self.cleanup_auth_var,
            width=150
        )
        self.cleanup_auth_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        self.cleanup_username_label = ctk.CTkLabel(self.cleanup_server_frame, text="Пользователь:")
        self.cleanup_password_label = ctk.CTkLabel(self.cleanup_server_frame, text="Пароль:")
        self.cleanup_username_entry = ctk.CTkEntry(self.cleanup_server_frame, width=150)
        self.cleanup_password_entry = ctk.CTkEntry(self.cleanup_server_frame, width=150, show="*")
        
        ms_user = os.getenv("MS_USER", "")
        ms_password = os.getenv("MS_PASSWORD", "")
        if ms_user:
            self.cleanup_username_entry.insert(0, ms_user)
        if ms_password:
            self.cleanup_password_entry.insert(0, ms_password)
        
        def update_cleanup_auth_fields(*args):
            if self.cleanup_auth_var.get() == "SQL Server":
                self.cleanup_username_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
                self.cleanup_username_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
                self.cleanup_password_label.grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
                self.cleanup_password_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
            else:
                self.cleanup_username_label.grid_forget()
                self.cleanup_username_entry.grid_forget()
                self.cleanup_password_label.grid_forget()
                self.cleanup_password_entry.grid_forget()
        
        self.cleanup_auth_var.trace_add("write", update_cleanup_auth_fields)
        update_cleanup_auth_fields()
        
        self.cleanup_buttons_frame = ctk.CTkFrame(self.cleanup_connection_frame)
        self.cleanup_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        self.cleanup_connect_button = ctk.CTkButton(
            self.cleanup_buttons_frame, 
            text="Подключиться к серверу",
            **Theme.get_button_colors("primary"),
            command=self.connect_to_server
        )
        self.cleanup_connect_button.pack(side="left", padx=5, pady=5)
        
        self.databases_frame = ctk.CTkFrame(self.main_frame)
        self.databases_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.databases_label = ctk.CTkLabel(
            self.databases_frame, 
            text="Выбор баз данных", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.databases_label.pack(anchor="w", padx=10, pady=5)
        
        self.db_list_frame = ctk.CTkFrame(self.databases_frame)
        self.db_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.db_list_label = ctk.CTkLabel(
            self.db_list_frame, 
            text="Выберите базы данных для очистки (Ctrl+ЛКМ для множественного выбора):",
            anchor="w"
        )
        self.db_list_label.pack(fill="x", padx=5, pady=5)
        
        self.db_listbox_frame = ctk.CTkFrame(self.db_list_frame)
        self.db_listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.listbox = tk.Listbox(self.db_listbox_frame, selectmode=tk.EXTENDED, bg='#2b2b2b', fg='white', 
                                  selectbackground='#3a7ebf', highlightcolor='#3a7ebf', highlightthickness=0, 
                                  bd=0, font=('Arial', 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = ctk.CTkScrollbar(self.db_listbox_frame, command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=self.scrollbar.set)
        
        self.cleanup_action_frame = ctk.CTkFrame(self.main_frame)
        self.cleanup_action_frame.pack(fill="x", padx=10, pady=5)
        
        self.refresh_button = ctk.CTkButton(
            self.cleanup_action_frame, 
            text="Обновить список баз данных",
            **Theme.get_button_colors(),
            command=self.refresh_database_list
        )
        self.refresh_button.pack(side="left", padx=5, pady=5)
        
        self.cleanup_button = ctk.CTkButton(
            self.cleanup_action_frame, 
            text="Очистить выбранные базы данных",
            **Theme.get_button_colors("warning"),
            command=self.clean_selected_databases
        )
        self.cleanup_button.pack(side="right", padx=5, pady=5)
        
        self.delete_db_button = ctk.CTkButton(
            self.cleanup_action_frame, 
            text="Удалить выбранные базы данных",
            **Theme.get_button_colors("danger"),
            command=self.delete_selected_databases
        )
        self.delete_db_button.pack(side="right", padx=5, pady=5)
        
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Статус: Не подключено",
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=5, pady=5)
        
        self.cleanup_results_frame = ctk.CTkFrame(self.main_frame)
        self.cleanup_results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.cleanup_results_textbox = ctk.CTkTextbox(self.cleanup_results_frame)
        self.cleanup_results_textbox.pack(fill="both", expand=True, padx=5, pady=5)
    
    def connect_to_server(self):
        """Подключение к серверу для очистки баз данных"""
        server = self.cleanup_server_entry.get()
        
        if not server:
            self.update_cleanup_status("Ошибка: укажите сервер")
            return
            
        trusted_connection = self.cleanup_auth_var.get() == "Windows"
        username = None if trusted_connection else self.cleanup_username_entry.get()
        password = None if trusted_connection else self.cleanup_password_entry.get()
        
        try:
            self.cleaner.connect(
                server=server,
                username=username,
                password=password,
                trusted_connection=trusted_connection
            )
            
            self.update_cleanup_status(f"Подключено к серверу {server}")
            
            self.refresh_database_list()
            
        except Exception as e:
            self.update_cleanup_status(f"Ошибка подключения: {str(e)}")
            self.update_cleanup_results(f"Ошибка: {str(e)}")
    
    def refresh_database_list(self):
        """Обновляет список баз данных из сервера"""
        if not hasattr(self.cleaner, 'is_connected') or not self.cleaner.is_connected:
            self.update_cleanup_status("Ошибка: не подключено к серверу")
            return
            
        try:
            dbs = self.cleaner.connection.get_all_databases()
            
            self.listbox.delete(0, tk.END)
            for _, row in dbs.iterrows():
                self.listbox.insert(tk.END, row['name'])
                
            self.update_cleanup_status(f"Список баз данных обновлен. Найдено {len(dbs)} баз данных.")
            
        except Exception as e:
            self.update_cleanup_status(f"Ошибка обновления списка: {str(e)}")
    
    def clean_selected_databases(self):
        """Очищает выбранные базы данных от таблиц"""
        if not hasattr(self.cleaner, 'is_connected') or not self.cleaner.is_connected:
            self.update_cleanup_status("Ошибка: не подключено к серверу")
            return
            
        selection = self.listbox.curselection()
        if not selection:
            self.update_cleanup_status("Ошибка: не выбраны базы данных")
            return
            
        selected_dbs = [self.listbox.get(i) for i in selection]
        
        if not self.confirm_cleanup(selected_dbs):
            return
        
        threading.Thread(target=self._clean_databases_thread, args=(selected_dbs,)).start()
    
    def delete_selected_databases(self):
        """Удаляет выбранные базы данных"""
        if not hasattr(self.cleaner, 'is_connected') or not self.cleaner.is_connected:
            self.update_cleanup_status("Ошибка: не подключено к серверу")
            return
            
        selection = self.listbox.curselection()
        if not selection:
            self.update_cleanup_status("Ошибка: не выбраны базы данных")
            return
            
        selected_dbs = [self.listbox.get(i) for i in selection]
        
        if not self.confirm_delete_db(selected_dbs):
            return
        
        threading.Thread(target=self._delete_databases_thread, args=(selected_dbs,)).start()
    
    def _delete_databases_thread(self, databases):
        """Выполняет удаление баз данных в отдельном потоке"""
        self.update_cleanup_status(f"Начало удаления {len(databases)} баз данных...")
        self.update_cleanup_results("Процесс удаления запущен. Пожалуйста, подождите...")
        
        server = self.cleanup_server_entry.get()
        trusted_connection = self.cleanup_auth_var.get() == "Windows"
        username = None if trusted_connection else self.cleanup_username_entry.get()
        password = None if trusted_connection else self.cleanup_password_entry.get()
        
        results = {}
        for db in databases:
            try:
                if isinstance(db, tuple):
                    db_name = db[0]
                else:
                    db_name = db
                    
                self.update_cleanup_status(f"Удаление базы данных {db_name}...")
                
                self.cleaner.disconnect()
                self.cleaner.connect(
                    server=server,
                    username=username,
                    password=password,
                    trusted_connection=trusted_connection
                )
                
                success = self.cleaner.drop_database(db_name)
                results[db_name] = success
            except Exception as e:
                if isinstance(db, tuple):
                    db_name = db[0]
                else:
                    db_name = db
                results[db_name] = False
                self.update_cleanup_results(f"Ошибка при удалении {db_name}: {str(e)}")
                
        report = "Результаты удаления баз данных:\n\n"
        for db, success in results.items():
            status = "Успешно" if success else "Ошибка"
            report += f"{db}: {status}\n"
            
        self.update_cleanup_results(report)
        self.update_cleanup_status("Удаление завершено")
        
        self.refresh_database_list()
    
    def confirm_delete_db(self, databases):
        """Запрашивает подтверждение действия удаления баз данных"""
        from tkinter import messagebox
        
        message = f"ВНИМАНИЕ! Вы собираетесь ПОЛНОСТЬЮ УДАЛИТЬ следующие базы данных:\n\n"
        message += "\n".join(databases[:10])
        
        if len(databases) > 10:
            message += f"\n... и еще {len(databases) - 10} баз данных"
            
        message += "\n\nЭто действие НЕОБРАТИМО и приведет к ПОЛНОЙ ПОТЕРЕ ДАННЫХ! Хотите продолжить?"
        
        return messagebox.askyesno("Подтверждение удаления", message, icon="warning")
    
    def _clean_databases_thread(self, databases):
        """Выполняет очистку баз данных в отдельном потоке"""
        self.update_cleanup_status(f"Начало очистки {len(databases)} баз данных...")
        self.update_cleanup_results("Процесс очистки запущен. Пожалуйста, подождите...")
        
        results = {}
        for db in databases:
            try:
                if isinstance(db, tuple):
                    db_name = db[0]
                else:
                    db_name = db
                    
                self.update_cleanup_status(f"Очистка базы данных {db_name}...")
                success = self.cleaner.drop_all_tables_in_database(db_name)
                results[db_name] = success
            except Exception as e:
                if isinstance(db, tuple):
                    db_name = db[0]
                else:
                    db_name = db
                results[db_name] = False
                self.update_cleanup_results(f"Ошибка при очистке {db_name}: {str(e)}")
                
        report = "Результаты очистки баз данных:\n\n"
        for db, success in results.items():
            status = "Успешно" if success else "Ошибка"
            report += f"{db}: {status}\n"
            
        self.update_cleanup_results(report)
        self.update_cleanup_status("Очистка завершена")
    
    def confirm_cleanup(self, databases):
        """Запрашивает подтверждение действия очистки"""
        from tkinter import messagebox
        
        message = f"Вы собираетесь удалить ВСЕ таблицы из следующих баз данных:\n\n"
        message += "\n".join(databases[:10])
        
        if len(databases) > 10:
            message += f"\n... и еще {len(databases) - 10} баз данных"
            
        message += "\n\nЭто действие необратимо! Хотите продолжить?"
        
        return messagebox.askyesno("Подтверждение очистки", message)
    
    def update_cleanup_status(self, text):
        """Обновляет метку статуса"""
        self.status_label.configure(text=f"Статус: {text}")
    
    def update_cleanup_results(self, text):
        """Обновляет текстовое поле с результатами очистки"""
        self.cleanup_results_textbox.delete("1.0", tk.END)
        self.cleanup_results_textbox.insert("1.0", text) 