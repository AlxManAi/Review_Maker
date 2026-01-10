"""
Reviews Tab - UI for generating and viewing reviews
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QComboBox
)
from PyQt6.QtCore import Qt
from ui.components.neon_button import NeonButton


class ReviewsTab(QWidget):
    """Tab for managing and generating reviews."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the tab UI."""
        layout = QVBoxLayout(self)
        
        # Top toolbar
        toolbar_layout = QHBoxLayout()
        
        self.generate_btn = NeonButton("Сгенерировать отзыв", "primary")
        toolbar_layout.addWidget(self.generate_btn)
        
        toolbar_layout.addStretch()
        
        # Filters (Placeholder)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все товары", "Товар 1", "Товар 2"])
        toolbar_layout.addWidget(QLabel("Фильтр:"))
        toolbar_layout.addWidget(self.filter_combo)
        
        layout.addLayout(toolbar_layout)
        
        # Reviews table
        self.reviews_table = QTableWidget()
        self.reviews_table.setColumnCount(5)
        self.reviews_table.setHorizontalHeaderLabels([
            "Товар", "Отзыв", "Оценка", "Дата", "Действия"
        ])
        
        # Table settings
        header = self.reviews_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Content column stretches
        self.reviews_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.reviews_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.reviews_table)
