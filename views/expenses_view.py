from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFormLayout, QMessageBox, QComboBox)
from controllers.operations_controller import OperationsController
from views.utils import create_table, populate_table


class ExpensesView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = OperationsController()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Gestión de Egresos y Proveedores")
        title.setObjectName("ViewTitle")
        layout.addWidget(title)

        content_layout = QHBoxLayout()

        # Left panel: Providers
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        lbl_prov = QLabel("Directorio de Proveedores")
        lbl_prov.setObjectName("FormTitle")
        left_layout.addWidget(lbl_prov)

        self.table_prov = create_table(["ID", "Nombre", "RUC", "Teléfono"])
        left_layout.addWidget(self.table_prov)

        form_prov = QFormLayout()
        self.prov_name = QLineEdit()
        self.prov_ruc = QLineEdit()
        self.prov_phone = QLineEdit()
        self.prov_email = QLineEdit()
        form_prov.addRow("Nombre:", self.prov_name)
        form_prov.addRow("RUC:", self.prov_ruc)
        form_prov.addRow("Teléfono:", self.prov_phone)
        form_prov.addRow("Correo:", self.prov_email)
        left_layout.addLayout(form_prov)

        self.btn_add_prov = QPushButton("Registrar Proveedor")
        self.btn_add_prov.setObjectName("SuccessBtn")
        self.btn_add_prov.clicked.connect(self.add_provider)
        left_layout.addWidget(self.btn_add_prov)

        # Right panel: Expenses
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        lbl_exp = QLabel("Registro de Egresos (Gastos)")
        lbl_exp.setObjectName("FormTitle")
        right_layout.addWidget(lbl_exp)

        self.table_exp = create_table(["ID", "Fecha", "Monto", "Categoría", "Descripción"])
        right_layout.addWidget(self.table_exp)

        form_exp = QFormLayout()
        self.exp_amount = QLineEdit()
        self.exp_cat = QComboBox()
        self.exp_cat.addItems(["Mantenimiento", "Servicios Básicos", "Sueldos", "Insumos", "Otros"])
        self.exp_desc = QLineEdit()
        self.exp_prov = QComboBox()

        form_exp.addRow("Monto:", self.exp_amount)
        form_exp.addRow("Categoría:", self.exp_cat)
        form_exp.addRow("Descripción:", self.exp_desc)
        form_exp.addRow("Proveedor:", self.exp_prov)
        right_layout.addLayout(form_exp)

        self.btn_add_exp = QPushButton("Registrar Egreso")
        self.btn_add_exp.setObjectName("PrimaryBtn")
        self.btn_add_exp.clicked.connect(self.add_expense)
        right_layout.addWidget(self.btn_add_exp)

        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)
        layout.addLayout(content_layout)

    def load_data(self):
        providers = self.controller.get_all_providers()
        populate_table(self.table_prov, [
            [str(p.id), p.name, p.ruc or "", p.phone or ""]
            for p in providers
        ])
        self.exp_prov.clear()
        self.exp_prov.addItem("Ninguno", None)
        for p in providers:
            self.exp_prov.addItem(p.name, p.id)

        expenses = self.controller.get_all_expenses()
        populate_table(self.table_exp, [
            [str(e.id), e.date.strftime("%Y-%m-%d"), f"${e.amount:.2f}", e.category, e.description]
            for e in expenses
        ])

    def add_provider(self):
        name = self.prov_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        try:
            self.controller.add_provider(
                self.prov_ruc.text().strip(), name,
                self.prov_phone.text().strip(), self.prov_email.text().strip()
            )
            self.load_data()
            self.prov_name.clear(); self.prov_ruc.clear()
            self.prov_phone.clear(); self.prov_email.clear()
            QMessageBox.information(self, "Éxito", "Proveedor registrado")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def add_expense(self):
        amount_str = self.exp_amount.text().strip()
        if not amount_str:
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                QMessageBox.warning(self, "Error", "El monto del egreso debe ser mayor a cero.")
                return
            self.controller.add_expense(
                amount, self.exp_cat.currentText(),
                self.exp_desc.text().strip(), self.exp_prov.currentData()
            )
            self.load_data()
            self.exp_amount.clear(); self.exp_desc.clear()
            QMessageBox.information(self, "Éxito", "Egreso registrado")
        except ValueError as ve:
            QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
