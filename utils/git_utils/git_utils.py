"""
Утилиты для работы с Git
"""
import os
import requests
from typing import List, Tuple, Dict, Any
from git import Repo, GitCommandError

class GitManager:
    """Класс для управления Git репозиторием"""
    
    def __init__(self, base_url: str = None, prefix: str = None):
        """
        Инициализация менеджера Git
        
        Args:
            base_url: Базовый URL для Git репозиториев
            prefix: Префикс для имён пользователей (по умолчанию "224-user-")
        """
        self.base_url = base_url
        self.prefix = prefix or os.getenv("GIT_PREFIX", "224-user-")
    
    def set_base_url(self, base_url: str):
        """
        Устанавливает базовый URL для репозиториев
        
        Args:
            base_url: Базовый URL
        """
        self.base_url = base_url
        
    def set_prefix(self, prefix: str):
        """
        Устанавливает префикс для имён пользователей
        
        Args:
            prefix: Префикс
        """
        self.prefix = prefix
    
    def get_user_repositories(self, user_number: int) -> Tuple[bool, List[str]]:
        """
        Получает список репозиториев пользователя через API Gitea
        
        Args:
            user_number: Номер пользователя
            
        Returns:
            Кортеж (успех, список репозиториев или сообщение об ошибке)
        """
        user_name = f"{self.prefix}{user_number}"
        
        try:
            base = self.base_url.split(f'/{self.prefix}')[0] if f'/{self.prefix}' in self.base_url else self.base_url
            api_url = f"{base}/api/v1/users/{user_name}/repos"
            
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                repos = response.json()
                repo_names = [repo['name'] for repo in repos]
                return True, repo_names
            else:
                return False, f"Ошибка получения списка репозиториев: {response.status_code} - {response.reason}"
                
        except requests.exceptions.ConnectionError as e:
            error_details = str(e)
            server_host = api_url.split('/')[2]
            return False, f"Не удалось подключиться к серверу {server_host}. Возможно, сервер недоступен или брандмауэр блокирует соединение. Подробности: {error_details}"
        except requests.RequestException as e:
            return False, f"Ошибка запроса: {str(e)}"
        except Exception as e:
            return False, f"Непредвиденная ошибка: {str(e)}"
    
    def clone_repository(self, user_number: int, repo_name: str, target_path: str) -> Tuple[bool, str]:
        """
        Клонирует конкретный репозиторий пользователя
        
        Args:
            user_number: Номер пользователя
            repo_name: Имя репозитория
            target_path: Путь для клонирования
            
        Returns:
            Кортеж (успех, результат/ошибка)
        """
        user_name = f"{self.prefix}{user_number}"
        
        try:
            base = self.base_url.split(f'/{self.prefix}')[0] if f'/{self.prefix}' in self.base_url else self.base_url
            
            if repo_name == user_name:
                repo_url = f"{base}/{user_name}"
            else:
                repo_url = f"{base}/{user_name}/{repo_name}"
            
            Repo.clone_from(repo_url, target_path)
            return True, f"Успешно клонирован репозиторий {repo_name}"
        except GitCommandError as e:
            error_str = str(e)
            
            # Проверяем код ошибки 128 и наличие директории
            if "exit code(128)" in error_str:
                if "destination path" in error_str and "already exists" in error_str:
                    return False, f"Репозиторий {repo_name} уже существует на вашем ПК в директории {target_path}"
                elif "Could not connect to server" in error_str or "Failed to connect" in error_str:
                    return False, f"Не удалось подключиться к серверу Git. Проверьте соединение и настройки сервера."
            
            return False, str(e)
        except Exception as e:
            return False, str(e)
    
    def batch_clone_user_repositories(self, from_user: int, to_user: int, base_path: str, 
                                     progress_callback=None) -> List[Dict[str, Any]]:
        """
        Клонирует все репозитории для диапазона пользователей
        
        Args:
            from_user: Начальный номер пользователя
            to_user: Конечный номер пользователя
            base_path: Базовый путь для сохранения репозиториев
            progress_callback: Функция обратного вызова для отчета о прогрессе
            
        Returns:
            Список результатов клонирования
        """
        results = []
        total_users = to_user - from_user + 1
        processed = 0
        total_repos = 0
        cloned_repos = 0
        
        for user_num in range(from_user, to_user + 1):
            user_name = f"{self.prefix}{user_num}"
            computer_folder = f"Компьютер {user_num}"
            
            user_folder = os.path.join(base_path, computer_folder)
            
            if not os.path.exists(user_folder):
                try:
                    os.makedirs(user_folder)
                except Exception as e:
                    results.append({
                        "user_number": user_num,
                        "repo_name": None,
                        "success": False,
                        "message": f"Ошибка создания директории: {str(e)}"
                    })
                    continue
            
            success, repos_or_error = self.get_user_repositories(user_num)
            
            if not success:
                results.append({
                    "user_number": user_num,
                    "repo_name": None,
                    "success": False, 
                    "message": repos_or_error
                })
                
                processed += 1
                if progress_callback:
                    progress_callback(processed, total_users, cloned_repos, total_repos)
                continue
            else:
                repos = repos_or_error
                total_repos += len(repos)
                
                for repo_name in repos:
                    repo_path = os.path.join(user_folder, repo_name)
                    
                    success, message = self.clone_repository(user_num, repo_name, repo_path)
                    
                    results.append({
                        "user_number": user_num,
                        "repo_name": repo_name,
                        "success": success,
                        "message": message
                    })
                    
                    if success:
                        cloned_repos += 1
            
            processed += 1
            if progress_callback:
                progress_callback(processed, total_users, cloned_repos, total_repos)
        
        return results 