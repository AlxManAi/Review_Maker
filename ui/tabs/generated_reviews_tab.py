"""
Calendar Reviews Tab - Календарный просмотр отзывов
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QMessageBox, QCheckBox,
    QTextEdit, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime, timedelta
from ui.components.neon_button import NeonButton


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
        self.setStyleSheet(f"""
            ReviewCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #1e1e2e);
                border: 1px solid #4A90E2;  /* Ледяной синий */
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }}
            ReviewCard:hover {{
                border: 2px solid #87CEEB;  /* Голубой при наведении */
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)
        
        # Заголовок: Товар + чекбоксы
        header = QHBoxLayout()
        
        product_label = QLabel(f"<b>{review.product_name or 'Товар'}</b>")
        product_label.setStyleSheet("color: #4A90E2;")  # Ледяной синий
        header.addWidget(product_label)
        
        header.addStretch()
        
        # Маленькие чекбоксы как в других разделах
        self.approved_checkbox = QCheckBox("")
        self.approved_checkbox.setChecked(review.is_approved)
        self.approved_checkbox.setStyleSheet("""
            QCheckBox::indicator { 
                width: 12px; 
                height: 12px; 
                border: 1px solid #585b70;
                background-color: #313244;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #0000FF;
                border-color: #0000FF;
            }
        """)
        
        def on_approved_changed(v):
            self.approved_changed.emit(review.id, v)
        
        self.approved_checkbox.toggled.connect(on_approved_changed)
        header.addWidget(self.approved_checkbox)
        
        self.used_checkbox = QCheckBox("")
        self.used_checkbox.setChecked(review.is_used)
        self.used_checkbox.setStyleSheet("""
            QCheckBox::indicator { 
                width: 12px; 
                height: 12px; 
                border: 1px solid #585b70;
                background-color: #313244;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #0000FF;
                border-color: #0000FF;
            }
        """)
        
        def on_used_changed(v):
            self.used_changed.emit(review.id, v)
        
        self.used_checkbox.toggled.connect(on_used_changed)
        header.addWidget(self.used_checkbox)
        
        # Кнопка Открыть ->
        self.open_btn = NeonButton("📝", "secondary")  # Оранжевый
        self.open_btn.setFixedSize(30, 25)
        self.open_btn.setToolTip("Открыть полное редактирование")
        header.addWidget(self.open_btn)
        
        layout.addLayout(header)
        
        # Автор + Рейтинг
        author_rating = QLabel(f"👤 {review.author or 'Аноним'} | ⭐ {review.rating or 5}")
        author_rating.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(author_rating)
        
        # Текст отзыва с точной высотой 18px
        text_edit = QTextEdit()
        text_edit.setPlainText(review.content or "")
        text_edit.setFixedHeight(18)  # ТОЧНАЯ высота: шрифт 14px + 4px = 18px
        text_edit.setReadOnly(True) # Только для чтения здесь, редактируем в диалоге
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #222;
                color: #ccc;
                border: none;
                font-family: "Inter", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                padding: 2px;
                line-height: 1.0;
            }
        """)
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
        day_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #eee; padding: 5px;")
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
        
        # Информация о товарах без отзывов
        self.missing_reviews_label = QLabel("")
        self.missing_reviews_label.setStyleSheet("font-size: 12px; padding: 8px; background-color: #ff6b6b; color: white; border-radius: 5px; margin: 5px 0;")
        self.missing_reviews_label.setWordWrap(True)
        self.missing_reviews_label.hide()  # Скрыто по умолчанию
        layout.addWidget(self.missing_reviews_label)
        
        # Тулбар
        toolbar = QHBoxLayout()
        
        # Neon кнопки с цветовой схемой "Лед и Пламя"
        self.distribute_btn = NeonButton("Распределить по датам", "primary")  # Ледяной синий
        self.distribute_btn.clicked.connect(self.distribute_reviews_action)
        toolbar.addWidget(self.distribute_btn)

        self.clear_btn = NeonButton("Очистить все", "secondary")  # Оранжевый
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setEnabled(False)
        toolbar.addWidget(self.clear_btn)
        
        toolbar.addStretch()
        
        self.export_btn = NeonButton("Экспорт Excel", "suggested")  # Золотой - рекомендуемое
        self.export_btn.clicked.connect(self.export_excel)
        self.export_btn.setEnabled(False)
        toolbar.addWidget(self.export_btn)
        
        self.generate_missing_btn = NeonButton("Генерировать недостающие", "secondary")
        self.generate_missing_btn.clicked.connect(self.generate_missing_reviews)
        self.generate_missing_btn.setEnabled(False)
        self.generate_missing_btn.hide()  # Скрыта по умолчанию
        toolbar.addWidget(self.generate_missing_btn)
        
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
                
                # Проверяем условия для активации экспорта
                self._update_export_button_state()
                
                self.load_reviews()
    
    def _check_missing_reviews(self):
        """Проверить товары без отзывов и показать информацию."""
        if not self.current_period_id:
            self.missing_reviews_label.hide()
            return
        
        from core.database import db
        from core.models import ProductTask, Review
        
        with db.get_session() as session:
            # Получаем все товары периода
            products = session.query(ProductTask).filter_by(
                period_id=self.current_period_id
            ).all()
            
            if not products:
                self.missing_reviews_label.hide()
                return
            
            # Получаем товары с отзывами
            products_with_reviews = session.query(Review.product_task_id).filter_by(
                period_id=self.current_period_id,
                is_generated=True
            ).distinct().all()
            
            # Находим товары без отзывов
            products_with_reviews_ids = [p[0] for p in products_with_reviews]
            missing_products = [p for p in products if p.id not in products_with_reviews_ids]
            
            if missing_products:
                # Показываем информацию о товарах без отзывов
                product_names = [p.product_name for p in missing_products]
                text = f"⚠️ Товары без отзывов ({len(missing_products)}):\n"
                text += "\n".join([f"• {name}" for name in product_names[:5]])  # Показываем первые 5
                
                if len(missing_products) > 5:
                    text += f"\n• ... и еще {len(missing_products) - 5} товаров"
                
                self.missing_reviews_label.setText(text)
                self.missing_reviews_label.show()
                
                # Показываем кнопку генерации недостающих
                self.generate_missing_btn.show()
                self.generate_missing_btn.setEnabled(True)
                self.generate_missing_btn.setText(f"Генерировать недостающие ({len(missing_products)})")
            else:
                self.missing_reviews_label.hide()
                self.generate_missing_btn.hide()
                self.generate_missing_btn.setEnabled(False)
    
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
            
            # Проверяем товары без отзывов
            self._check_missing_reviews()
            
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
        """Обработать изменение чекбокса ОК с обработкой ошибок."""
        try:
            from core.database import db
            from core.models import Review
            
            with db.get_session() as session:
                review = session.query(Review).get(review_id)
                if review:
                    review.is_approved = is_approved
                    session.commit()
                else:
                    print(f"Ошибка: Отзыв с ID {review_id} не найден")
            
            # Обновляем состояние кнопки экспорта
            self._update_export_button_state()
        except Exception as e:
            print(f"Ошибка при изменении статуса утверждения: {e}")
    
    def on_used_changed(self, review_id, is_used):
        """Обработать изменение чекбокса Использовано с обработкой ошибок."""
        try:
            from core.database import db
            from core.models import Review
            
            with db.get_session() as session:
                review = session.query(Review).get(review_id)
                if review:
                    review.is_used = is_used
                    session.commit()
                else:
                    print(f"Ошибка: Отзыв с ID {review_id} не найден")
            
            # Обновляем состояние кнопки экспорта
            self._update_export_button_state()
        except Exception as e:
            print(f"Ошибка при изменении статуса использования: {e}")
    
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
    
    def _update_export_button_state(self):
        """Обновить состояние кнопки экспорта."""
        if not self.current_period_id:
            self.export_btn.setEnabled(False)
            return
        
        from core.database import db
        from core.models import Review
        
        with db.get_session() as session:
            # Проверяем все отзывы для периода
            total_reviews = session.query(Review).filter_by(
                period_id=self.current_period_id,
                is_generated=True
            ).count()
            
            if total_reviews == 0:
                self.export_btn.setEnabled(False)
                self.export_btn.setToolTip("Нет отзывов для экспорта")
                return
            
            # Проверяем что все отзывы приняты
            approved_reviews = session.query(Review).filter_by(
                period_id=self.current_period_id,
                is_generated=True,
                is_approved=True
            ).count()
            
            # Проверяем что все отзывы использованы
            used_reviews = session.query(Review).filter_by(
                period_id=self.current_period_id,
                is_generated=True,
                is_used=True
            ).count()
            
            # Активируем кнопку только если все отзывы приняты и использованы
            can_export = (approved_reviews == total_reviews and used_reviews == total_reviews)
            
            self.export_btn.setEnabled(can_export)
            
            if can_export:
                self.export_btn.setToolTip(f"Экспорт {total_reviews} отзывов в Excel")
            else:
                remaining_approved = total_reviews - approved_reviews
                remaining_used = total_reviews - used_reviews
                self.export_btn.setToolTip(
                    f"Нужно принять: {remaining_approved}, использовать: {remaining_used}"
                )
    
    def export_excel(self):
        """Экспорт отзывов в Excel."""
        if not self.current_period_id:
            QMessageBox.warning(self, "Ошибка", "Период не выбран")
            return
        
        from core.database import db
        from core.models import Review, Period
        from PyQt6.QtWidgets import QFileDialog
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        from datetime import datetime
        
        try:
            with db.get_session() as session:
                # Получаем информацию о периоде
                period = session.query(Period).get(self.current_period_id)
                if not period:
                    QMessageBox.warning(self, "Ошибка", "Период не найден")
                    return
                
                # Получаем все принятые и использованные отзывы
                reviews = session.query(Review).filter_by(
                    period_id=self.current_period_id,
                    is_generated=True,
                    is_approved=True,
                    is_used=True
                ).order_by(Review.target_date).all()
                
                if not reviews:
                    QMessageBox.warning(self, "Ошибка", "Нет отзывов для экспорта")
                    return
                
                # Выбираем файл для сохранения
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Сохранить Excel файл",
                    f"отзывы_{period.start_date.strftime('%Y-%m-%d')}.xlsx",
                    "Excel Files (*.xlsx)"
                )
                
                if not file_path:
                    return
                
                # Создаем Excel файл
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Отзывы"
                
                # Заголовки
                headers = [
                    "ID", "Товар", "Автор", "Рейтинг", 
                    "Отзыв", "Плюсы", "Минусы", "Дата", "Источник"
                ]
                
                # Стили для заголовков
                header_font = Font(bold=True, size=12)
                header_fill = PatternFill(start_color="FF4472C4", end_color="FF4472C4", fill_type="solid")
                header_alignment = Alignment(horizontal="center", vertical="center")
                
                # Записываем заголовки
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=col, value=header)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                
                # Записываем отзывы
                for row, review in enumerate(reviews, 2):
                    ws.cell(row=row, column=1, value=review.id)
                    ws.cell(row=row, column=2, value=review.product_name or "")
                    ws.cell(row=row, column=3, value=review.author or "")
                    ws.cell(row=row, column=4, value=review.rating or "")
                    ws.cell(row=row, column=5, value=review.content or "")
                    ws.cell(row=row, column=6, value=review.pros or "")
                    ws.cell(row=row, column=7, value=review.cons or "")
                    ws.cell(row=row, column=8, value=review.target_date.strftime("%d.%m.%Y") if review.target_date else "")
                    ws.cell(row=row, column=9, value=review.source or "")
                
                # Автоматическая ширина колонок
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = adjusted_width
                
                # Сохраняем файл
                wb.save(file_path)
                
                QMessageBox.information(
                    self, 
                    "Успех", 
                    f"Экспортировано {len(reviews)} отзывов в файл:\n{file_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Ошибка экспорта", 
                f"Произошла ошибка при экспорте:\n{str(e)}"
            )
    
    def generate_missing_reviews(self):
        """Генерировать отзывы для товаров без отзывов."""
        if not self.current_period_id:
            QMessageBox.warning(self, "Ошибка", "Период не выбран")
            return
        
        from core.database import db
        from core.models import ProductTask, Review
        
        with db.get_session() as session:
            # Получаем товары без отзывов
            products = session.query(ProductTask).filter_by(
                period_id=self.current_period_id
            ).all()
            
            products_with_reviews = session.query(Review.product_task_id).filter_by(
                period_id=self.current_period_id,
                is_generated=True
            ).distinct().all()
            
            products_with_reviews_ids = [p[0] for p in products_with_reviews]
            missing_products = [p for p in products if p.id not in products_with_reviews_ids]
            
            if not missing_products:
                QMessageBox.information(self, "Информация", "Все товары имеют отзывы")
                return
            
            # Подтверждение
            product_names = [p.product_name for p in missing_products[:5]]
            text = f"Сгенерировать отзывы для {len(missing_products)} товаров?\n\n"
            text += "Товары:\n" + "\n".join([f"• {name}" for name in product_names])
            
            if len(missing_products) > 5:
                text += f"\n• ... и еще {len(missing_products) - 5} товаров"
            
            reply = QMessageBox.question(
                self, 
                "Подтверждение", 
                text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Запускаем генерацию
            from ui.dialogs.generate_dialog import GenerateDialog
            product_ids = [p.id for p in missing_products]
            
            dialog = GenerateDialog(parent=self, product_ids=product_ids)
            if dialog.exec():
                # Обновляем после генерации
                self.load_reviews()
                QMessageBox.information(
                    self, 
                    "Успех", 
                    f"Сгенерировано отзывы для {len(missing_products)} товаров"
                )
