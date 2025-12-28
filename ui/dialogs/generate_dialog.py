"""
Generate Dialog - Диалог для генерации отзывов
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QRadioButton, QGroupBox,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class GenerateWorker(QThread):
    """Worker для генерации отзывов в отдельном потоке."""
    finished = pyqtSignal(bool, str)  # success, message
    progress = pyqtSignal(str)   # message
    
    def __init__(self, product_ids, model):
        super().__init__()
        self.product_ids = product_ids
        self.model = model
    
    def run(self):
        try:
            from core.ai_service import ai_service
            total_generated = 0
            errors = []
            
            for i, pid in enumerate(self.product_ids, 1):
                self.progress.emit(f"Обработка товара {i}/{len(self.product_ids)}...")
                
                count, msg = ai_service.generate_reviews(
                    product_task_id=pid,
                    model=self.model
                )
                
                if count > 0:
                    total_generated += count
                else:
                    errors.append(f"ID {pid}: {msg}")
            
            if total_generated > 0:
                msg = f"Успешно сгенерировано {total_generated} отзывов"
                if errors:
                    msg += f"\n\nОшибки:\n" + "\n".join(errors)
                self.finished.emit(True, msg)
            else:
                error_msg = "\n".join(errors) if errors else "Ничего не сгенерировано"
                self.finished.emit(False, error_msg)
                
        except Exception as e:
            self.finished.emit(False, str(e))


class GenerateDialog(QDialog):
    """Dialog for generating reviews."""
    
    def __init__(self, parent=None, product_ids: list = None):
        super().__init__(parent)
        self.product_ids = product_ids or []
        self.init_ui()
        self.load_products_info()
    
    def init_ui(self):
        self.setWindowTitle("Генерация отзывов")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Info
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        
        self.product_label = QLabel(f"Выбрано товаров: {len(self.product_ids)}")
        self.product_label.setWordWrap(True)
        self.product_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        info_layout.addWidget(self.product_label)
        
        self.details_label = QLabel("Загрузка...")
        info_layout.addWidget(self.details_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Model selection
        model_group = QGroupBox("Выберите модель AI")
        model_layout = QVBoxLayout()
        
        self.radio_perplexity = QRadioButton("Perplexity (Sonar)")
        self.radio_perplexity.setChecked(True)
        self.radio_mistral = QRadioButton("Mistral (Small)")
        self.radio_deepseek = QRadioButton("DeepSeek (V3)")
        
        model_layout.addWidget(self.radio_perplexity)
        model_layout.addWidget(self.radio_mistral)
        model_layout.addWidget(self.radio_deepseek)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Генерировать")
        self.generate_btn.clicked.connect(self.start_generation)
        self.generate_btn.setStyleSheet("background-color: #007bff; color: white; padding: 8px;")
        
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_products_info(self):
        """Load info about selected products."""
        if not self.product_ids:
            return
            
        from core.database import db
        from core.models import ProductTask
        
        try:
            total_reviews_needed = 0
            
            with db.get_session() as session:
                products = session.query(ProductTask).filter(ProductTask.id.in_(self.product_ids)).all()
                for p in products:
                    total_reviews_needed += (p.review_count or 0)
            
            self.details_label.setText(
                f"Всего нужно отзывов: {total_reviews_needed}\n"
                f"Примеров будет использовано: (автоматически)"
            )
            
        except Exception as e:
            self.details_label.setText(f"Ошибка загрузки данных: {e}")

    def start_generation(self):
        """Start generation process."""
        model = "perplexity"
        if self.radio_mistral.isChecked():
            model = "mistral"
        elif self.radio_deepseek.isChecked():
            model = "deepseek"
        
        self.generate_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.radio_perplexity.setEnabled(False)
        self.radio_mistral.setEnabled(False)
        self.radio_deepseek.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Запуск генерации...")
        
        self.worker = GenerateWorker(self.product_ids, model)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.progress.connect(self.update_status)
        self.worker.start()
    
    def update_status(self, message):
        self.status_label.setText(message)

    def on_generation_finished(self, success, message):
        """Обработать завершение генерации."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        
        # Включить кнопки
        self.generate_btn.setEnabled(True)
        self.close_btn.setEnabled(True)
        self.radio_perplexity.setEnabled(True)
        self.radio_mistral.setEnabled(True)
        self.radio_deepseek.setEnabled(True)
        
        if success:
            QMessageBox.information(
                self,
                "Успех",
                message
            )
            self.accept()  # Закрыть диалог
        else:
            QMessageBox.warning(
                self,
                "Ошибка",
                message
            )
