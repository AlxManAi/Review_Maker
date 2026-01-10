"""
Generate Dialog - Диалог для генерации отзывов
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QRadioButton, QGroupBox,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt
from core.database import db
from core.models import ProductTask, Review
from core.ai_service import ai_service
from ui.components.neon_button import NeonButton


class GenerateDialog(QDialog):
    """Dialog for generating reviews."""
    
    def __init__(self, parent=None, product_ids: list = None):
        super().__init__(parent)
        self.product_ids = product_ids or []
        self.init_ui()
        self.load_products_info()
    
    def init_ui(self):
        self.setWindowTitle("Генерация отзывов")
        self.setFixedSize(500, 450)
        
        layout = QVBoxLayout()
        
        # Info
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        
        self.product_label = QLabel(f"Выбрано товаров: {len(self.product_ids)}")
        self.product_label.setWordWrap(True)
        info_layout.addWidget(self.product_label)
        
        self.details_label = QLabel("Загрузка...")
        self.details_label.setWordWrap(True)
        info_layout.addWidget(self.details_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Model selection
        model_group = QGroupBox("Выберите модель AI")
        model_layout = QVBoxLayout()

        radio_style = (
            "QRadioButton { spacing: 8px; color: #cdd6f4; }"
            "QRadioButton::indicator { width: 16px; height: 16px; border-radius: 8px; border: 2px solid #45475a; background-color: #313244; }"
            "QRadioButton::indicator:checked { background-color: #4a9eff; border-color: #4a9eff; }"
        )
        
        self.radio_perplexity = QRadioButton("Perplexity (Sonar)")
        self.radio_perplexity.setChecked(True)
        self.radio_perplexity.setStyleSheet(radio_style)
        self.radio_mistral = QRadioButton("Mistral (Small)")
        self.radio_mistral.setStyleSheet(radio_style)
        self.radio_deepseek = QRadioButton("DeepSeek (V3)")
        self.radio_deepseek.setStyleSheet(radio_style)
        
        model_layout.addWidget(self.radio_perplexity)
        model_layout.addWidget(self.radio_mistral)
        model_layout.addWidget(self.radio_deepseek)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.generate_btn = NeonButton("Генерировать", "primary")
        self.generate_btn.clicked.connect(self.start_generation)
        
        self.close_btn = NeonButton("Закрыть", "secondary")
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_products_info(self):
        """Load info about selected products."""
        if not self.product_ids:
            return
            
        try:
            total_reviews_needed = 0
            total_existing = 0
            total_to_generate = 0
            
            with db.get_session() as session:
                products = session.query(ProductTask).filter(ProductTask.id.in_(self.product_ids)).all()
                for p in products:
                    needed = (p.review_count or 0)
                    existing = session.query(Review).filter(Review.product_task_id == p.id).count()
                    
                    total_reviews_needed += needed
                    total_existing += existing
                    
                    if existing < needed:
                        total_to_generate += (needed - existing)
            
            self.details_label.setText(
                f"Всего нужно отзывов: {total_reviews_needed}\n"
                f"Уже существует: {total_existing}\n"
                f"Будет сгенерировано: {total_to_generate}\n"
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
        
        # Проверяем есть ли принятые отзывы
        with db.get_session() as session:
            total_approved = 0
            for pid in self.product_ids:
                approved = session.query(Review).filter(
                    Review.product_task_id == pid,
                    Review.is_approved == True
                ).count()
                total_approved += approved
            
            if total_approved > 0:
                reply = QMessageBox.question(
                    self, "Предупреждение", 
                    f"У выбранных товаров есть {total_approved} принятых отзывов. "
                    "Все равно дополнить до нужного количества?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
        
        from ui.widgets.progress_dialog import ProgressDialog, GenerateWorker
        progress_dialog = ProgressDialog("Генерация отзывов", self)
        
        # Показываем сколько будет сгенерировано
        with db.get_session() as session:
            total_to_generate = 0
            for pid in self.product_ids:
                product = session.query(ProductTask).get(pid)
                if product:
                    needed = product.review_count or 0
                    existing = session.query(Review).filter(Review.product_task_id == pid).count()
                    if existing < needed:
                        total_to_generate += (needed - existing)

        progress_dialog.set_operation_details(f"Будет сгенерировано: {total_to_generate} отзывов")

        # Создаем worker с корректными данными (ВАЖНО: второй аргумент ai_service, а не model)
        worker = GenerateWorker(self.product_ids, ai_service, model=model, total_to_generate=total_to_generate)
        worker.progress_updated.connect(progress_dialog.update_progress)
        worker.finished.connect(lambda total_generated, msg: self._on_generation_finished(total_generated, msg, progress_dialog))
        # Ошибки показываем только текстом в прогресс-окне (без модальных окон во время работы)
        worker.error.connect(progress_dialog.update_details)
        
        # Обновляем статус
        self.status_label.setText("Генерация...")
        self.status_label.setStyleSheet("color: #ffc107; font-weight: bold;")

        worker.start()
        progress_dialog.exec()

    def _on_generation_finished(self, total_generated, message, dialog):
        """Обработать завершение генерации."""
        dialog.finish(message)
        if "ошиб" in (message or "").lower():
            QMessageBox.warning(dialog, "Генерация завершена", message)
        else:
            QMessageBox.information(dialog, "Генерация завершена", message)
        self.accept()
