import os
import threading
import customtkinter as ctk
from ..theme import Theme
from utils.git_utils import GitManager

class GitTab:
    def __init__(self, parent):
        self.parent = parent
        
        self.base_git_url = os.getenv("GIT_URL", "http://localhost:8888/224-user-")
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        self.git_manager = GitManager(self.base_git_url)
        
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
            text=f"Будут клонированы репозитории пользователей формата '224-user-X'\nВ директории на рабочем столе в папки 'Компьютер X'",
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        self.description_label.pack(anchor="w", padx=10, pady=(0, 15))
        
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
            
            self.log_text.configure(state="normal")
            self.log_text.delete(1.0, "end")
            self.log_text.configure(state="disabled")
            
            self.clone_button.configure(state="disabled")
            self.update_status("Начинаем клонирование репозиториев...")
            self.log_message("Запуск процесса клонирования...")
            
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