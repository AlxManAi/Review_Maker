"""
Neon Input - Поля ввода с неоновыми эффектами
"""
from PyQt6.QtWidgets import QLineEdit, QTextEdit, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor

class NeonLineEdit(QLineEdit):
    """
    Поле ввода с неоновыми эффектами
    """
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(placeholder, parent)
        
        self._focus_intensity = 0.0
        self._setup_base_style()
        self._setup_neon_effect()
        self._setup_animations()
    
    def _setup_base_style(self):
        """Базовые настройки поля ввода"""
        self.setMinimumHeight(18)  # Шрифт 14px + 4px = 18px
        
        font = self.font()
        font.setFamily("Inter, Segoe UI, Arial, sans-serif")
        font.setPointSize(14)
        self.setFont(font)
    
    def _setup_neon_effect(self):
        """Настройка неонового свечения"""
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setYOffset(0)
        self.setGraphicsEffect(self.shadow_effect)
    
    def _setup_animations(self):
        """Настройка анимаций"""
        self.focus_animation = QPropertyAnimation(self, b"focus_intensity")
        self.focus_animation.setDuration(200)
        self.focus_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def _update_style(self):
        """Обновление стиля"""
        neon_color = "#4A90E2"  # Ледяной синий
        base_color = "#313244"
        
        if self.hasFocus():
            border_color = neon_color
            bg_color = "#1e1e2e"
        else:
            border_color = "#45475a"
            bg_color = base_color
        
        style = f"""
            QLineEdit {{
                background-color: {bg_color};
                color: #cdd6f4;
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 2px 6px;
                font-family: "Inter", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                selection-background-color: #0000FF;
                selection-color: #FFFFFF;
            }}
            
            QLineEdit:focus {{
                border-color: #0000FF;
                background-color: #1e1e2e;
            }}
        """
        
        self.setStyleSheet(style)
        
        # Обновление свечения при фокусе
        if self.hasFocus():
            glow_color = QColor(neon_color)
            glow_color.setAlphaF(0.4 + self._focus_intensity * 0.6)
            self.shadow_effect.setColor(glow_color)
            self.shadow_effect.setBlurRadius(8 + self._focus_intensity * 12)
        else:
            self.shadow_effect.setColor(QColor(neon_color))
            self.shadow_effect.setBlurRadius(0)
    
    def set_focus_intensity(self, intensity):
        """Установить интенсивность свечения при фокусе"""
        self._focus_intensity = max(0.0, min(1.0, intensity))
        self._update_style()
    
    def get_focus_intensity(self):
        """Получить интенсивность свечения"""
        return self._focus_intensity
    
    focus_intensity = pyqtProperty(float, get_focus_intensity, set_focus_intensity)
    
    def focusInEvent(self, event):
        """При получении фокуса"""
        super().focusInEvent(event)
        self.focus_animation.setStartValue(0.0)
        self.focus_animation.setEndValue(1.0)
        self.focus_animation.start()
    
    def focusOutEvent(self, event):
        """При потере фокуса"""
        super().focusOutEvent(event)
        self.focus_animation.setStartValue(1.0)
        self.focus_animation.setEndValue(0.0)
        self.focus_animation.start()
