"""
Projects Tab - UI for managing projects
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QLabel, QLineEdit, QTextEdit, QFormLayout, QDialogButtonBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
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
        
        self.name_edit = QLineEdit()
        self.url_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        
        layout.addRow("Название:", self.name_edit)
        layout.addRow("URL сайта:", self.url_edit)
        layout.addRow("Описание:", self.desc_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
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
        button_style = "padding: 5px 15px;"
        
        self.new_btn = QPushButton("Новый проект")
        self.new_btn.clicked.connect(self.create_project)
        self.new_btn.setStyleSheet(button_style)
        toolbar.addWidget(self.new_btn)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_project)
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white; " + button_style)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "URL сайта", "Создан"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.open_project)
        layout.addWidget(self.table)
    
    def load_projects(self):
        self.table.setRowCount(0)
        with db.get_session() as session:
            projects = session.query(Project).order_by(Project.created_at.desc()).all()
            for project in projects:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(project.id)))
                self.table.setItem(row, 1, QTableWidgetItem(project.name))
                self.table.setItem(row, 2, QTableWidgetItem(project.site_url))
                self.table.setItem(row, 3, QTableWidgetItem(project.created_at.strftime("%Y-%m-%d %H:%M")))
    
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
