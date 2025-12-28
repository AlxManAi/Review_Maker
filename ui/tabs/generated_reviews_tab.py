"""
Calendar Reviews Tab - Календарный просмотр отзывов
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QMessageBox, QCheckBox,
    QTextEdit, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime, timedelta


class ReviewCard(QFrame):
    """Карточка отзыва."""
    
    approved_changed = pyqtSignal(int, bool)  # review_id, is_approved
    used_changed = pyqtSignal(int, bool)  # review_id, is_used
    
    def __init__(self, review, parent=None):
        super().__init__(parent)
        self.review_id = review.id
        self.init_ui(review)
    
    def init_ui(self, review):
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            ReviewCard {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            ReviewCard:hover {
                border: 1px solid #666;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)
        
        # Заголовок: Товар + чекбоксы
        header = QHBoxLayout()
        
        product_label = QLabel(f"<b>{review.product_name or 'Товар'}</b>")
        product_label.setStyleSheet("color: #4a9eff;")
        header.addWidget(product_label)
        
        header.addStretch()
        
        # Чекбокс ОК
        self.ok_checkbox = QCheckBox("ОК")
        self.ok_checkbox.setChecked(review.is_approved or False)
        self.ok_checkbox.stateChanged.connect(
            lambda state: self.approved_changed.emit(self.review_id, state == Qt.CheckState.Checked.value)
        )
        header.addWidget(self.ok_checkbox)
        
        # Чекбокс Использовано
        self.used_checkbox = QCheckBox("Использовано")
        self.used_checkbox.setChecked(review.is_used or False)
        self.used_checkbox.stateChanged.connect(
            lambda state: self.used_changed.emit(self.review_id, state == Qt.CheckState.Checked.value)
        )
        header.addWidget(self.used_checkbox)
        
        # Кнопка Открыть ->
        self.open_btn = QPushButton("📝")
        self.open_btn.setFixedSize(30, 25)
        self.open_btn.setToolTip("Открыть полное редактирование")
        # Мы не можем сразу подключить к методу родителя здесь легко без сигнала
        # Поэтому добавим сигнал clicked и пробросим
        # Или просто public метод
        header.addWidget(self.open_btn)
        
        layout.addLayout(header)
        
        # Автор + Рейтинг
        author_rating = QLabel(f"👤 {review.author or 'Аноним'} | ⭐ {review.rating or 5}")
        author_rating.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(author_rating)
        
        # Текст отзыва (кликабельный для открытия)
        # Сделаем кнопку прозрачную поверх или просто кнопку "Открыть" выше
        
        text_edit = QTextEdit()
        text_edit.setPlainText(review.content or "")
        text_edit.setMinimumHeight(80)
        text_edit.setMaximumHeight(120)
        text_edit.setReadOnly(True) # Только для чтения здесь, редактируем в диалоге
        text_edit.setStyleSheet("background-color: #222; color: #ccc; border: none;")
        layout.addWidget(text_edit)
        
        # Плюсы
        if review.pros:
            pros_label = QLabel(f"<b>➕ Плюсы:</b> {review.pros[:50]}...")
            pros_label.setStyleSheet("color: #5cb85c; font-size: 11px;")
            layout.addWidget(pros_label)
        
        self.setLayout(layout)

    
class DayContainer(QFrame):
    """Контейнер дня (вертикальный список дней)."""
    
    def __init__(self, date, parent=None):
        super().__init__(parent)
        self.date = date
        self.setAcceptDrops(True) # Включаем прием дропов для перетаскивания
        self.init_ui()
    
    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.setStyleSheet("""
            DayContainer {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 5px;
                margin-bottom: 5px;
            }
        """)
        
        # Основной вертикальный лейаут дня
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # Заголовок дня
        header_layout = QHBoxLayout()
        day_label = QLabel(self.date.strftime("%d.%m.%Y (%A)"))
        day_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #eee;")
        header_layout.addWidget(day_label)
        header_layout.addStretch()
        
        self.layout.addLayout(header_layout)
        
        # Область для карточек отзывов
        self.reviews_area = QVBoxLayout()
        self.reviews_area.setSpacing(5)
        self.layout.addLayout(self.reviews_area)
        
        self.setLayout(self.layout)
    
    def add_review(self, review_card):
        self.reviews_area.addWidget(review_card)


class GeneratedReviewsTab(QWidget):
    """Вкладка с календарным просмотром отзывов."""
    
    def __init__(self):
        super().__init__()
        self.current_period_id = None
        self.period_start = None
        self.period_end = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Статистика и инфо
        self.stats_label = QLabel("Выберите период для просмотра отзывов")
        self.stats_label.setStyleSheet("font-size: 14px; padding: 10px; background-color: #2d2d2d; border-radius: 5px;")
        layout.addWidget(self.stats_label)
        
        # Тулбар
        toolbar = QHBoxLayout()
        
        self.distribute_btn = QPushButton("Распределить по датам")
        self.distribute_btn.clicked.connect(self.distribute_reviews_action)
        self.distribute_btn.setStyleSheet("background-color: #17a2b8; color: white; padding: 5px 15px;")
        toolbar.addWidget(self.distribute_btn)

        self.clear_btn = QPushButton("Очистить все")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setEnabled(False)
        self.clear_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 5px 15px;")
        toolbar.addWidget(self.clear_btn)
        
        toolbar.addStretch()
        
        self.export_btn = QPushButton("Экспорт Excel")
        self.export_btn.clicked.connect(self.export_excel)
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("background-color: #28a745; color: white; padding: 5px 15px;")
        toolbar.addWidget(self.export_btn)
        
        layout.addLayout(toolbar)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Контейнер для списка дней (Вертикальный)
        self.days_container = QWidget()
        self.days_layout = QVBoxLayout() # Дни идут друг под другом
        self.days_layout.setSpacing(10)
        self.days_layout.addStretch() # Чтобы дни прижимались к верху
        self.days_container.setLayout(self.days_layout)
        
        scroll.setWidget(self.days_container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def open_review_dialog(self, review_card):
        """Открыть диалог редактирования отзыва."""
        from ui.dialogs.review_edit_dialog import ReviewEditDialog
        from core.database import db
        from core.models import Review
        
        with db.get_session() as session:
            review = session.query(Review).get(review_card.review_id)
            if review:
                dialog = ReviewEditDialog(review, parent=self)
                if dialog.exec():
                    # Перезагружаем интерфейс после сохранения
                    self.load_reviews()
    
    def set_period(self, period_id):
        """Установить период для просмотра."""
        from core.database import db
        from core.models import Period
        
        with db.get_session() as session:
            period = session.query(Period).get(period_id)
            if period:
                self.current_period_id = period_id
                self.period_start = period.start_date
                self.period_end = period.end_date
                
                self.clear_btn.setEnabled(True)
                self.export_btn.setEnabled(True)
                
                self.load_reviews()
    
    def load_reviews(self):
        """Загрузить отзывы и отрисовать календарь."""
        # Очистка текущих дней
        # Важно: удаляем виджеты правильно из layout
        while self.days_layout.count():
            item = self.days_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Если вдруг там layout (хотя мы кладем виджеты)
                pass

        if not self.current_period_id or not self.period_start or not self.period_end:
            return
            
        # Восстанавливаем stretch в конце
        self.days_layout.addStretch()

        from core.database import db
        from core.models import Review
        
        with db.get_session() as session:
            # Получить все сгенерированные отзывы
            reviews = session.query(Review).filter_by(
                period_id=self.current_period_id,
                is_generated=True
            ).all()
            
            # Проверяем, есть ли отзывы без даты. Если есть - предлагаем или делаем распределение
            reviews_without_date = [r for r in reviews if not r.target_date]
            if reviews_without_date:
                print(f"Найдено {len(reviews_without_date)} отзывов без даты. Запускаю авто-распределение.")
                self._distribute_reviews_logic(session, reviews_without_date, self.period_start, self.period_end)
                # Перезагружаем список обновленных отзывов
                reviews = session.query(Review).filter_by(
                    period_id=self.current_period_id,
                    is_generated=True
                ).order_by(Review.target_date).all()
            
            # Статистика
            self.stats_label.setText(f"<b>Сгенерировано отзывов:</b> {len(reviews)}")
            
            # Группируем отзывы по датам
            reviews_by_date = {}
            for r in reviews:
                if r.target_date:
                    d = r.target_date.date() if isinstance(r.target_date, datetime) else r.target_date
                    if d not in reviews_by_date:
                        reviews_by_date[d] = []
                    reviews_by_date[d].append(r)
            
            # Отрисовываем дни
            current_date = self.period_start.date() if isinstance(self.period_start, datetime) else self.period_start
            end_date = self.period_end.date() if isinstance(self.period_end, datetime) else self.period_end
            
            # Вставляем дни ПЕРЕД stretch (который последний)
            insert_pos = 0
            
            while current_date <= end_date:
                day_container = DayContainer(current_date)
                
                # Если есть отзывы на эту дату - добавляем их
                if current_date in reviews_by_date:
                    for review in reviews_by_date[current_date]:
                        card = ReviewCard(review)
                        card.approved_changed.connect(self.on_approved_changed)
                        card.used_changed.connect(self.on_used_changed)
                        # Подключаем кнопку открытия
                        card.open_btn.clicked.connect(lambda checked, c=card: self.open_review_dialog(c))
                        
                        day_container.add_review(card)
                
                self.days_layout.insertWidget(insert_pos, day_container)
                insert_pos += 1
                current_date += timedelta(days=1)



    def distribute_reviews_action(self):
        """Ручной вызов перераспределения."""
        if not self.current_period_id: 
            return
            
        from core.database import db
        from core.models import Review
        
        with db.get_session() as session:
            reviews = session.query(Review).filter_by(
                period_id=self.current_period_id,
                is_generated=True
            ).all()
            
            self._distribute_reviews_logic(session, reviews, self.period_start, self.period_end)
            
        self.load_reviews()

    def _distribute_reviews_logic(self, session, reviews, start_date, end_date):
        """Логика распределения отзывов по датам."""
        if not reviews:
            return

        total_days = (end_date - start_date).days + 1
        if total_days <= 0: total_days = 1
        
        # Простая логика: равномерно размазать
        # Можно улучшить: "схожие отзывы подальше" (пока просто round-robin)
        
        import random
        
        # Преобразуем start_date в datetime если надо
        curr = start_date
        
        # Шаг распределения: если отзывов меньше чем дней, кидаем случайно или равномерно
        # Если отзывов больше - заполняем каждый день
        
        # Создаем список всех доступных дат
        all_dates = [start_date + timedelta(days=i) for i in range(total_days)]
        
        # Перемешиваем отзывы чтобы схожие (которые часто идут подряд при генерации) встали в разные места
        # Но пользователь просил "схожие подальше". Если мы их генерили пачкой для одного товара, они мб подряд.
        # Random shuffle неплохо справляется с базовым разбросом.
        reviews_to_update = list(reviews)
        random.shuffle(reviews_to_update)
        
        # Распределяем
        for i, review in enumerate(reviews_to_update):
            # i % total_days дает индекс даты. Это обеспечит равномерное заполнение.
            date_idx = i % total_days
            target_date = all_dates[date_idx]
            
            review.target_date = target_date
            
        session.commit()

    
    def on_approved_changed(self, review_id, is_approved):
        """Обработать изменение чекбокса ОК."""
        from core.database import db
        from core.models import Review
        
        with db.get_session() as session:
            review = session.query(Review).get(review_id)
            if review:
                review.is_approved = is_approved
                session.commit()
    
    def on_used_changed(self, review_id, is_used):
        """Обработать изменение чекбокса Использовано."""
        from core.database import db
        from core.models import Review
        
        with db.get_session() as session:
            review = session.query(Review).get(review_id)
            if review:
                review.is_used = is_used
                session.commit()
    
    def clear_all(self):
        """Очистить все отзывы периода."""
        if not self.current_period_id:
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Удалить ВСЕ сгенерированные отзывы этого периода?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from core.database import db
            from core.models import Review
            
            with db.get_session() as session:
                deleted = session.query(Review).filter_by(
                    period_id=self.current_period_id,
                    is_generated=True
                ).delete()
                session.commit()
            
            QMessageBox.information(self, "Успех", f"Удалено {deleted} отзывов")
            self.load_reviews()
    
    def export_excel(self):
        """Экспорт отзывов в Excel."""
        QMessageBox.information(self, "Экспорт", "Функция экспорта будет реализована")
