"""
AutoNekits - Многофункциональный инструмент для работы с базами данных и Git
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    """
    Главная функция запуска приложения
    """
    from ui import get_app_instance
    
    app = get_app_instance()
    
    app.mainloop()

if __name__ == "__main__":
    main()
