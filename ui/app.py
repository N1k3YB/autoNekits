import customtkinter as ctk
import sys
import os

from .tabs.mssql_tab import MSSQLTab
from .tabs.postgres_tab import PostgresTab
from .tabs.git_tab import GitTab
from .theme import Theme

class AutoNekits(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AutoNekits")
        self.geometry("1300x1000")
        self.minsize(800, 500)
        
        Theme.setup()
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.pack(fill="x", pady=(0, 10))
        
        self.logo_label = ctk.CTkLabel(
            self.header_frame, 
            text="SemiMajor Expert Specialy For KCPT DemoExamenation", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.pack(side="left", padx=10, pady=10)
        
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True)
        
        self.tabview.add("MS SQL Server")
        self.tabview.add("PostgreSQL")
        self.tabview.add("Git")
        
        self.mssql_tab = MSSQLTab(self.tabview.tab("MS SQL Server"))
        self.postgres_tab = PostgresTab(self.tabview.tab("PostgreSQL"))
        self.git_tab = GitTab(self.tabview.tab("Git"))
        
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30)
        self.status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Готов к работе", 
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
    def update_status(self, message):
        """Обновляет строку состояния"""
        self.status_label.configure(text=message)

def get_app_instance():
    """Возвращает экземпляр приложения"""
    app = AutoNekits()
    return app 