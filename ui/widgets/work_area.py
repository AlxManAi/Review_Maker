"""
Work Area - Рабочая зона для работы с периодом
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui.components.neon_button import NeonButton
from ui.tabs.products_tab import ProductsTab
from ui.tabs.generated_reviews_tab import GeneratedReviewsTab

class WorkArea(QWidget):
    """Рабочая зона для выбранного периода."""
    
    back_to_periods = pyqtSignal() # Сигнал возврата к списку периодов
    
    def __init__(self):
        super().__init__()
        print("DEBUG: WorkArea initializing...")
        self.current_period_id = None
        self.init_ui()
        print("DEBUG: WorkArea initialized.")
        
    def init_ui(self):
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            
            # Header
            header = QHBoxLayout()
            
            self.back_btn = NeonButton("← Назад к периодам", "secondary")
            self.back_btn.clicked.connect(self.back_to_periods.emit)
            self.back_btn.setMinimumWidth(180)
            
            header.addWidget(self.back_btn)
            
            self.title_label = QLabel("Период #...")
            self.title_label.setStyleSheet("font-size: 16px; margin-left: 15px; color: #cdd6f4;")
            header.addWidget(self.title_label)
            
            header.addStretch()
            layout.addLayout(header)
            
            # Разделитель или просто отступ для "воздуха"
            layout.addSpacing(15)
            
            # Tabs
            print("DEBUG: WorkArea creating tabs...")
            self.tabs = QTabWidget()
            
            self.products_tab = ProductsTab()
            print("DEBUG: ProductsTab created.")
            
            self.reviews_tab = GeneratedReviewsTab()
            print("DEBUG: GeneratedReviewsTab created.")
            
            self.tabs.addTab(self.products_tab, "1. Товары")
            self.tabs.addTab(self.reviews_tab, "2. Календарь отзывов")
            
            # Обновление календаря при переключении на него
            self.tabs.currentChanged.connect(self.on_tab_changed)
            
            layout.addWidget(self.tabs)
            self.setLayout(layout)
        except Exception as e:
            print(f"ERROR in WorkArea init_ui: {e}")
            import traceback
            traceback.print_exc()

    def set_period(self, period_id):
        """Установить текущий период."""
        print(f"DEBUG: WorkArea set_period {period_id}")
        self.current_period_id = period_id
        
        # Обновить заголовок
        from core.database import db
        from core.models import Period
        with db.get_session() as session:
            period = session.query(Period).get(period_id)
            if period:
                start = period.start_date.strftime("%d.%m.%Y")
                end = period.end_date.strftime("%d.%m.%Y")
                self.title_label.setText(f"Период: {start} - {end}")
        
        # Передать период во вкладки
        self.products_tab.set_period(period_id)
        self.reviews_tab.set_period(period_id)
        
        # Открыть первую вкладку по умолчанию
        self.tabs.setCurrentIndex(0)

    def on_tab_changed(self, index):
        """При переключении вкладок обновлять данные."""
        if index == 1: # Календарь
            # Убедимся что период установлен перед загрузкой
            if hasattr(self, 'current_period_id') and self.current_period_id:
                self.reviews_tab.set_period(self.current_period_id)
            else:
                self.reviews_tab.load_reviews()
        elif index == 0: # Товары
            # Load only if not already loaded to avoid unnecessary refreshes
            if not self.products_tab.table.rowCount():
                self.products_tab.load_products()
        
        # Обновляем умную активность
        self._update_smart_activity()
    
    def _update_smart_activity(self):
        """Обновление умной активности на основе контекста"""
        # Умная активность теперь управляется на уровне вкладок
        pass
