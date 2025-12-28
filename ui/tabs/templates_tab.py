"""
Templates Tab - UI for managing review templates
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QLabel, QSplitter,
    QTextEdit, QLineEdit
)
from PyQt6.QtCore import Qt


class TemplatesTab(QWidget):
    """Tab for managing templates."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the tab UI."""
        layout = QVBoxLayout(self)
        
        # Top toolbar
        toolbar_layout = QHBoxLayout()
        
        self.new_template_btn = QPushButton("Создать шаблон")
        self.new_template_btn.setStyleSheet("background-color: #28a745; color: white; padding: 5px 15px;")
        toolbar_layout.addWidget(self.new_template_btn)
        
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Template List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("Шаблоны:"))
        self.template_list = QListWidget()
        left_layout.addWidget(self.template_list)
        
        splitter.addWidget(left_widget)
        
        # Right side: Template Editor (Preview)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit()
        right_layout.addWidget(self.name_edit)
        
        right_layout.addWidget(QLabel("Содержание:"))
        self.content_edit = QTextEdit()
        right_layout.addWidget(self.content_edit)
        
        self.save_btn = QPushButton("Сохранить")
        right_layout.addWidget(self.save_btn)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 2)  # Give editor more space
        
        layout.addWidget(splitter)
