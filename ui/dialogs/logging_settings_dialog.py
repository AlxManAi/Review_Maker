"""
Logging Settings Dialog - Диалог настроек логирования
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QComboBox, QPushButton, QSpinBox, QGroupBox, QTextEdit,
    QProgressBar, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from core.logger import app_logger
import os


class LoggingSettingsDialog(QDialog):
    """Диалог настроек логирования."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки логирования")
        self.setModal(True)
        self.resize(500, 600)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        
        # Группа основных настроек
        main_group = QGroupBox("Основные настройки")
        main_layout = QVBoxLayout()
        
        # Включение логирования
        self.enabled_checkbox = QCheckBox("Включить логирование")
        self.enabled_checkbox.toggled.connect(self.on_enabled_changed)
        main_layout.addWidget(self.enabled_checkbox)
        
        # Уровень логирования
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Уровень логирования:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.on_level_changed)
        level_layout.addWidget(self.level_combo)
        level_layout.addStretch()
        main_layout.addLayout(level_layout)
        
        # Хранение файлов
        files_layout = QHBoxLayout()
        files_layout.addWidget(QLabel("Хранить логи (дней):"))
        self.max_files_spin = QSpinBox()
        self.max_files_spin.setRange(1, 30)
        self.max_files_spin.valueChanged.connect(self.on_max_files_changed)
        files_layout.addWidget(self.max_files_spin)
        files_layout.addStretch()
        main_layout.addLayout(files_layout)
        
        main_group.setLayout(main_layout)
        layout.addWidget(main_group)
        
        # Группа вывода
        output_group = QGroupBox("Вывод логов")
        output_layout = QVBoxLayout()
        
        self.file_checkbox = QCheckBox("Записывать в файл")
        self.file_checkbox.toggled.connect(self.on_file_logging_changed)
        output_layout.addWidget(self.file_checkbox)
        
        self.console_checkbox = QCheckBox("Выводить в консоль")
        self.console_checkbox.toggled.connect(self.on_console_logging_changed)
        output_layout.addWidget(self.console_checkbox)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Информация о логах
        info_group = QGroupBox("Информация о логах")
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel("Загрузка...")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        # Кнопка обновления информации
        self.refresh_btn = QPushButton("Обновить информацию")
        self.refresh_btn.clicked.connect(self.update_log_info)
        info_layout.addWidget(self.refresh_btn)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Управление логами
        manage_group = QGroupBox("Управление логами")
        manage_layout = QVBoxLayout()
        
        # Кнопка очистки
        self.clear_btn = QPushButton("Очистить все логи")
        self.clear_btn.clicked.connect(self.clear_logs)
        self.clear_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 8px;")
        manage_layout.addWidget(self.clear_btn)
        
        # Кнопка открытия папки
        self.open_folder_btn = QPushButton("Открыть папку с логами")
        self.open_folder_btn.clicked.connect(self.open_log_folder)
        self.open_folder_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px;")
        manage_layout.addWidget(self.open_folder_btn)
        
        manage_group.setLayout(manage_layout)
        layout.addWidget(manage_group)
        
        # Кнопки диалога
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_settings(self):
        """Загрузка настроек в интерфейс."""
        settings = app_logger.settings
        
        self.enabled_checkbox.setChecked(settings.get("enabled", True))
        self.level_combo.setCurrentText(settings.get("level", "INFO"))
        self.max_files_spin.setValue(settings.get("max_files", 7))
        self.file_checkbox.setChecked(settings.get("file_logging", True))
        self.console_checkbox.setChecked(settings.get("console_logging", True))
        
        self.update_log_info()
    
    def on_enabled_changed(self, checked):
        """Изменение включения логирования."""
        app_logger.enable_logging(checked)
        self.update_log_info()
    
    def on_level_changed(self, level):
        """Изменение уровня логирования."""
        app_logger.set_level(level)
    
    def on_max_files_changed(self, value):
        """Изменение количества хранимых файлов."""
        app_logger.settings["max_files"] = value
        app_logger.save_settings()
    
    def on_file_logging_changed(self, checked):
        """Изменение файлового логирования."""
        app_logger.settings["file_logging"] = checked
        app_logger.save_settings()
        app_logger.setup_logging()
    
    def on_console_logging_changed(self, checked):
        """Изменение консольного логирования."""
        app_logger.settings["console_logging"] = checked
        app_logger.save_settings()
        app_logger.setup_logging()
    
    def update_log_info(self):
        """Обновление информации о логах."""
        info = app_logger.get_log_info()
        
        if "error" in info:
            self.info_label.setText(f"Ошибка: {info['error']}")
            return
        
        if not app_logger.is_enabled():
            self.info_label.setText("Логирование отключено")
            return
        
        text = f"""Количество лог файлов: {info['count']}
Общий размер: {info['total_size_mb']} МБ
Папка логов: {info['log_dir']}

Файлы:
"""
        
        for file_info in info['files']:
            text += f"• {file_info['name']} ({file_info['size_mb']} МБ)\n"
        
        self.info_label.setText(text)
    
    def clear_logs(self):
        """Очистка всех логов."""
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Вы уверены, что хотите удалить все логи? Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            app_logger.clear_all_logs()
            self.update_log_info()
            QMessageBox.information(self, "Готово", "Все логи удалены")
    
    def open_log_folder(self):
        """Открытие папки с логами."""
        try:
            import subprocess
            import platform
            
            log_dir = os.path.expanduser("~/ReviewGenerator/logs")
            
            if platform.system() == "Windows":
                os.startfile(log_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", log_dir])
            else:  # Linux
                subprocess.run(["xdg-open", log_dir])
                
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть папку: {e}")
