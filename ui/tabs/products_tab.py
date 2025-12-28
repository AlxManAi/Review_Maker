"""
Products Tab - UI for managing product tasks with CSV import
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QMessageBox, QFileDialog, QLabel, QStyledItemDelegate
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.database import db
from core.models import ProductTask


class TableItemDelegate(QStyledItemDelegate):
    """Custom delegate to fix text display during editing."""
    
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        # Set minimum height for editor to prevent text from being squished
        if editor:
            editor.setMinimumHeight(52)  # Увеличена высота для лучшей читаемости
            # Set font size explicitly
            font = QFont()
            font.setPointSize(10)
            editor.setFont(font)
        return editor


class ProductsTab(QWidget):
    """Tab for managing product tasks."""
    
    def __init__(self):
        super().__init__()
        self.current_period_id = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Buttons with consistent styling
        button_style = "padding: 5px 15px;"
        
        self.add_btn = QPushButton("Добавить товар")
        self.add_btn.clicked.connect(self.add_product)
        self.add_btn.setEnabled(False)
        self.add_btn.setStyleSheet(button_style)
        
        self.import_btn = QPushButton("Импорт Excel")
        self.import_btn.clicked.connect(self.import_excel)
        self.import_btn.setEnabled(False)
        self.import_btn.setStyleSheet(button_style)
        
        self.export_btn = QPushButton("Экспорт Excel")
        self.export_btn.clicked.connect(self.export_excel)
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet(button_style)
        
        self.parse_btn = QPushButton("Парсить отзывы")
        self.parse_btn.clicked.connect(self.parse_reviews)
        self.parse_btn.setEnabled(False)
        self.parse_btn.setStyleSheet("background-color: #28a745; color: white; " + button_style)
        
        self.generate_btn = QPushButton("Генерировать отзывы")
        self.generate_btn.clicked.connect(self.generate_reviews)
        self.generate_btn.setEnabled(False)
        self.generate_btn.setStyleSheet("background-color: #007bff; color: white; " + button_style)
        
        
        toolbar.addWidget(self.add_btn)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_products)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white; " + button_style)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addWidget(self.parse_btn)
        toolbar.addStretch()

        toolbar.addWidget(self.generate_btn)
        layout.addLayout(toolbar)


        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Кол-во", "URL товара", "Использован"])
        
        # Set column widths
        self.table.setColumnWidth(0, 50)   # ID - узкая
        self.table.setColumnWidth(2, 80)   # Кол-во - узкая
        self.table.setColumnWidth(4, 100)  # Использован - средняя
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Название - средняя
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # URL - растягивается
        self.table.setColumnWidth(1, 200)  # Название - начальная ширина
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setDefaultSectionSize(55)  # Увеличена высота строки для удобства редактирования
        
        # Set custom delegate to fix editing display
        self.table.setItemDelegate(TableItemDelegate())
        
        # Connect with error handling
        self.table.itemDoubleClicked.connect(self._safe_double_click)
        self.table.itemChanged.connect(self._safe_item_changed)
        layout.addWidget(self.table)
        
        # Review count validation label
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("padding: 5px; font-weight: bold;")
        layout.addWidget(self.validation_label)

    
    def _safe_double_click(self, item):
        """Safe wrapper for double click handler."""
        try:
            self.on_item_double_clicked(item)
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при редактировании:\n{str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(self, "Ошибка", error_msg)
    
    def _safe_item_changed(self, item):
        """Safe wrapper for item changed handler."""
        try:
            self.on_item_changed(item)
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при сохранении:\n{str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(self, "Ошибка", error_msg)

    
    def set_period(self, period_id):
        self.current_period_id = period_id
        self.add_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.parse_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.load_products()
    
    def refresh_validation(self):
        """Public method to refresh validation from external sources."""
        self.update_validation()


    
    def load_products(self):
        self.table.setRowCount(0)
        if not self.current_period_id:
            return
        
        self.table.blockSignals(True)  # Prevent itemChanged during load
        
        # Load products and extract data inside session
        products_data = []
        with db.get_session() as session:
            products = session.query(ProductTask).filter_by(period_id=self.current_period_id).all()
            for product in products:
                products_data.append({
                    'id': product.id,
                    'product_name': product.product_name,
                    'review_count': product.review_count,
                    'product_url': product.product_url,
                    'is_used': product.is_used
                })
        
        # Add rows outside session using extracted data
        for data in products_data:
            self._add_product_row_from_data(data)
        
        self.table.blockSignals(False)
        
        # Update validation after loading
        self.update_validation()
    
    def update_validation(self):
        """Update review count validation label and generate button state."""
        if not self.current_period_id:
            self.validation_label.setText("")
            return
        
        with db.get_session() as session:
            # Get period's total_reviews_count
            from core.models import Period
            period = session.query(Period).get(self.current_period_id)
            if not period:
                return
            
            total_required = period.total_reviews_count
            
            # Calculate sum of product review counts
            from core.models import ProductTask
            products = session.query(ProductTask).filter_by(period_id=self.current_period_id).all()
            total_assigned = sum(p.review_count or 0 for p in products)
            
            # Update label
            if total_assigned == total_required:
                self.validation_label.setText(f"✓ Назначено отзывов: {total_assigned} / {total_required}")
                self.validation_label.setStyleSheet("padding: 5px; font-weight: bold; color: green;")
                self.generate_btn.setEnabled(True)
                self.generate_btn.setToolTip("")
            elif total_assigned < total_required:
                remaining = total_required - total_assigned
                self.validation_label.setText(f"⚠ Назначено отзывов: {total_assigned} / {total_required} (осталось: {remaining})")
                self.validation_label.setStyleSheet("padding: 5px; font-weight: bold; color: orange;")
                self.generate_btn.setEnabled(False)
                self.generate_btn.setToolTip(f"Назначьте ещё {remaining} отзывов для генерации")
            else:
                excess = total_assigned - total_required
                self.validation_label.setText(f"✗ Назначено отзывов: {total_assigned} / {total_required} (лишних: {excess})")
                self.validation_label.setStyleSheet("padding: 5px; font-weight: bold; color: red;")
                self.generate_btn.setEnabled(False)
                self.generate_btn.setToolTip(f"Уберите {excess} отзывов - превышен лимит периода")

    
    def _add_product_row_from_data(self, data):
        """Add product row from data dictionary."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # ID (read-only)
        id_item = QTableWidgetItem(str(data['id']))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, id_item)
        
        # Editable fields (but need double-click to edit)
        name_item = QTableWidgetItem(data['product_name'])
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 1, name_item)
        
        count_item = QTableWidgetItem(str(data['review_count']) if data['review_count'] else "")
        count_item.setFlags(count_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 2, count_item)
        
        url_item = QTableWidgetItem(data['product_url'] or "")
        url_item.setFlags(url_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 3, url_item)
        
        # Checkbox for "Used"
        checkbox_widget = QWidget()
        checkbox = QCheckBox()
        checkbox.setChecked(data['is_used'])
        checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        checkbox.stateChanged.connect(lambda state, pid=data['id']: self.toggle_used(pid, state))
        layout = QHBoxLayout(checkbox_widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 4, checkbox_widget)

    
    def export_excel(self):
        """Export products table to Excel."""
        if not self.current_period_id:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Экспорт Excel", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            from openpyxl import Workbook
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Товары"
            
            # Headers
            headers = ["ID", "Название товара", "Кол-во отзывов", "URL", "Использовано"]
            ws.append(headers)
            
            # Data
            with db.get_session() as session:
                products = session.query(ProductTask).filter_by(period_id=self.current_period_id).all()
                for product in products:
                    ws.append([
                        product.id,
                        product.product_name,
                        product.review_count,
                        product.product_url or "",
                        "Да" if product.is_used else "Нет"
                    ])
            
            wb.save(file_path)
            QMessageBox.information(self, "Успех", f"Экспортировано в {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    
    def on_item_double_clicked(self, item):
        """Double click = enable editing."""
        if item.column() in [0, 4]:  # Skip ID and checkbox
            return
        
        # Use Qt.ItemFlag directly to avoid recursion
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
        self.table.editItem(item)

    
    def add_product(self):
        if not self.current_period_id:
            return
        
        with db.get_session() as session:
            product = ProductTask(
                period_id=self.current_period_id,
                product_name="Новый товар",
                review_count=None,
                product_url=""
            )
            session.add(product)
            session.commit()
        
        # Reload all products to avoid detached instance issues
        self.load_products()
    
    def delete_products(self):
        """Delete selected products."""
        if not self.current_period_id:
            return
        
        # Get selected rows
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите товары для удаления")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Удалить {len(selected_rows)} товар(ов)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # Delete products
        with db.get_session() as session:
            for row in selected_rows:
                product_id = int(self.table.item(row, 0).text())
                product = session.query(ProductTask).get(product_id)
                if product:
                    session.delete(product)
            session.commit()
        
        self.load_products()
        QMessageBox.information(self, "Успех", f"Удалено {len(selected_rows)} товар(ов)")
    
    
    def import_excel(self):
        """Import products from Excel file."""
        if not self.current_period_id:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Импорт Excel", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(file_path)
            ws = wb.active
            
            # Skip header row
            rows = list(ws.iter_rows(min_row=2, values_only=True))
            
            with db.get_session() as session:
                for row in rows:
                    if not row or not row[0]:  # Skip empty rows
                        continue
                    
                    # row format: ID, Название, Кол-во, URL, Использовано
                    product = ProductTask(
                        period_id=self.current_period_id,
                        product_name=row[1] if len(row) > 1 else "Товар",
                        review_count=int(row[2]) if len(row) > 2 and row[2] else None,
                        product_url=row[3] if len(row) > 3 else ""
                    )
                    session.add(product)
                session.commit()
            
            self.load_products()
            QMessageBox.information(self, "Успех", f"Импортировано {len(rows)} товаров")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка импорта: {str(e)}")

    
    def on_item_changed(self, item):
        row = item.row()
        col = item.column()
        
        try:
            product_id = int(self.table.item(row, 0).text())
        except (ValueError, AttributeError):
            return
        
        # Don't try to modify flags - causes recursion in PyQt6
        # Item will be made non-editable on next load
        
        try:
            with db.get_session() as session:
                product = session.query(ProductTask).get(product_id)
                if not product:
                    return
                
                if col == 1:
                    product.product_name = item.text()
                elif col == 2:
                    text = item.text().strip()
                    product.review_count = int(text) if text else None
                elif col == 3:
                    product.product_url = item.text()
                session.commit()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
            self.load_products()  # Reload to reset values
        
        # Update validation after changing review count
        self.update_validation()

    
    def toggle_used(self, product_id, state):
        with db.get_session() as session:
            product = session.query(ProductTask).get(product_id)
            product.is_used = (state == Qt.CheckState.Checked.value)
            session.commit()
    
    def parse_reviews(self):
        """Parse reviews from selected products to build training examples."""
        if not self.current_period_id:
            return
        
        # Get selected products
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите товары для парсинга")
            return
        
        from core.parser_service import parser_service
        
        total_parsed = 0
        errors = []
        
        for row in selected_rows:
            product_id = int(self.table.item(row, 0).text())
            product_name = self.table.item(row, 1).text()
            
            try:
                count, message = parser_service.parse_product_reviews(product_id)
                total_parsed += count
                if count == 0:
                    errors.append(f"{product_name}: {message}")
            except Exception as e:
                errors.append(f"{product_name}: {str(e)}")
        
        # Show results
        result_msg = f"Спарсено {total_parsed} отзывов"
        if errors:
            result_msg += f"\n\nОшибки:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result_msg += f"\n... и ещё {len(errors) - 5} ошибок"
        
        if total_parsed > 0:
            QMessageBox.information(self, "Парсинг завершён", result_msg)
        else:
            QMessageBox.warning(self, "Парсинг завершён", result_msg)
        
        self.load_products()
    
    def generate_reviews(self):
        """Генерация отзывов с помощью AI."""
        # Получить выбранные товары
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите товар(ы)")
            return
        
        product_ids = []
        for row in selected_rows:
            try:
                id_item = self.table.item(row, 0)
                if id_item:
                    product_ids.append(int(id_item.text()))
            except ValueError:
                continue
                
        if not product_ids:
            return
            
        # Проверка (опционально)
        from core.database import db
        from core.models import ProductTask
        
        with db.get_session() as session:
            count = session.query(ProductTask).filter(ProductTask.id.in_(product_ids)).count()
            if count == 0:
                 QMessageBox.warning(self, "Ошибка", "Товары не найдены")
                 return
        
        # Открыть диалог генерации
        from ui.dialogs.generate_dialog import GenerateDialog
        dialog = GenerateDialog(parent=self, product_ids=product_ids)
        if dialog.exec():
            # Обновить валидацию после генерации
            self.update_validation()
            # Обновить валидацию после генерации
            self.update_validation()


