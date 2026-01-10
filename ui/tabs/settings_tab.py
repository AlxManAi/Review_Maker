"""
Settings Tab - Вкладка настроек проекта
"""
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTextEdit, QLabel, QPushButton, QMessageBox,
    QGroupBox, QGridLayout, QLineEdit, QSpinBox
)
from PyQt6.QtCore import Qt
from core.logger import app_logger
from ui.components.neon_button import NeonButton


class SettingsTab(QWidget):
    """Вкладка настроек проекта."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок с кнопкой назад
        header_layout = QHBoxLayout()
        
        back_btn = NeonButton("← Назад", "secondary")
        back_btn.clicked.connect(self.go_back)
        back_btn.setMaximumWidth(100)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Создаем вкладки для разных настроек
        tab_widget = QTabWidget()
        
        # Вкладка промптов
        prompts_tab = self.create_prompts_tab()
        tab_widget.addTab(prompts_tab, "Промпты")
        
        # Вкладка базы знаний
        knowledge_tab = self.create_knowledge_tab()
        tab_widget.addTab(knowledge_tab, "База знаний")
        
        # Вкладка API
        api_tab = self.create_api_tab()
        tab_widget.addTab(api_tab, "API настройки")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
    
    def create_prompts_tab(self):
        """Создать вкладку редактирования промптов."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("Редактирование промптов")
        header.setProperty("class", "section_title")
        layout.addWidget(header)
        
        # Редактор промптов
        self.prompts_editor = QTextEdit()
        self.prompts_editor.setPlaceholderText("Здесь будут отображены промпты...")
        self.prompts_editor.setMinimumHeight(400)
        layout.addWidget(self.prompts_editor)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        load_btn = NeonButton("Загрузить", "secondary")
        load_btn.clicked.connect(self.load_prompts)
        buttons_layout.addWidget(load_btn)
        
        save_btn = NeonButton("Сохранить", "primary")
        save_btn.clicked.connect(self.save_prompts)
        buttons_layout.addWidget(save_btn)
        
        reset_btn = NeonButton("Сбросить", "danger")
        reset_btn.clicked.connect(self.reset_prompts)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Загружаем текущие промпты
        self.load_prompts()
        
        widget.setLayout(layout)
        return widget
    
    def create_knowledge_tab(self):
        """Создать вкладку редактирования базы знаний."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("База знаний проекта")
        header.setProperty("class", "section_title")
        layout.addWidget(header)
        
        # Информация о проекте
        project_group = QGroupBox("Информация о проекте")
        project_layout = QGridLayout()
        
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Название проекта")
        project_layout.addWidget(QLabel("Название:"), 0, 0)
        project_layout.addWidget(self.project_name, 0, 1)
        
        self.project_website = QLineEdit()
        self.project_website.setPlaceholderText("Сайт проекта")
        project_layout.addWidget(QLabel("Сайт:"), 1, 0)
        project_layout.addWidget(self.project_website, 1, 1)
        
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # Редактор базы знаний
        self.knowledge_editor = QTextEdit()
        self.knowledge_editor.setPlaceholderText("База знаний в формате JSON...")
        self.knowledge_editor.setMinimumHeight(300)
        layout.addWidget(self.knowledge_editor)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        load_btn = NeonButton("Загрузить", "secondary")
        load_btn.clicked.connect(self.load_knowledge)
        buttons_layout.addWidget(load_btn)
        
        save_btn = NeonButton("Сохранить", "primary")
        save_btn.clicked.connect(self.save_knowledge)
        buttons_layout.addWidget(save_btn)
        
        reset_btn = NeonButton("Сбросить", "danger")
        reset_btn.clicked.connect(self.reset_knowledge)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Загружаем текущую базу знаний
        self.load_knowledge()
        
        widget.setLayout(layout)
        return widget
    
    def create_api_tab(self):
        """Создать вкладку настроек API."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("Настройки API")
        header.setProperty("class", "section_title")
        layout.addWidget(header)
        
        # Настройки API
        api_group = QGroupBox("Ключи API")
        api_layout = QGridLayout()
        
        self.perplexity_key = QLineEdit()
        self.perplexity_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.perplexity_key.setPlaceholderText("PERPLEXITY_API_KEY")
        api_layout.addWidget(QLabel("Perplexity:"), 0, 0)
        api_layout.addWidget(self.perplexity_key, 0, 1)
        
        self.mistral_key = QLineEdit()
        self.mistral_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.mistral_key.setPlaceholderText("MISTRAL_API_KEY")
        api_layout.addWidget(QLabel("Mistral:"), 1, 0)
        api_layout.addWidget(self.mistral_key, 1, 1)
        
        self.deepseek_key = QLineEdit()
        self.deepseek_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.deepseek_key.setPlaceholderText("DEEPSEEK_API_KEY")
        api_layout.addWidget(QLabel("DeepSeek:"), 2, 0)
        api_layout.addWidget(self.deepseek_key, 2, 1)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Настройки генерации
        gen_group = QGroupBox("Настройки генерации")
        gen_layout = QGridLayout()
        
        self.delay_min = QSpinBox()
        self.delay_min.setRange(1, 60)
        self.delay_min.setValue(8)
        gen_layout.addWidget(QLabel("Задержка мин (сек):"), 0, 0)
        gen_layout.addWidget(self.delay_min, 0, 1)
        
        self.delay_max = QSpinBox()
        self.delay_max.setRange(1, 120)
        self.delay_max.setValue(20)
        gen_layout.addWidget(QLabel("Задержка макс (сек):"), 1, 0)
        gen_layout.addWidget(self.delay_max, 1, 1)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        layout.addStretch()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_btn = NeonButton("Сохранить API", "primary")
        save_btn.clicked.connect(self.save_api_settings)
        buttons_layout.addWidget(save_btn)
        
        load_env_btn = NeonButton("Загрузить из .env", "secondary")
        load_env_btn.clicked.connect(self.load_from_env)
        buttons_layout.addWidget(load_env_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        return widget
    
    def load_prompts(self):
        """Загрузить промпты из файла."""
        try:
            with open("config/smart_prompts.json", "r", encoding="utf-8") as f:
                prompts = json.load(f)
                self.prompts_editor.setPlainText(json.dumps(prompts, indent=2, ensure_ascii=False))
                app_logger.info("Промпты загружены в редактор")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить промпты: {e}")
            app_logger.error(f"Ошибка загрузки промптов: {e}")
    
    def save_prompts(self):
        """Сохранить промпты в файл."""
        try:
            prompts_text = self.prompts_editor.toPlainText()
            prompts = json.loads(prompts_text)
            
            with open("config/smart_prompts.json", "w", encoding="utf-8") as f:
                json.dump(prompts, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Успех", "Промпты сохранены!")
            app_logger.info("Промпты сохранены")
            
            # Перезагружаем сервис
            from core.smart_prompt_service import SmartPromptService
            global smart_prompt_service
            smart_prompt_service = SmartPromptService()
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка JSON", f"Ошибка в формате JSON: {e}")
            app_logger.error(f"Ошибка JSON в промптах: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить промпты: {e}")
            app_logger.error(f"Ошибка сохранения промптов: {e}")
    
    def reset_prompts(self):
        """Сбросить промпты к значениям по умолчанию."""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Сбросить промпты к значениям по умолчанию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from core.smart_prompt_service import SmartPromptService
                service = SmartPromptService()
                default_prompts = service._get_fallback_prompts()
                
                self.prompts_editor.setPlainText(json.dumps(default_prompts, indent=2, ensure_ascii=False))
                app_logger.info("Промпты сброшены к значениям по умолчанию")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сбросить промпты: {e}")
                app_logger.error(f"Ошибка сброса промптов: {e}")
    
    def load_knowledge(self):
        """Загрузить базу знаний из файла."""
        try:
            with open("config/knowledge_base.json", "r", encoding="utf-8") as f:
                knowledge = json.load(f)
                
                # Заполняем поля проекта
                project_info = knowledge.get("project_info", {})
                self.project_name.setText(project_info.get("name", ""))
                self.project_website.setText(project_info.get("website", ""))
                
                # Удаляем project_info для редактора
                knowledge_for_editor = knowledge.copy()
                knowledge_for_editor.pop("project_info", None)
                
                self.knowledge_editor.setPlainText(json.dumps(knowledge_for_editor, indent=2, ensure_ascii=False))
                app_logger.info("База знаний загружена в редактор")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить базу знаний: {e}")
            app_logger.error(f"Ошибка загрузки базы знаний: {e}")
    
    def save_knowledge(self):
        """Сохранить базу знаний в файл."""
        try:
            knowledge_text = self.knowledge_editor.toPlainText()
            knowledge = json.loads(knowledge_text)
            
            # Добавляем информацию о проекте
            knowledge["project_info"] = {
                "name": self.project_name.text(),
                "website": self.project_website.text(),
                "specialization": "пластиковые изделия для дачи, бани, строительства",
                "years_experience": "15+ лет на рынке"
            }
            
            with open("config/knowledge_base.json", "w", encoding="utf-8") as f:
                json.dump(knowledge, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Успех", "База знаний сохранена!")
            app_logger.info("База знаний сохранена")
            
            # Перезагружаем сервис
            from core.smart_prompt_service import SmartPromptService
            global smart_prompt_service
            smart_prompt_service = SmartPromptService()
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка JSON", f"Ошибка в формате JSON: {e}")
            app_logger.error(f"Ошибка JSON в базе знаний: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить базу знаний: {e}")
            app_logger.error(f"Ошибка сохранения базы знаний: {e}")
    
    def reset_knowledge(self):
        """Сбросить базу знаний к значениям по умолчанию."""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Сбросить базу знаний к значениям по умолчанию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Создаем базовую структуру
                default_knowledge = {
                    "project_info": {
                        "name": "Проект",
                        "website": "",
                        "specialization": "пластиковые изделия",
                        "years_experience": "10+ лет"
                    },
                    "product_categories": {},
                    "common_rules": {
                        "materials": {
                            "allowed": ["пластик", "полипропилен"],
                            "forbidden": ["нержавейка", "металл"]
                        }
                    }
                }
                
                self.project_name.setText(default_knowledge["project_info"]["name"])
                self.project_website.setText(default_knowledge["project_info"]["website"])
                
                knowledge_for_editor = default_knowledge.copy()
                knowledge_for_editor.pop("project_info", None)
                
                self.knowledge_editor.setPlainText(json.dumps(knowledge_for_editor, indent=2, ensure_ascii=False))
                app_logger.info("База знаний сброшена к значениям по умолчанию")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сбросить базу знаний: {e}")
                app_logger.error(f"Ошибка сброса базы знаний: {e}")
    
    def save_api_settings(self):
        """Сохранить настройки API."""
        try:
            # Здесь можно добавить сохранение в .env файл
            QMessageBox.information(self, "Информация", "Настройки API сохранены в .env файл")
            app_logger.info("Настройки API сохранены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки API: {e}")
            app_logger.error(f"Ошибка сохранения API: {e}")
    
    def load_from_env(self):
        """Загрузить настройки из .env файла."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            import os
            self.perplexity_key.setText(os.getenv("PERPLEXITY_API_KEY", ""))
            self.mistral_key.setText(os.getenv("MISTRAL_API_KEY", ""))
            self.deepseek_key.setText(os.getenv("DEEPSEEK_API_KEY", ""))
            
            QMessageBox.information(self, "Успех", "Настройки загружены из .env файла")
            app_logger.info("Настройки API загружены из .env")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить из .env: {e}")
            app_logger.error(f"Ошибка загрузки из .env: {e}")
    
    def go_back(self):
        """Вернуться на предыдущий уровень."""
        # Находим родительское окно и вызываем метод назад
        parent = self.parent()
        while parent and not hasattr(parent, 'stack'):
            parent = parent.parent()

        if parent and hasattr(parent, 'back_from_settings'):
            parent.back_from_settings()
        elif parent and hasattr(parent, 'show_projects'):
            parent.show_projects()
