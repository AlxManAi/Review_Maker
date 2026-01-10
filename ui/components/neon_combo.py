"""
Neon Combo - Выпадающие списки с неоновыми эффектами
"""
from PyQt6.QtWidgets import QComboBox, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor

class NeonComboBox(QComboBox):
    """
    Выпадающий список с неоновыми эффектами
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._hover_intensity = 0.0
        self._setup_base_style()
        self._setup_neon_effect()
        self._setup_animations()
    
    def _setup_base_style(self):
        """Базовые настройки"""
        self.setMinimumHeight(17)  # Шрифт 13px + 4px = 17px
        self.setMinimumWidth(140)
        
        font = self.font()
        font.setFamily("Inter, Segoe UI, Arial, sans-serif")
        font.setPointSize(13)
        self.setFont(font)
    
    def _setup_neon_effect(self):
        """Настройка неонового свечения"""
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(6)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setYOffset(0)
        self.setGraphicsEffect(self.shadow_effect)
    
    def _setup_animations(self):
        """Настройка анимаций"""
        self.hover_animation = QPropertyAnimation(self, b"hover_intensity")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def _update_style(self):
        """Обновление стиля"""
        neon_color = "#4A90E2"  # Ледяной синий
        base_color = "#313244"
        
        style = f"""
            QComboBox {{
                background-color: {base_color};
                color: #cdd6f4;
                border: 2px solid #45475a;
                border-radius: 6px;
                padding: 2px 8px;
                font-family: "Inter", "Segoe UI", Arial, sans-serif;
                font-size: 13px;
                min-width: 140px;
                min-height: 17px;
            }}
            
            QComboBox:hover {{
                border-color: {neon_color};
                background-color: #1e1e2e;
            }}
            
            QComboBox:focus {{
                border-color: {neon_color};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                background-color: transparent;
            }}
            
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
                background-color: #4A90E2;  /* Ледяной синий */
            }}
            
            QComboBox QAbstractItemView {{
                background-color: #1e1e2e;
                border: 2px solid {neon_color};
                border-radius: 6px;
                selection-background-color: #4A90E2;  /* Ледяной синий */
                selection-color: #FFFFFF;
                padding: 4px;
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
                margin: 2px;
            }}
            
            QComboBox QAbstractItemView::item:selected {{
                background-color: #4A90E2;  /* Ледяной синий */
                color: #FFFFFF;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: #45475a;
            }}
        """
        
        self.setStyleSheet(style)
        
        # Обновление свечения
        glow_color = QColor(neon_color)
        glow_color.setAlphaF(self._hover_intensity * 0.5)
        self.shadow_effect.setColor(glow_color)
        self.shadow_effect.setBlurRadius(6 + self._hover_intensity * 10)
    
    def set_hover_intensity(self, intensity):
        """Установить интенсивность свечения при наведении"""
        self._hover_intensity = max(0.0, min(1.0, intensity))
        self._update_style()
    
    def get_hover_intensity(self):
        """Получить интенсивность свечения"""
        return self._hover_intensity
    
    hover_intensity = pyqtProperty(float, get_hover_intensity, set_hover_intensity)
    
    def enterEvent(self, event):
        """При наведении"""
        super().enterEvent(event)
        self.hover_animation.setStartValue(0.0)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
    
    def leaveEvent(self, event):
        """При уходе курсора"""
        super().leaveEvent(event)
        self.hover_animation.setStartValue(1.0)
        self.hover_animation.setEndValue(0.0)
        self.hover_animation.start()
