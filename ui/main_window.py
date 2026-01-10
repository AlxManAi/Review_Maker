"""
Main Window - Primary application window
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
    QStatusBar, QMenuBar, QMenu, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

# Import Tabs/Widgets
from ui.tabs.projects_tab import ProjectsTab
from ui.tabs.periods_tab import PeriodsTab
from ui.tabs.settings_tab import SettingsTab
from ui.widgets.work_area import WorkArea
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.logging_settings_dialog import LoggingSettingsDialog

class MainWindow(QMainWindow):
    """Main application window with hierarchical navigation."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Review Generator")
        self.setMinimumSize(1200, 800)
        
        self.init_ui()
        self.setup_menu()
        
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked Widget for drill-down navigation
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Page 0: Projects (Level 1)
        self.projects_tab = ProjectsTab()
        self.projects_tab.project_selected.connect(self.show_periods)
        self.stack.addWidget(self.projects_tab)
        
        # Page 1: Periods (Level 2)
        self.periods_tab = PeriodsTab()
        self.periods_tab.period_selected.connect(self.show_work_area)
        self.periods_tab.back_to_projects = self.show_projects # Custom signal hack or setter
        # Note: PeriodsTab needs modification to support 'Back' button or we add it here?
        # Ideally PeriodsTab should emit signal. Let's add 'back_requested' signal to PeriodsTab later if needed.
        # But for now, we can wrap PeriodsTab in a widget with a back button OR modify PeriodsTab.
        # Let's modify PeriodsTab logic slightly later or use a wrapper.
        # Actually, let's just add it directly for now and see.
        
        self.stack.addWidget(self.periods_tab)
        
        # Page 2: Work Area (Level 3 - Tabs: Products, Calendar)
        self.work_area = WorkArea()
        self.work_area.back_to_periods.connect(self._back_to_periods_from_work_area)
        self.stack.addWidget(self.work_area)
        
        # Page 3: Settings (Level 4)
        self.settings_tab = SettingsTab()
        self.stack.addWidget(self.settings_tab)
        
        # Status Bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("Файл")
        
        settings_action = QAction("Настройки проекта", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        # Разделитель
        file_menu.addSeparator()
        
        logging_action = QAction("Настройки логирования", self)
        logging_action.triggered.connect(self.open_logging_settings)
        file_menu.addAction(logging_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
    def show_projects(self):
        """Show Projects List (Level 1)."""
        self.stack.setCurrentIndex(0)
        self.statusbar.showMessage("Проекты")
        
    def show_periods(self, project_id):
        """Show Periods for Project (Level 2)."""
        self.current_project_id = project_id
        self.periods_tab.set_project(project_id)
        self.stack.setCurrentIndex(1)
        self.statusbar.showMessage(f"Проект #{project_id}")
        
    def show_periods_back(self):
        """Back to Periods (Level 2)."""
        self.stack.setCurrentIndex(1)
        
    def show_work_area(self, period_id):
        """Show Work Area for Period (Level 3)."""
        print(f"DEBUG: Showing WorkArea for period {period_id}")
        self.current_period_id = period_id
        self.work_area.set_period(period_id)
        self.stack.setCurrentIndex(2)
        print(f"DEBUG: Stack index set to 2. Current widget: {self.stack.currentWidget()}")
        self.statusbar.showMessage(f"Период #{period_id}")
        
    def open_settings(self):
        """Open Settings Dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_settings(self):
        """Show Settings Tab (Level 4)."""
        self._settings_return_index = self.stack.currentIndex()
        self.stack.setCurrentIndex(3)
        self.statusbar.showMessage("Настройки проекта")

    def back_from_settings(self):
        idx = getattr(self, "_settings_return_index", 0)
        if idx == 2 and getattr(self, "current_period_id", None):
            self.show_work_area(self.current_period_id)
            return
        if idx == 1 and getattr(self, "current_project_id", None):
            self.show_periods(self.current_project_id)
            return
        self.stack.setCurrentIndex(idx)

    def _back_to_periods_from_work_area(self):
        if getattr(self, "current_project_id", None):
            self.show_periods(self.current_project_id)
        else:
            self.show_projects()
    
    def open_logging_settings(self):
        """Open Logging Settings Dialog."""
        dialog = LoggingSettingsDialog(self)
        dialog.exec()
