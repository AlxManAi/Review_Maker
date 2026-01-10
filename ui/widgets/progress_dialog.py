"""
Progress Dialog - Единый красивый прогресс-бар для долгих операций
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QWidget, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QRectF, QPointF
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QColor
from core.logger import app_logger
import sys
from ui.components.neon_button import NeonButton


class ModernProgressBar(QProgressBar):
    """Современный красивый прогресс-бар с градиентом"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setTextVisible(True)
        self._anim_offset = 0
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start(35)

    def _tick(self):
        self._anim_offset = (self._anim_offset + 3) % 200
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        radius = 15.0

        painter.setPen(QColor("#555"))
        painter.setBrush(QColor("#2d2d2d"))
        painter.drawRoundedRect(rect, radius, radius)

        minimum = self.minimum()
        maximum = self.maximum()
        value = self.value()

        frac = 0.0
        if maximum > minimum:
            frac = (value - minimum) / (maximum - minimum)
            frac = max(0.0, min(1.0, float(frac)))

        inner = rect.adjusted(2.0, 2.0, -2.0, -2.0)
        chunk_w = inner.width() * frac
        if chunk_w > 0.0:
            chunk_rect = QRectF(inner.left(), inner.top(), chunk_w, inner.height())
            grad = QLinearGradient(
                QPointF(chunk_rect.left() - self._anim_offset, chunk_rect.center().y()),
                QPointF(chunk_rect.left() - self._anim_offset + 220.0, chunk_rect.center().y()),
            )
            grad.setColorAt(0.0, QColor("#4a9eff"))
            grad.setColorAt(0.7, QColor("#7c4dff"))
            grad.setColorAt(1.0, QColor("#a855f7"))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(chunk_rect, 13.0, 13.0)

        if self.isTextVisible():
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            if maximum > minimum:
                percentage = int(frac * 100)
                text = f"{percentage}%"
            else:
                text = self.text()
            painter.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter), text)


class ProgressDialog(QDialog):
    """Диалог с прогресс-баром для долгих операций"""
    
    def __init__(self, title="Выполнение операции", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(560, 280)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding: 2px 0px;
            }
        """)
        
        self.init_ui()
        self.can_close = False
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 18)
        
        # Заголовок операции
        self.title_label = QLabel("Выполнение операции...")
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setMinimumHeight(30)
        layout.addWidget(self.title_label)
        
        # Детальная информация
        self.details_label = QLabel("Подготовка...")
        self.details_label.setWordWrap(True)
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_label.setStyleSheet("color: #cdd6f4; font-size: 13px; padding: 4px 0px;")
        self.details_label.setMinimumHeight(54)
        layout.addWidget(self.details_label)
        
        # Прогресс-бар
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Статистика
        self.stats_label = QLabel("0 / 0")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setStyleSheet("color: #4a9eff; font-weight: bold;")
        self.stats_label.setMinimumHeight(24)
        layout.addWidget(self.stats_label)
        
        # Кнопка отмены
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.cancel_btn = NeonButton("Отмена", "secondary")
        self.cancel_btn.setMinimumHeight(32)
        self.cancel_btn.setMaximumHeight(32)
        self.cancel_btn.setMinimumWidth(140)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
    
    def update_progress(self, current, total, details=""):
        """Обновить прогресс"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{percentage}%")
            self.stats_label.setText(f"{current} / {total}")
            
            if details:
                self.details_label.setText(details)
            
            # Принудительное обновление UI
            self.progress_bar.update()
            self.stats_label.update()
            self.details_label.update()
            QApplication.processEvents()
    
    def update_details(self, details):
        """Обновить только детали операции"""
        if details is not None:
            self.details_label.setText(str(details))
            self.details_label.update()
    
    def set_title(self, title):
        """Установить заголовок операции"""
        self.title_label.setText(title)
    
    def set_operation_details(self, details):
        """Установить детали операции"""
        self.details_label.setText(details)
    
    def finish(self, message="Операция завершена"):
        """Завершить операцию"""
        self.progress_bar.setValue(100)
        self.details_label.setText(message)
        self.cancel_btn.setText("Закрыть")
        self.can_close = True
        self.cancel_btn.setEnabled(True)
    
    def cancel_operation(self):
        """Отмена операции"""
        if self.can_close:
            self.accept()
        else:
            # Здесь можно добавить логику отмены операции
            pass
    
    def closeEvent(self, event):
        """Запрет закрытия во время выполнения"""
        if not self.can_close:
            event.ignore()
        else:
            super().closeEvent(event)


class ParseWorker(QThread):
    """Worker для парсинга с прогрессом"""
    
    progress_updated = pyqtSignal(int, int, str)  # current, total, details
    finished = pyqtSignal(int, str)  # result_count, message
    error = pyqtSignal(str)
    
    def __init__(self, product_ids, parser_service):
        super().__init__()
        self.product_ids = product_ids
        self.parser_service = parser_service
        self.should_cancel = False
    
    def run(self):
        """Выполнить парсинг с обновлением прогресса"""
        total = len(self.product_ids)
        
        for i, product_id in enumerate(self.product_ids):
            if self.should_cancel:
                break
            
            # Обновляем прогресс
            self.progress_updated.emit(i, total, f"Парсинг товара {i+1}/{total}...")
            
            try:
                count, message = self.parser_service.parse_product_reviews(product_id)
                app_logger.info(f"Товар {product_id}: {count} отзывов, {message}")
            except Exception as e:
                error_msg = f"Ошибка парсинга товара {product_id}: {str(e)}"
                self.error.emit(error_msg)
                app_logger.error(error_msg)
        
        # Финальное обновление
        self.progress_updated.emit(total, total, "Парсинг завершен")
        self.finished.emit(total, "Парсинг завершен")
    
    def cancel(self):
        """Отменить операцию"""
        self.should_cancel = True


class GenerateWorker(QThread):
    """Worker для генерации с прогрессом"""
    
    progress_updated = pyqtSignal(int, int, str)  # current, total, details
    finished = pyqtSignal(int, str)  # result_count, message
    error = pyqtSignal(str)
    
    def __init__(self, product_ids, ai_service, model="perplexity", total_to_generate: int = 0):
        super().__init__()
        self.product_ids = product_ids
        self.ai_service = ai_service
        self.model = model
        self.total_to_generate = int(total_to_generate or 0)
        self.should_cancel = False
    
    def run(self):
        """Выполнить генерацию с обновлением прогресса"""
        total_products = len(self.product_ids)
        total_reviews = self.total_to_generate if self.total_to_generate > 0 else total_products
        generated_reviews = 0
        
        for i, product_id in enumerate(self.product_ids):
            if self.should_cancel:
                break
            
            # Обновляем прогресс
            self.progress_updated.emit(
                generated_reviews,
                total_reviews,
                f"Товар {i+1}/{total_products}: генерация..."
            )
            
            try:
                count, message = self.ai_service.generate_reviews(product_task_id=product_id, model=self.model)
                generated_reviews += int(count or 0)
                app_logger.info(f"Товар {product_id}: {count} отзывов, {message}")

                # Обновляем прогресс по количеству добавленных отзывов
                self.progress_updated.emit(
                    min(generated_reviews, total_reviews),
                    total_reviews,
                    f"Товар {i+1}/{total_products}: {message}"
                )
            except Exception as e:
                error_msg = f"Ошибка генерации для товара {product_id}: {str(e)}"
                self.error.emit(error_msg)
                app_logger.error(error_msg)
        
        # Финальное обновление
        self.progress_updated.emit(min(generated_reviews, total_reviews), total_reviews, "Генерация завершена")
        self.finished.emit(generated_reviews, f"Генерация завершена. Добавлено: {generated_reviews}")
    
    def cancel(self):
        """Отменить операцию"""
        self.should_cancel = True
