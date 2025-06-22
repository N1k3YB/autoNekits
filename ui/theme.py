import customtkinter as ctk

class Theme:
    """Класс для управления темой приложения"""
    
    PRIMARY_COLOR = "#3a7ebf"
    SECONDARY_COLOR = "#2a5a8a"
    SUCCESS_COLOR = "#2d9d5c"
    WARNING_COLOR = "#f79009"
    DANGER_COLOR = "#d13438"
    
    @classmethod
    def setup(cls):
        """Настраивает основные параметры темы"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        cls._customize_colors()
        
    @classmethod
    def _customize_colors(cls):
        """Настраивает индивидуальные цвета элементов интерфейса"""
        pass
    
    @classmethod
    def toggle_theme(cls):
        """Переключает между темной и светлой темой"""
        if ctk.get_appearance_mode() == "dark":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
            
    @classmethod
    def get_button_colors(cls, button_type="primary"):
        """Возвращает цвета для кнопки в зависимости от типа"""
        if button_type == "primary":
            return {"fg_color": cls.PRIMARY_COLOR, "hover_color": cls.SECONDARY_COLOR}
        elif button_type == "success":
            return {"fg_color": cls.SUCCESS_COLOR, "hover_color": "#238b4b"}
        elif button_type == "warning":
            return {"fg_color": cls.WARNING_COLOR, "hover_color": "#e67e00"}
        elif button_type == "danger":
            return {"fg_color": cls.DANGER_COLOR, "hover_color": "#ba2d2d"}
        else:
            return {} 