"""
Settings Dialog - Диалог настроек приложения
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGroupBox, QFormLayout, 
    QLineEdit, QDialogButtonBox, QLabel, QMessageBox
)
import json
import os

class SettingsDialog(QDialog):
    """Диалог настроек (API ключи и промпты)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(500)
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # API Keys Group
        keys_group = QGroupBox("API Ключи (из .env)")
        keys_layout = QFormLayout()
        
        self.perplexity_key = QLineEdit()
        self.perplexity_key.setPlaceholderText("pplx-...")
        self.perplexity_key.setEchoMode(QLineEdit.EchoMode.Password)
        keys_layout.addRow("Perplexity API Key:", self.perplexity_key)
        
        self.mistral_key = QLineEdit()
        self.mistral_key.setPlaceholderText("...")
        self.mistral_key.setEchoMode(QLineEdit.EchoMode.Password)
        keys_layout.addRow("Mistral API Key:", self.mistral_key)
        
        self.deepseek_key = QLineEdit()
        self.deepseek_key.setPlaceholderText("sk-...")
        self.deepseek_key.setEchoMode(QLineEdit.EchoMode.Password)
        keys_layout.addRow("DeepSeek API Key:", self.deepseek_key)
        
        keys_group.setLayout(keys_layout)
        layout.addWidget(keys_group)
        
        # Keys Info
        info_label = QLabel("Ключи сохраняются в файл .env в корне проекта")
        info_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(info_label)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_settings(self):
        """Загрузить настройки."""
        from dotenv import load_dotenv
        load_dotenv()
        
        self.perplexity_key.setText(os.getenv("PERPLEXITY_API_KEY", ""))
        self.mistral_key.setText(os.getenv("MISTRAL_API_KEY", ""))
        self.deepseek_key.setText(os.getenv("DEEPSEEK_API_KEY", ""))
        
    def save_settings(self):
        """Сохранить настройки."""
        env_content = ""
        
        # Читаем существующий
        try:
            with open(".env", "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Простой парсинг для сохранения других переменных если есть
                env_map = {}
                for line in lines:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        env_map[k] = v
        except FileNotFoundError:
            env_map = {}
            
        # Обновляем
        env_map["PERPLEXITY_API_KEY"] = self.perplexity_key.text()
        env_map["MISTRAL_API_KEY"] = self.mistral_key.text()
        env_map["DEEPSEEK_API_KEY"] = self.deepseek_key.text()
        
        # Записываем
        with open(".env", "w", encoding="utf-8") as f:
            for k, v in env_map.items():
                f.write(f"{k}={v}\n")
                
        # Перезагружаем переменные окружения
        os.environ["PERPLEXITY_API_KEY"] = self.perplexity_key.text()
        os.environ["MISTRAL_API_KEY"] = self.mistral_key.text()
        os.environ["DEEPSEEK_API_KEY"] = self.deepseek_key.text()
        
        # Переинициализация AI сервиса чтобы подхватил новые ключи
        from core.ai_service import ai_service
        ai_service.__init__()
        
        QMessageBox.information(self, "Успех", "Настройки сохранены")
        self.accept()
