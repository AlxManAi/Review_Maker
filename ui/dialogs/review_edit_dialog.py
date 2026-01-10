"""
Review Edit Dialog - Диалог просмотра и редактирования отзыва
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QCheckBox, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import Qt
from core.logger import app_logger

from ui.components.neon_button import NeonButton

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
        
        # URL размещения
        url_layout = QHBoxLayout()
        self.url_edit = QLineEdit(review.placement_url or "")
        self.url_edit.setPlaceholderText("URL размещения отзыва...")
        url_layout.addWidget(QLabel("URL:"))
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)
        
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
        
        # Статусы и Кнопки в одном ряду для гармонии
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(15, 20, 15, 15) # Больше отступов для "воздуха"
        bottom_layout.setSpacing(30)
        
        # Левая часть: Статусы
        status_sub_layout = QVBoxLayout()
        status_sub_layout.setSpacing(8)
        self.ok_checkbox = QCheckBox("Утверждаю")
        self.ok_checkbox.setChecked(review.is_approved or False)
        self.ok_checkbox.setStyleSheet("color: #cdd6f4; font-size: 14px;") # Убрано font-weight: bold
        status_sub_layout.addWidget(self.ok_checkbox)
        
        self.used_checkbox = QCheckBox("Размещен")
        self.used_checkbox.setChecked(review.is_used or False)
        self.used_checkbox.setStyleSheet("color: #cdd6f4; font-size: 14px;") # Убрано font-weight: bold
        status_sub_layout.addWidget(self.used_checkbox)
        bottom_layout.addLayout(status_sub_layout)
        
        bottom_layout.addStretch() # Отступ между статусами и кнопками
        
        # Правая часть: Кнопки
        buttons_sub_layout = QHBoxLayout()
        buttons_sub_layout.setSpacing(12)
        
        # 1. Сохранить (primary - синий контур)
        self.save_btn = NeonButton("Сохранить", "primary")
        self.save_btn.clicked.connect(self.save_review)
        buttons_sub_layout.addWidget(self.save_btn)
        
        # 2. Удалить (danger - красный контур)
        self.delete_btn = NeonButton("Удалить отзыв", "danger")
        self.delete_btn.clicked.connect(self.delete_review)
        buttons_sub_layout.addWidget(self.delete_btn)
        
        # 3. Отмена (secondary - серый контур)
        self.cancel_btn = NeonButton("Отмена", "secondary")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_sub_layout.addWidget(self.cancel_btn)
        
        bottom_layout.addLayout(buttons_sub_layout)
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        # Общие отступы всего окна
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
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
                    review.placement_url = self.url_edit.text()
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
    
    def delete_review(self):
        """Удалить отзыв из БД."""
        reply = QMessageBox.question(
            self, 
            "Подтверждение удаления", 
            "Вы уверены, что хотите удалить этот отзыв?\n\nЭто действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from core.database import db
                from core.models import Review
                from core.logger import app_logger
                
                # Проверяем что review_id существует
                if not hasattr(self, 'review_id') or not self.review_id:
                    QMessageBox.warning(self, "Ошибка", "ID отзыва не указан")
                    return
                
                with db.get_session() as session:
                    review = session.query(Review).get(self.review_id)
                    if not review:
                        QMessageBox.warning(self, "Ошибка", f"Отзыв с ID {self.review_id} не найден")
                        return
                    
                    # Проверяем что отзыв не принят или использован
                    if review.is_approved or review.is_used:
                        QMessageBox.warning(
                            self, 
                            "Ошибка", 
                            "Нельзя удалить принятый или использованный отзыв"
                        )
                        return
                    
                    # Удаляем отзыв
                    app_logger.info(f"Удаление отзыва ID: {self.review_id}")
                    session.delete(review)
                    session.commit()
                    
                    QMessageBox.information(self, "Успех", "Отзыв успешно удален")
                    self.accept()  # Закрываем диалог после удаления
                    
            except Exception as e:
                try:
                    from core.logger import app_logger
                    app_logger.error(f"Ошибка при удалении отзыва: {e}")
                    app_logger.exception("Full traceback:")
                except:
                    pass  # Если даже логгер не работает
                QMessageBox.critical(
                    self, 
                    "Ошибка", 
                    f"Не удалось удалить отзыв:\n{str(e)}"
                )
