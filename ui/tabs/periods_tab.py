"""
Periods Tab - UI for managing periods within a project
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QLabel, QFormLayout, QDialogButtonBox,
    QDateEdit, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime, timedelta
from ui.components.neon_button import NeonButton
from ui.components.resizable_widget import ResizableLineEdit
from core.database import db
from core.models import Period


class PeriodDialog(QDialog):
    """Dialog for creating/editing periods."""
    
    def __init__(self, project_id, period=None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.period = period
        self.setWindowTitle("Новый период" if not period else "Редактировать период")
        self.setMinimumWidth(400)
        self._setup_ui()
        
        if period:
            self._load_period()
    
    def _setup_ui(self):
        layout = QFormLayout(self)
        
        # Date pickers
        self.start_edit = QDateEdit()
        self.start_edit.setCalendarPopup(True)
        self.start_edit.setDate(QDate.currentDate())
        self.start_edit.dateChanged.connect(self._on_start_changed)
        
        self.end_edit = QDateEdit()
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setDate(QDate.currentDate().addDays(30))
        
        layout.addRow("Дата начала:", self.start_edit)
        layout.addRow("Дата окончания:", self.end_edit)
        
        self.info_label = QLabel("Период: 30 дней")
        layout.addRow(self.info_label)
        
        # Total reviews count
        from PyQt6.QtWidgets import QSpinBox
        self.total_reviews_edit = QSpinBox()
        self.total_reviews_edit.setMinimum(0)
        self.total_reviews_edit.setMaximum(10000)
        self.total_reviews_edit.setValue(100)
        self.total_reviews_edit.setSuffix(" отзывов")
        layout.addRow("Общее количество отзывов:", self.total_reviews_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _on_start_changed(self, date):
        # Auto-set end date to +30 days
        self.end_edit.setDate(date.addDays(30))
        self._update_info()
    
    def _update_info(self):
        days = self.start_edit.date().daysTo(self.end_edit.date())
        self.info_label.setText(f"Период: {days} дней")
    
    def validate_and_accept(self):
        start = self.start_edit.date().toPyDate()
        end = self.end_edit.date().toPyDate()
        
        if end <= start:
            QMessageBox.warning(self, "Ошибка", "Дата окончания должна быть позже даты начала!")
            return
        
        days_diff = (end - start).days
        if days_diff > 30:
            QMessageBox.warning(self, "Ошибка", f"Период не может превышать 30 дней! (Текущий: {days_diff} дней)")
            return
        
        if self.total_reviews_edit.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Количество отзывов должно быть больше 0!")
            return
        
        self.accept()
    
    def get_data(self):
        return {
            "project_id": self.project_id,
            "start_date": datetime.combine(self.start_edit.date().toPyDate(), datetime.min.time()),
            "end_date": datetime.combine(self.end_edit.date().toPyDate(), datetime.min.time()),
            "total_reviews_count": self.total_reviews_edit.value(),
            "status": "draft"
        }
    
    def _load_period(self):
        """Load existing period data into the dialog."""
        self.start_edit.setDate(QDate(self.period.start_date))
        self.end_edit.setDate(QDate(self.period.end_date))
        self.total_reviews_edit.setValue(self.period.total_reviews_count)
        self._update_info()



class PeriodsTab(QWidget):
    """Tab for displaying periods."""
    
    period_selected = pyqtSignal(int)
    period_updated = pyqtSignal(int)
    back_to_projects = None  # Will be a method from MainWindow
    
    def __init__(self):
        super().__init__()
        self.current_project_id = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Neon кнопки с цветовой схемой "Лед и Пламя"
        self.back_btn = NeonButton("← К проектам", "secondary")  # Оранжевый
        self.back_btn.clicked.connect(lambda: self.back_to_projects() if self.back_to_projects else None)
        toolbar.addWidget(self.back_btn)
        
        self.open_btn = NeonButton("Открыть", "suggested")  # Золотой - рекомендуемое действие
        self.open_btn.clicked.connect(self.open_period)
        self.open_btn.setEnabled(False)
        toolbar.addWidget(self.open_btn)
        
        self.add_btn = NeonButton("Добавить период", "primary")  # Ледяной синий
        self.add_btn.clicked.connect(self.create_period)
        self.add_btn.setEnabled(False)
        toolbar.addWidget(self.add_btn)
        
        self.edit_btn = NeonButton("Редактировать", "secondary")  # Оранжевый
        self.edit_btn.clicked.connect(self.edit_period)
        self.edit_btn.setEnabled(False)
        toolbar.addWidget(self.edit_btn)
        
        self.delete_btn = NeonButton("Удалить период", "secondary")  # Оранжевый
        self.delete_btn.clicked.connect(self.delete_period)
        self.delete_btn.setEnabled(False)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)

        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Начало", "Окончание", "Отзывов", "Создан"])

        header = self.table.horizontalHeader()
        
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(3, 80)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.open_period)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
    
    def set_project(self, project_id):
        self.current_project_id = project_id
        self.add_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.load_periods()
        
    def load_periods(self):
        self.table.setRowCount(0)
        if not self.current_project_id:
            return
        
        # Устанавливаем высоту строк (Compact: 22px)
        self.table.verticalHeader().setDefaultSectionSize(24)
        self.table.verticalHeader().setVisible(False)
        
        with db.get_session() as session:
            periods = session.query(Period).filter_by(project_id=self.current_project_id).order_by(Period.created_at.desc()).all()
            for period in periods:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(period.id)))
                self.table.setItem(row, 1, QTableWidgetItem(period.start_date.strftime("%Y-%m-%d")))
                self.table.setItem(row, 2, QTableWidgetItem(period.end_date.strftime("%Y-%m-%d")))
                self.table.setItem(row, 3, QTableWidgetItem(str(period.total_reviews_count)))
                self.table.setItem(row, 4, QTableWidgetItem(period.created_at.strftime("%Y-%m-%d %H:%M")))

    def create_period(self):
        if not self.current_project_id:
            return
        
        dialog = PeriodDialog(self.current_project_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            with db.get_session() as session:
                period = Period(**data)
                session.add(period)
                session.commit()
            
            self.load_periods()
    
    def edit_period(self):
        """Edit selected period."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите период для редактирования")
            return
        
        period_id = int(self.table.item(row, 0).text())
        
        with db.get_session() as session:
            period = session.query(Period).get(period_id)
            if not period:
                return
            
            # Create dialog with existing period data
            dialog = PeriodDialog(self.current_project_id, period=period, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                # Update period
                period.start_date = data["start_date"]
                period.end_date = data["end_date"]
                period.total_reviews_count = data["total_reviews_count"]
                session.commit()
                
                # Emit signal to update products tab validation
                self.period_updated.emit(period_id)
        
        self.load_periods()

    def open_period(self):
        print("DEBUG: open_period called")
        row = self.table.currentRow()
        if row >= 0:
            period_id = int(self.table.item(row, 0).text())
            print(f"DEBUG: Emitting period_selected for id {period_id}")
            self.period_selected.emit(period_id)
        else:
            print("DEBUG: No row selected or row < 0")
    
    def delete_period(self):
        """Delete selected period."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите период для удаления")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Удалить {len(selected_rows)} период(ов)?\n\n⚠ Будут удалены все товары и отзывы этого периода!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Delete periods
        with db.get_session() as session:
            for row in selected_rows:
                period_id = int(self.table.item(row, 0).text())
                period = session.query(Period).get(period_id)
                if period:
                    session.delete(period)
            session.commit()
        
        self.load_periods()
        QMessageBox.information(self, "Успех", f"Удалено {len(selected_rows)} период(ов)")
