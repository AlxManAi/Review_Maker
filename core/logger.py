"""
Logger - Файловое логирование для десктоп приложения с настройками
"""
import logging
import os
from datetime import datetime
from pathlib import Path
import glob
import json


class AppLogger:
    """Система логирования приложения с настройками."""
    
    def __init__(self):
        self.logger = None
        self.settings_file = Path.home() / "ReviewGenerator" / "logging_settings.json"
        self.settings = self.load_settings()
        self.setup_logging()
    
    def load_settings(self):
        """Загрузка настроек логирования."""
        default_settings = {
            "enabled": True,
            "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            "max_files": 7,  # Хранить логи за последние 7 дней
            "file_logging": True,
            "console_logging": True
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.save_settings(default_settings)
                return default_settings
        except Exception:
            return default_settings
    
    def save_settings(self, settings=None):
        """Сохранение настроек логирования."""
        if settings:
            self.settings = settings
        
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек логирования: {e}")
    
    def setup_logging(self):
        """Настройка логирования."""
        if not self.settings.get("enabled", True):
            # Логирование отключено
            self.logger = logging.getLogger('ReviewGenerator')
            self.logger.setLevel(logging.CRITICAL + 1)  # Отключаем все логи
            return
        
        # Создаем папку для логов
        log_dir = Path.home() / "ReviewGenerator" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Имя файла с датой
        log_file = log_dir / f"review_generator_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        # Настраиваем логгер
        self.logger = logging.getLogger('ReviewGenerator')
        self.logger.setLevel(getattr(logging, self.settings.get("level", "INFO")))
        
        # Удаляем существующие обработчики
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Форматирование
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Файловый обработчик
        if self.settings.get("file_logging", True):
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, self.settings.get("level", "INFO")))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Консольный обработчик
        if self.settings.get("console_logging", True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.settings.get("level", "INFO")))
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Записываем запуск
        self.info("=== ЗАПУСК ПРИЛОЖЕНИЯ REVIEW GENERATOR ===")
        self.info(f"Файл лога: {log_file}")
        self.info(f"Настройки: {self.settings}")
        
        # Очистка старых логов
        self.cleanup_old_logs()
    
    def cleanup_old_logs(self):
        """Очистка старых логов."""
        try:
            log_dir = Path.home() / "ReviewGenerator" / "logs"
            max_files = self.settings.get("max_files", 7)
            
            # Находим все лог файлы
            log_files = glob.glob(str(log_dir / "review_generator_*.log"))
            log_files.sort(reverse=True)  # Новые первые
            
            # Удаляем старые файлы
            for log_file in log_files[max_files:]:
                try:
                    os.remove(log_file)
                    self.info(f"Удален старый лог файл: {log_file}")
                except Exception as e:
                    self.error(f"Ошибка удаления лог файла {log_file}: {e}")
        
        except Exception as e:
            self.error(f"Ошибка очистки логов: {e}")
    
    def clear_all_logs(self):
        """Полная очистка всех логов."""
        try:
            log_dir = Path.home() / "ReviewGenerator" / "logs"
            
            # Удаляем все лог файлы
            log_files = glob.glob(str(log_dir / "review_generator_*.log"))
            for log_file in log_files:
                try:
                    os.remove(log_file)
                    print(f"Удален лог файл: {log_file}")
                except Exception as e:
                    print(f"Ошибка удаления лог файла {log_file}: {e}")
            
            print(f"Очищено {len(log_files)} лог файлов")
            
        except Exception as e:
            print(f"Ошибка очистки логов: {e}")
    
    def get_log_info(self):
        """Получение информации о логах."""
        try:
            log_dir = Path.home() / "ReviewGenerator" / "logs"
            log_files = glob.glob(str(log_dir / "review_generator_*.log"))
            
            total_size = sum(os.path.getsize(f) for f in log_files if os.path.exists(f))
            
            return {
                "count": len(log_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "log_dir": str(log_dir),
                "files": [{"name": Path(f).name, "size_mb": round(os.path.getsize(f) / (1024 * 1024), 2)} for f in log_files if os.path.exists(f)]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def is_enabled(self):
        """Проверка включено ли логирование."""
        return self.settings.get("enabled", True)
    
    def enable_logging(self, enabled=True):
        """Включение/выключение логирования."""
        self.settings["enabled"] = enabled
        self.save_settings()
        self.setup_logging()  # Перенастройка логирования
    
    def set_level(self, level):
        """Установка уровня логирования."""
        self.settings["level"] = level
        self.save_settings()
        self.setup_logging()
    
    def debug(self, message):
        """DEBUG сообщение."""
        if self.logger and self.is_enabled():
            self.logger.debug(message)
    
    def info(self, message):
        """INFO сообщение."""
        if self.logger and self.is_enabled():
            self.logger.info(message)
    
    def warning(self, message):
        """WARNING сообщение."""
        if self.logger and self.is_enabled():
            self.logger.warning(message)
    
    def error(self, message):
        """ERROR сообщение."""
        if self.logger and self.is_enabled():
            self.logger.error(message)
    
    def critical(self, message):
        """CRITICAL сообщение."""
        if self.logger and self.is_enabled():
            self.logger.critical(message)
    
    def exception(self, message):
        """EXCEPTION с traceback."""
        if self.logger and self.is_enabled():
            self.logger.exception(message)


# Глобальный экземпляр
app_logger = AppLogger()
