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
        # Шрифт 14px, Высота 24px (оптимально для компактности)
        self.setMinimumHeight(24)
        self.setMaximumHeight(24)
        
        font = self.font()
        font.setFamily("Inter, Segoe UI, Arial, sans-serif")
        font.setPointSize(14)
        font.setWeight(400) # Normal weight
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
        """Обновление стиля - Ghost Style (1px контурный стиль)"""
        if self.button_type == "danger":
            border_color = "#ff4d4d"  # Красный
            text_color = "#ff4d4d"
            hover_bg = "rgba(255, 77, 77, 0.12)"
        elif self.button_type == "suggested":
            border_color = "#ff9f43"  # Оранжевый
            text_color = "#ff9f43"
            hover_bg = "rgba(255, 159, 67, 0.12)"
        elif self.button_type == "secondary":
            border_color = "#585b70"  # Серый
            text_color = "#cdd6f4"
            hover_bg = "rgba(88, 91, 112, 0.15)"
        else: # primary
            border_color = "#4a9eff"  # Синий
            text_color = "#4a9eff"
            hover_bg = "rgba(74, 158, 255, 0.12)"

        style = f"""
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 3px 12px;
                font-family: "Inter", "Segoe UI", Arial, sans-serif;
                text-align: center;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background-color: {hover_bg.replace('0.12', '0.2').replace('0.15', '0.2')};
            }}
            QPushButton:disabled {{
                color: #45475a;
                border-color: #313244;
                background-color: transparent;
            }}
        """
        self.setStyleSheet(style)
        
        # Свечение только при пульсации или наведении (ослабленное для элегантности)
        glow_color = QColor(border_color)
        opacity = 0.3 if self._glow_intensity > 0 else 0.0
        glow_color.setAlphaF(opacity * self._glow_intensity)
        self.shadow_effect.setColor(glow_color)
        self.shadow_effect.setBlurRadius(12 * self._glow_intensity)
    
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
        try:
            # Проверяем тип intensity
            if isinstance(intensity, (int, float)):
                # Явно используем встроенную функцию max
                import builtins
                self._glow_intensity = builtins.max(0.0, builtins.min(1.0, float(intensity)))
            elif isinstance(intensity, str):
                # Пытаемся конвертировать строку в число
                try:
                    import builtins
                    self._glow_intensity = builtins.max(0.0, builtins.min(1.0, float(intensity)))
                except ValueError:
                    print(f"Warning: Cannot convert '{intensity}' to float, using 0.0")
                    self._glow_intensity = 0.0
            else:
                print(f"Warning: Invalid intensity type {type(intensity)}, using 0.0")
                self._glow_intensity = 0.0
            
            self._update_style()
        except Exception as e:
            print(f"Error in set_glow_intensity: {e}")
            self._glow_intensity = 0.0
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
