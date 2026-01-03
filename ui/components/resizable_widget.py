"""
Resizable Widget - Виджет с возможностью изменения размера перетаскиванием
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QRect, QSize, QPoint
from PyQt6.QtGui import QCursor, QPainter, QColor

class ResizableWidget(QWidget):
    """
    Базовый класс для виджетов с возможностью изменения размера
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._resize_enabled = True
        self._resize_margin = 5
        self._resize_area = None
        self._original_pos = None
        self._original_size = None
        self._mouse_start = None
        
        self.setMouseTracking(True)
    
    def set_resize_enabled(self, enabled):
        """Включить/выключить возможность изменения размера"""
        self._resize_enabled = enabled
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        if event.button() == Qt.MouseButton.LeftButton and self._resize_enabled:
            resize_area = self._get_resize_area(event.position().toPoint())
            if resize_area:
                self._resize_area = resize_area
                self._original_pos = self.pos()
                self._original_size = self.size()
                self._mouse_start = event.globalPosition().toPoint()
                event.accept()
                return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обработка движения мыши"""
        if self._resize_enabled:
            # Изменение размера
            if self._resize_area and event.buttons() & Qt.MouseButton.LeftButton:
                self._perform_resize(event.globalPosition().toPoint())
                event.accept()
                return
            
            # Изменение курсора
            resize_area = self._get_resize_area(event.position().toPoint())
            if resize_area:
                self._set_cursor_for_area(resize_area)
            else:
                self.unsetCursor()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._resize_area = None
            self.unsetCursor()
        
        super().mouseReleaseEvent(event)
    
    def _get_resize_area(self, pos):
        """Определить область изменения размера"""
        if not self._resize_enabled:
            return None
        
        rect = self.rect()
        margin = 5
        
        # Только правый край для изменения ширины
        if pos.x() >= rect.right() - margin:
            return "right"
        
        return None
    
    def _set_cursor_for_area(self, area):
        """Установить курсор для области изменения размера"""
        if area == "right":
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def _perform_resize(self, global_pos):
        """Выполнить изменение размера - только ширина справа"""
        if not self._resize_area or not self._original_size or not self._mouse_start:
            return
        
        delta = global_pos - self._mouse_start
        new_size = QSize(self._original_size)
        
        # Только изменение ширины справа
        if self._resize_area == "right":
            new_width = max(50, self._original_size.width() + delta.x())
            new_size.setWidth(new_width)
        
        # Применение изменений
        self.resize(new_size)


class ResizableLineEdit(QLineEdit):
    """Поле ввода с возможностью изменения размера перетаскиванием справа"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Настройка внешнего вида
        from ui.components.neon_input import NeonLineEdit
        neon_style = NeonLineEdit()._update_style()
        
        # Установка правильной высоты и ширины
        self.setMinimumHeight(18)
        self.setMinimumWidth(100)
        self.resize(200, 18)
        
        # Переменные для изменения размера
        self._resize_enabled = True
        self._resize_margin = 5
        self._resize_area = None
        self._original_size = None
        self._mouse_start = None
        self._save_size_on_resize = True
        self._original_width = None
        
        # Включаем отслеживание мыши
        self.setMouseTracking(True)
        
        # Применение стилей
        self._setup_style()
    
    def _setup_style(self):
        """Настройка стилей как у NeonLineEdit"""
        self.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #313244, stop:1 #1e1e2e);
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 2px 6px;
                selection-background-color: #0000FF;
                selection-color: #FFFFFF;
                font-family: "Inter", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                min-height: 18px;
            }
            
            QLineEdit:focus {
                border-color: #0000FF;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #1e1e2e, stop:1 #181825);
            }
        """)
    
    def set_resize_enabled(self, enabled):
        """Включить/выключить возможность изменения размера"""
        self._resize_enabled = enabled
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        if event.button() == Qt.MouseButton.LeftButton and self._resize_enabled:
            resize_area = self._get_resize_area(event.position().toPoint())
            if resize_area:
                self._resize_area = resize_area
                self._original_size = self.size()
                self._mouse_start = event.globalPosition().toPoint()
                event.accept()
                return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обработка движения мыши"""
        if self._resize_enabled:
            # Изменение размера
            if self._resize_area and event.buttons() & Qt.MouseButton.LeftButton:
                self._perform_resize(event.globalPosition().toPoint())
                event.accept()
                return
            
            # Изменение курсора
            resize_area = self._get_resize_area(event.position().toPoint())
            if resize_area:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.unsetCursor()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._resize_area = None
            self.unsetCursor()
        
        super().mouseReleaseEvent(event)
    
    def _get_resize_area(self, pos):
        """Определить область изменения размера - только правый край"""
        if not self._resize_enabled:
            return None
        
        rect = self.rect()
        margin = 5
        
        # Только правый край для изменения ширины
        if pos.x() >= rect.right() - margin:
            return "right"
        
        return None
    
    def _perform_resize(self, global_pos):
        """Выполнить изменение размера - только ширина справа"""
        if not self._resize_area or not self._original_size or not self._mouse_start:
            return
        
        delta = global_pos - self._mouse_start
        new_size = QSize(self._original_size)
        
        # Только изменение ширины справа
        if self._resize_area == "right":
            new_width = max(50, self._original_size.width() + delta.x())
            new_size.setWidth(new_width)
        
        # Применение изменений
        self.resize(new_size)
    
    def resizeEvent(self, event):
        """Сохранение размера при изменении"""
        super().resizeEvent(event)
        if self._save_size_on_resize:
            new_width = event.size().width()
            if self._original_width is None:
                self._original_width = new_width
            
            # Сохраняем новую ширину в настройки
            self._save_width_to_settings(new_width)
    
    def _save_width_to_settings(self, width):
        """Сохранение ширины в настройки"""
        try:
            import json
            import os
            
            settings_file = "field_widths.json"
            settings_path = os.path.join(os.path.dirname(__file__), "..", "..", settings_file)
            
            # Загружаем существующие настройки
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            
            # Сохраняем ширину для этого поля
            field_id = id(self)  # Уникальный ID поля
            settings[str(field_id)] = width
            
            # Записываем настройки
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Ошибка сохранения ширины поля: {e}")
