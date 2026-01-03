"""
Neon Button - Кнопка с неоновыми эффектами и умной активностью
"""
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor

class NeonButton(QPushButton):
    """
    Кнопка с неоновыми эффектами:
    - Фиолетовая неоновая обводка
    - Эффект свечения
    - Умная активность (active, suggested, hover)
    - Плавные анимации
    """
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        
        # Типы кнопок
        self.button_type = button_type  # primary, secondary, suggested
        self._glow_intensity = 0.0
        self._is_pulsing = False
        
        # Настройка базового стиля
        self._setup_base_style()
        self._setup_neon_effect()
        self._setup_animations()
        
        # Применение стиля
        self._update_style()
    
    def _setup_base_style(self):
        """Базовые настройки кнопки"""
        self.setMinimumHeight(18)  # Шрифт 14px + 4px = 18px
        self.setMinimumWidth(140)
        
        # Шрифт 14px
        font = self.font()
        font.setFamily("Inter, Segoe UI, Arial, sans-serif")
        font.setPointSize(14)
        font.setWeight(600)  # Полужирный
        self.setFont(font)
    
    def _setup_neon_effect(self):
        """Настройка яркого неонового свечения"""
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(25)  # Увеличенное свечение
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setYOffset(0)
        self.shadow_effect.setColor(QColor(255, 255, 255))  # Белый для яркости
        self.setGraphicsEffect(self.shadow_effect)
    
    def _setup_animations(self):
        """Настройка анимаций"""
        self.glow_animation = QPropertyAnimation(self, b"glow_intensity")
        self.glow_animation.setDuration(300)
        self.glow_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def _update_style(self):
        """Обновление стиля - настоящие синие кнопки с четкой обводкой"""
        # Настоящий синий цвет с четкой обводкой SteelBlue
        base_color = "#0000FF"  # Настоящий синий
        neon_color = "#4682B4"  # SteelBlue - самый четкий и контрастный
        text_color = "#FFFFFF"
        
        # Стиль с тонкой 1px пиксельной обводкой
        style = f"""
            QPushButton {{
                background-color: {base_color};
                color: {text_color};
                border: 1px solid {neon_color};  /* Тонкая 1px обводка */
                border-radius: 6px;
                padding: 3px 10px;
                font-family: "Inter", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                text-align: center;
                min-height: 18px;  /* Шрифт 14px + 4px = 18px */
            }}
            
            /* Тонкая 1px пиксельная обводка */
            QPushButton::before {{
                content: "";
                position: absolute;
                top: 1px;
                left: 1px;
                right: 1px;
                bottom: 1px;
                border: 1px solid {neon_color};
                border-radius: 5px;
                pointer-events: none;
            }}
            
            QPushButton:hover {{
                background-color: {neon_color};
                border-color: {base_color};
                color: #FFFFFF;
            }}
            
            QPushButton:pressed {{
                background-color: {base_color};
                border-color: {neon_color};
            }}
            
            QPushButton:disabled {{
                background-color: #313244;
                border-color: #45475a;
                color: #6c7086;
            }}
        """
        
        self.setStyleSheet(style)
        
        # Свечение с контрастным цветом
        glow_color = QColor(neon_color)
        glow_color.setAlphaF(0.4)
        self.shadow_effect.setColor(glow_color)
        self.shadow_effect.setBlurRadius(10)
    
    def set_button_type(self, button_type):
        """Установить тип кнопки"""
        self.button_type = button_type
        self._update_style()
    
    def set_suggested(self, suggested=True):
        """Сделать кнопку рекомендуемой действием"""
        if suggested:
            self.set_button_type("suggested")
            self.start_pulsing()
        else:
            self.set_button_type("primary")
            self.stop_pulsing()
    
    def start_pulsing(self):
        """Запустить пульсацию (для рекомендуемых действий)"""
        if not self._is_pulsing:
            self._is_pulsing = True
            self._pulse_animation()
    
    def stop_pulsing(self):
        """Остановить пульсацию"""
        self._is_pulsing = False
        self.set_glow_intensity(0.0)
    
    def _pulse_animation(self):
        """Внутренняя анимация пульсации"""
        if not self._is_pulsing:
            return
        
        # Анимация от 0 до 1 и обратно
        self.glow_animation.setStartValue(0.0)
        self.glow_animation.setEndValue(1.0)
        self.glow_animation.finished.connect(lambda: self._pulse_reverse())
        self.glow_animation.start()
    
    def _pulse_reverse(self):
        """Обратная анимация пульсации"""
        if not self._is_pulsing:
            return
        
        self.glow_animation.finished.disconnect()
        self.glow_animation.setStartValue(1.0)
        self.glow_animation.setEndValue(0.0)
        self.glow_animation.finished.connect(lambda: self._pulse_animation())
        self.glow_animation.start()
    
    def set_glow_intensity(self, intensity):
        """Установить интенсивность свечения (0.0 - 1.0)"""
        self._glow_intensity = max(0.0, min(1.0, intensity))
        self._update_style()
    
    def get_glow_intensity(self):
        """Получить интенсивность свечения"""
        return self._glow_intensity
    
    glow_intensity = pyqtProperty(float, get_glow_intensity, set_glow_intensity)
    
    def enterEvent(self, event):
        """При наведении - усиление свечения"""
        super().enterEvent(event)
        if not self._is_pulsing:
            self.set_glow_intensity(0.3)
    
    def leaveEvent(self, event):
        """При уходе курсора - возврат к нормальному состоянию"""
        super().leaveEvent(event)
        if not self._is_pulsing:
            self.set_glow_intensity(0.0)
