"""
Review Edit Dialog - Диалог просмотра и редактирования отзыва
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QCheckBox, QDialogButtonBox, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import Qt

class ReviewEditDialog(QDialog):
    """Диалог для полного просмотра и редактирования отзыва."""
    
    def __init__(self, review, parent=None):
        super().__init__(parent)
        self.review_id = review.id
        self.setWindowTitle(f"Отзыв #{review.id}")
        self.setMinimumSize(600, 500)
        
        self.init_ui(review)
        
    def init_ui(self, review):
        layout = QVBoxLayout()
        
        # Заголовок
        header = QHBoxLayout()
        
        product_label = QLabel(f"<b>Товар:</b> {review.product_name or '?'}")
        product_label.setStyleSheet("color: #4a9eff; font-size: 14px;")
        header.addWidget(product_label)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Метаданные (Автор, Рейтинг, Дата)
        meta_layout = QHBoxLayout()
        
        # Автор
        self.author_edit = QLineEdit(review.author or "")
        self.author_edit.setPlaceholderText("Имя Фамилия")
        meta_layout.addWidget(QLabel("Автор:"))
        meta_layout.addWidget(self.author_edit)
        
        # Рейтинг
        self.rating_edit = QLineEdit(str(review.rating or 5))
        self.rating_edit.setFixedWidth(50)
        self.rating_edit.setPlaceholderText("1-5")
        meta_layout.addWidget(QLabel("Рейтинг:"))
        meta_layout.addWidget(self.rating_edit)
        
        # Дата (Target Date)
        target_date_str = review.target_date.strftime("%Y-%m-%d") if review.target_date else ""
        self.date_edit = QLineEdit(target_date_str)
        self.date_edit.setPlaceholderText("YYYY-MM-DD")
        meta_layout.addWidget(QLabel("Дата:"))
        meta_layout.addWidget(self.date_edit)
        
        layout.addLayout(meta_layout)
        
        # Текст отзыва
        layout.addWidget(QLabel("<b>Текст отзыва:</b>"))
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(review.content or "")
        layout.addWidget(self.content_edit)
        
        # Плюсы
        layout.addWidget(QLabel("<b>Плюсы:</b>"))
        self.pros_edit = QTextEdit()
        self.pros_edit.setPlainText(review.pros or "")
        self.pros_edit.setMaximumHeight(80)
        layout.addWidget(self.pros_edit)
        
        # Минусы
        layout.addWidget(QLabel("<b>Минусы:</b>"))
        self.cons_edit = QTextEdit()
        self.cons_edit.setPlainText(review.cons or "")
        self.cons_edit.setMaximumHeight(80)
        layout.addWidget(self.cons_edit)
        
        # Статусы
        status_layout = QHBoxLayout()
        
        self.ok_checkbox = QCheckBox("ОК (Утвержден)")
        self.ok_checkbox.setChecked(review.is_approved or False)
        status_layout.addWidget(self.ok_checkbox)
        
        self.used_checkbox = QCheckBox("Использовано (Опубликован)")
        self.used_checkbox.setChecked(review.is_used or False)
        status_layout.addWidget(self.used_checkbox)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_review)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def save_review(self):
        """Сохранить изменения в БД."""
        from datetime import datetime
        
        try:
            # Валидация
            rating = int(self.rating_edit.text())
            if not 1 <= rating <= 5:
                raise ValueError("Рейтинг должен быть от 1 до 5")
            
            date_val = None
            if self.date_edit.text().strip():
                try:
                    date_val = datetime.strptime(self.date_edit.text().strip(), "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Неверный формат даты (YYYY-MM-DD)")
            
            # Сохранение
            from core.database import db
            from core.models import Review
            
            with db.get_session() as session:
                review = session.query(Review).get(self.review_id)
                if review:
                    review.author = self.author_edit.text()
                    review.rating = rating
                    review.target_date = date_val
                    review.content = self.content_edit.toPlainText()
                    review.pros = self.pros_edit.toPlainText()
                    review.cons = self.cons_edit.toPlainText()
                    review.is_approved = self.ok_checkbox.isChecked()
                    review.is_used = self.used_checkbox.isChecked()
                    session.commit()
            
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")
