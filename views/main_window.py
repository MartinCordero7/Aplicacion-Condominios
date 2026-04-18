from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QStackedWidget
from PyQt6.QtCore import Qt
from views.persons_view import PersonsView
from views.units_view import UnitsView
from views.quotas_view import QuotasView
from views.expenses_view import ExpensesView
from views.maintenance_view import MaintenanceView
from views.reports_view import ReportsView

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Sistema de Condominios - {self.current_user.full_name} ({self.current_user.role})")
        self.setGeometry(100, 100, 1024, 768)

        # Main Layout (Sidebar + Content)
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        lbl_menu = QLabel("MENÚ PRINCIPAL")
        lbl_menu.setObjectName("SidebarMenuTitle")
        sidebar_layout.addWidget(lbl_menu)
        
        # Modules
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_units = QPushButton("Unidades")
        self.btn_owners = QPushButton("Propietarios/Inquilinos")
        self.btn_quotas = QPushButton("Cuotas y Pagos")
        self.btn_expenses = QPushButton("Egresos y Gastos")
        self.btn_maintenance = QPushButton("Mantenimiento")
        self.btn_reports = QPushButton("Reportes")
        
        buttons = [
            self.btn_dashboard, self.btn_units, self.btn_owners, 
            self.btn_quotas, self.btn_expenses, self.btn_maintenance, self.btn_reports
        ]
        
        for btn in buttons:
            btn.setObjectName("SidebarBtn")
            sidebar_layout.addWidget(btn)
            
        sidebar.setLayout(sidebar_layout)

        # Content Area - Using QStackedWidget for multiple views
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("ContentArea")
        
        # Views
        self.dashboard_view = QWidget()
        dashboard_layout = QVBoxLayout(self.dashboard_view)
        welcome_lbl = QLabel(f"Bienvenido/a, {self.current_user.full_name}\nSelecciona una opción del menú izquierdo.")
        welcome_lbl.setObjectName("WelcomeTitle")
        welcome_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashboard_layout.addWidget(welcome_lbl)
        
        self.units_view = UnitsView()
        self.persons_view = PersonsView()
        self.quotas_view = QuotasView()
        self.expenses_view = ExpensesView()
        self.maintenance_view = MaintenanceView()
        self.reports_view = ReportsView()
        
        self.content_area.addWidget(self.dashboard_view)
        self.content_area.addWidget(self.units_view)
        self.content_area.addWidget(self.persons_view)
        self.content_area.addWidget(self.quotas_view)
        self.content_area.addWidget(self.expenses_view)
        self.content_area.addWidget(self.maintenance_view)
        self.content_area.addWidget(self.reports_view)
        
        self.content_area.setCurrentWidget(self.dashboard_view)

        # Navigation Connections
        self.btn_dashboard.clicked.connect(lambda: self.content_area.setCurrentWidget(self.dashboard_view))
        self.btn_units.clicked.connect(lambda: self.content_area.setCurrentWidget(self.units_view))
        self.btn_owners.clicked.connect(lambda: self.content_area.setCurrentWidget(self.persons_view))
        self.btn_quotas.clicked.connect(lambda: self.content_area.setCurrentWidget(self.quotas_view))
        self.btn_expenses.clicked.connect(lambda: self.content_area.setCurrentWidget(self.expenses_view))
        self.btn_maintenance.clicked.connect(lambda: self.content_area.setCurrentWidget(self.maintenance_view))
        self.btn_reports.clicked.connect(lambda: self.content_area.setCurrentWidget(self.reports_view))

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
