"""
Projects Tab - UI for managing projects
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QLabel, QLineEdit, QTextEdit, QFormLayout, QDialogButtonBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.components.neon_button import NeonButton
from core.database import db
from core.models import Project


class ProjectDialog(QDialog):
    """Dialog for creating/editing projects."""
    
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Новый проект" if not project else "Редактировать проект")
        self.setMinimumWidth(500)
        self._setup_ui()
        
        if project:
            self._load_project()
    
    def _setup_ui(self):
        layout = QFormLayout(self)
        
        # Используем обычные QLineEdit с правильной шириной
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumWidth(200)
        self.name_edit.setMaximumWidth(400)
        
        self.url_edit = QLineEdit()
        self.url_edit.setMinimumWidth(200)
        self.url_edit.setMaximumWidth(400)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setMinimumWidth(300)
        
        # Загружаем сохраненные размеры полей
        self._load_field_sizes()
        
        layout.addRow("Название:", self.name_edit)
        layout.addRow("URL сайта:", self.url_edit)
        layout.addRow("Описание:", self.desc_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _load_field_sizes(self):
        """Загрузка сохраненных размеров полей"""
        try:
            import json
            import os
            
            settings_file = "field_widths.json"
            settings_path = os.path.join(os.path.dirname(__file__), "..", "..", settings_file)
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    
                # Применяем сохраненные размеры для обычных QLineEdit
                name_id = str(id(self.name_edit))
                url_id = str(id(self.url_edit))
                
                if name_id in settings:
                    width = settings[name_id]
                    self.name_edit.setMinimumWidth(width)
                    self.name_edit.setMaximumWidth(width + 100)  # Небольшой запас
                    
                if url_id in settings:
                    width = settings[url_id]
                    self.url_edit.setMinimumWidth(width)
                    self.url_edit.setMaximumWidth(width + 100)  # Небольшой запас
                    
        except Exception as e:
            print(f"Ошибка загрузки размеров полей: {e}")
    
    def _load_project(self):
        self.name_edit.setText(self.project.name)
        self.url_edit.setText(self.project.site_url)
        self.desc_edit.setPlainText(self.project.description or "")
    
    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "site_url": self.url_edit.text(),
            "description": self.desc_edit.toPlainText()
        }


class ProjectsTab(QWidget):
    """Tab for managing projects."""
    
    project_selected = pyqtSignal(int)  # Emits project_id
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.load_projects()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar with consistent button styling
        toolbar = QHBoxLayout()
        
        # Neon кнопки с цветовой схемой "Лед и Пламя"
        self.new_btn = NeonButton("Новый проект", "primary")  # Ледяной синий
        self.new_btn.clicked.connect(self.create_project)
        toolbar.addWidget(self.new_btn)
        
        self.delete_btn = NeonButton("Удалить", "secondary")  # Оранжевый
        self.delete_btn.clicked.connect(self.delete_project)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "URL сайта", "Создан"])
        
        # Установка регуляторов как в товарах
        self.table.setColumnWidth(0, 50)   # ID - узкая
        self.table.setColumnWidth(1, 200)  # Название - начальная ширина
        self.table.setColumnWidth(2, 250)  # URL - начальная ширина
        self.table.setColumnWidth(3, 150)  # Создан - начальная ширина
        
        # Регуляторы для всех колонок кроме ID
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)      # ID - фиксированная
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # Название - интерактивная
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive) # URL - интерактивная
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Создан - интерактивная
        
        # Соединяем сигнал изменения размеров с сохранением
        self.table.horizontalHeader().sectionResized.connect(self._save_column_sizes)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.open_project)
        layout.addWidget(self.table)
    
    def load_projects(self):
        self.table.setRowCount(0)
        
        # Устанавливаем высоту строк (Golden Air: 26px)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.verticalHeader().setVisible(False)
        
        # Загружаем сохраненные размеры колонок
        self._load_column_sizes()
        
        with db.get_session() as session:
            projects = session.query(Project).order_by(Project.created_at.desc()).all()
            for project in projects:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(project.id)))
                self.table.setItem(row, 1, QTableWidgetItem(project.name))
                self.table.setItem(row, 2, QTableWidgetItem(project.site_url))
                self.table.setItem(row, 3, QTableWidgetItem(project.created_at.strftime("%Y-%m-%d %H:%M")))
    
    def _load_column_sizes(self):
        """Загрузка сохраненных размеров колонок"""
        try:
            import json
            import os
            
            settings_file = "column_widths.json"
            settings_path = os.path.join(os.path.dirname(__file__), "..", "..", settings_file)
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                
                # Применяем сохраненные размеры для колонок проектов
                table_key = "projects_table"
                if table_key in settings:
                    sizes = settings[table_key]
                    if "name" in sizes:
                        self.table.setColumnWidth(1, sizes["name"])
                    if "url" in sizes:
                        self.table.setColumnWidth(2, sizes["url"])
                    if "created" in sizes:
                        self.table.setColumnWidth(3, sizes["created"])
                        
        except Exception as e:
            print(f"Ошибка загрузки размеров колонок: {e}")
    
    def _save_column_sizes(self):
        """Сохранение размеров колонок"""
        try:
            import json
            import os
            
            settings_file = "column_widths.json"
            settings_path = os.path.join(os.path.dirname(__file__), "..", "..", settings_file)
            
            # Загружаем существующие настройки
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            
            # Сохраняем размеры колонок проектов
            table_key = "projects_table"
            settings[table_key] = {
                "name": self.table.columnWidth(1),
                "url": self.table.columnWidth(2),
                "created": self.table.columnWidth(3)
            }
            
            # Записываем настройки
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Ошибка сохранения размеров колонок: {e}")
    
    def resizeEvent(self, event):
        """Сохранение размеров колонок при изменении размера"""
        super().resizeEvent(event)
        # Сохраняем размеры колонок при изменении размера таблицы
        self._save_column_sizes()
    
    def create_project(self):
        dialog = ProjectDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"] or not data["site_url"]:
                QMessageBox.warning(self, "Ошибка", "Название и URL обязательны!")
                return
            
            with db.get_session() as session:
                project = Project(**data)
                session.add(project)
                session.commit()
            
            self.load_projects()
    
    def open_project(self):
        row = self.table.currentRow()
        if row >= 0:
            project_id = int(self.table.item(row, 0).text())
            self.project_selected.emit(project_id)
    
    def delete_project(self):
        """Delete selected project."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите проект для удаления")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Удалить {len(selected_rows)} проект(ов)?\n\n⚠ Будут удалены все периоды, товары и отзывы этого проекта!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Delete projects
        with db.get_session() as session:
            for row in selected_rows:
                project_id = int(self.table.item(row, 0).text())
                project = session.query(Project).get(project_id)
                if project:
                    session.delete(project)
            session.commit()
        
        self.load_projects()
        QMessageBox.information(self, "Успех", f"Удалено {len(selected_rows)} проект(ов)")
