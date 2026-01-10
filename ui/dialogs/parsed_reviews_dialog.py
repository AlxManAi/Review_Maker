"""
Parsed Reviews Dialog - Dialog for reviewing and approving parsed reviews
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QMessageBox, QScrollArea,
    QWidget, QCheckBox, QFrame, QSpinBox
)
from PyQt6.QtCore import Qt
from core.database import db
from core.models import ReviewExample
from datetime import datetime
from ui.components.neon_button import NeonButton


class ParsedReviewCard(QFrame):
    """Карточка спарсенного отзыва"""
    
    def __init__(self, review, parent=None):
        super().__init__(parent)
        self.review = review
        self.approved = False
        self.init_ui()
    
    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            ParsedReviewCard {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Заголовок
        header = QHBoxLayout()
        
        # Чекбокс для утверждения
        self.approve_cb = QCheckBox("Одобрить")
        self.approve_cb.setChecked(False)
        self.approve_cb.stateChanged.connect(self.on_approve_changed)
        header.addWidget(self.approve_cb)
        
        # Автор и рейтинг
        author_rating = QLabel(f"<b>{self.review.author or 'Аноним'}</b> ({self.review.rating or 5}★)")
        author_rating.setStyleSheet("color: #4a9eff; font-size: 14px;")
        header.addWidget(author_rating)
        
        # Дата
        if self.review.review_date:
            date_label = QLabel(self.review.review_date.strftime("%d.%m.%Y"))
            date_label.setStyleSheet("color: #888; font-size: 12px;")
            header.addWidget(date_label)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Текст отзыва
        content = QTextEdit()
        content.setPlainText(self.review.content or "")
        content.setReadOnly(True)
        content.setFixedHeight(80)
        content.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ccc;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        layout.addWidget(content)
        
        # Плюсы и минусы
        if self.review.pros:
            pros_label = QLabel(f"<b>➕ Плюсы:</b> {self.review.pros}")
            pros_label.setStyleSheet("color: #5cb85c; font-size: 11px;")
            layout.addWidget(pros_label)
        
        if self.review.cons:
            cons_label = QLabel(f"<b>➖ Минусы:</b> {self.review.cons}")
            cons_label.setStyleSheet("color: #d9534f; font-size: 11px;")
            layout.addWidget(cons_label)
        
        self.setLayout(layout)
    
    def on_approve_changed(self, state):
        """Обработать изменение чекбокса"""
        self.approved = (state == Qt.CheckState.Checked.value)
    
    def is_approved(self):
        """Проверить, одобрен ли отзыв"""
        return self.approved


class ParsedReviewsDialog(QDialog):
    """Диалог для просмотра спарсенных отзывов"""
    
    def __init__(self, product_ids, parent=None):
        super().__init__(parent)
        self.product_ids = product_ids
        self.review_cards = []
        self.init_ui()
        self.load_reviews()
    
    def init_ui(self):
        self.setWindowTitle("Спарсенные отзывы")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("Просмотр и утверждение спарсенных отзывов")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Информация
        info = QLabel("Отметьте отзывы, которые хотите использовать как примеры для генерации")
        info.setStyleSheet("color: #888; font-size: 12px; padding-bottom: 10px;")
        layout.addWidget(info)
        
        # Scroll area для отзывов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.reviews_container = QWidget()
        self.reviews_layout = QVBoxLayout()
        self.reviews_container.setLayout(self.reviews_layout)
        scroll.setWidget(self.reviews_container)
        layout.addWidget(scroll)
        
        # Кнопки
        buttons = QHBoxLayout()
        
        self.approve_btn = NeonButton("Одобрить выбранные", "primary")
        self.approve_btn.clicked.connect(self.approve_selected)
        
        self.reject_btn = NeonButton("Отклонить все", "danger")
        self.reject_btn.clicked.connect(self.reject_all)
        
        self.close_btn = NeonButton("Закрыть", "secondary")
        self.close_btn.clicked.connect(self.accept)
        
        buttons.addWidget(self.approve_btn)
        buttons.addWidget(self.reject_btn)
        buttons.addStretch()
        buttons.addWidget(self.close_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def load_reviews(self):
        """Загрузить спарсенные отзывы"""
        from core.models import ProductTask
        
        try:
            with db.get_session() as session:
                # Получаем названия товаров для информации
                products = session.query(ProductTask).filter(
                    ProductTask.id.in_(self.product_ids)
                ).all()
                product_names = {p.id: p.product_name for p in products}
                
                # Получаем отзывы для всех товаров
                reviews = session.query(ReviewExample).filter(
                    ReviewExample.product_name.in_(product_names.values())
                ).order_by(ReviewExample.created_at.desc()).all()
                
                if not reviews:
                    no_reviews = QLabel("Спарсенные отзывы не найдены")
                    no_reviews.setStyleSheet("color: #888; text-align: center; padding: 20px;")
                    self.reviews_layout.addWidget(no_reviews)
                    return
                
                # Создаем карточки для каждого отзыва
                for review in reviews:
                    card = ParsedReviewCard(review)
                    self.review_cards.append(card)
                    self.reviews_layout.addWidget(card)
                
                # Добавляем растяжение в конце
                self.reviews_layout.addStretch()
                
        except Exception as e:
            error_label = QLabel(f"Ошибка загрузки отзывов: {str(e)}")
            error_label.setStyleSheet("color: #d9534f; padding: 20px;")
            self.reviews_layout.addWidget(error_label)
    
    def approve_selected(self):
        """Одобрить выбранные отзывы"""
        approved_count = 0
        try:
            with db.get_session() as session:
                for card in self.review_cards:
                    if card.is_approved():
                        # Отмечаем как хороший пример
                        card.review.is_good_example = True
                        card.review.approved_at = datetime.utcnow()
                        session.merge(card.review)
                        approved_count += 1
                
                session.commit()
                
                QMessageBox.information(
                    self, 
                    "Успех", 
                    f"Одобрено {approved_count} отзывов"
                )
                
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Ошибка", 
                f"Ошибка при сохранении: {str(e)}"
            )
    
    def reject_all(self):
        """Отклонить все отзывы"""
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Удалить все спарсенные отзывы?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with db.get_session() as session:
                    # Удаляем все отзывы для этих товаров
                    from core.models import ProductTask
                    products = session.query(ProductTask).filter(
                        ProductTask.id.in_(self.product_ids)
                    ).all()
                    product_names = {p.id: p.product_name for p in products}
                    
                    deleted = session.query(ReviewExample).filter(
                        ReviewExample.product_name.in_(product_names.values())
                    ).delete()
                    
                    session.commit()
                    
                    QMessageBox.information(
                        self, 
                        "Успех", 
                        f"Удалено {deleted} отзывов"
                    )
                    
                    self.accept()
                    
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Ошибка", 
                    f"Ошибка при удалении: {str(e)}"
                )
