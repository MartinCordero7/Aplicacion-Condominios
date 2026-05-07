from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFormLayout, QMessageBox,
                             QDateEdit, QComboBox)
from PyQt6.QtCore import Qt, QDate
from controllers.finance_controller import FinanceController
from controllers.property_controller import PropertyController
from views.utils import create_table, populate_table
import datetime


class QuotasView(QWidget):
    def __init__(self):
        super().__init__()
        self.finance_controller = FinanceController()
        self.property_controller = PropertyController()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # Left panel: Table & Generation
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        title = QLabel("Gestión de Cuotas y Pagos")
        title.setObjectName("ViewTitle")
        left_layout.addWidget(title)

        # Generator Box
        gen_layout = QHBoxLayout()
        gen_layout.addWidget(QLabel("Generar Cuotas Mensuales - Base por Alícuota:"))
        self.base_amount_input = QLineEdit()
        self.base_amount_input.setPlaceholderText("Ej. 10.00")
        gen_layout.addWidget(self.base_amount_input)

        self.btn_generate = QPushButton("Generar Masivamente")
        self.btn_generate.setObjectName("SuccessBtn")
        self.btn_generate.clicked.connect(self.generate_quotas)
        gen_layout.addWidget(self.btn_generate)
        left_layout.addLayout(gen_layout)

        self.table = create_table(["ID", "Unidad", "Emisión", "Vencimiento", "Monto", "Tipo", "Estado"])
        self.table.itemSelectionChanged.connect(self.on_select)
        left_layout.addWidget(self.table)

        # Right panel: Form for Single Quota & Payment
        right_panel = QWidget()
        right_panel.setFixedWidth(300)
        right_layout = QVBoxLayout(right_panel)

        form_title = QLabel("Nueva Cuota Individual")
        form_title.setObjectName("FormTitle")
        right_layout.addWidget(form_title)

        form_layout = QFormLayout()
        self.unit_combo = QComboBox()
        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(QDate.currentDate().addDays(30))
        self.amount_input = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Ordinaria", "Extraordinaria", "Multa"])
        self.desc_input = QLineEdit()

        form_layout.addRow("Unidad:", self.unit_combo)
        form_layout.addRow("Vence:", self.due_date_input)
        form_layout.addRow("Monto:", self.amount_input)
        form_layout.addRow("Tipo:", self.type_combo)
        form_layout.addRow("Desc:", self.desc_input)

        right_layout.addLayout(form_layout)

        self.btn_save_quota = QPushButton("Crear Cuota")
        self.btn_save_quota.clicked.connect(self.add_single_quota)
        right_layout.addWidget(self.btn_save_quota)

        right_layout.addSpacing(20)

        pay_title = QLabel("Registrar Pago")
        pay_title.setObjectName("FormTitle")
        right_layout.addWidget(pay_title)

        pay_form = QFormLayout()
        self.pay_quota_id = QLineEdit()
        self.pay_quota_id.setReadOnly(True)
        self.pay_method = QComboBox()
        self.pay_method.addItems(["Transferencia", "Efectivo", "Cheque"])
        self.pay_ref = QLineEdit()

        pay_form.addRow("Cuota ID:", self.pay_quota_id)
        pay_form.addRow("Método:", self.pay_method)
        pay_form.addRow("Referencia:", self.pay_ref)
        right_layout.addLayout(pay_form)

        self.btn_pay = QPushButton("Registrar Pago")
        self.btn_pay.setObjectName("PrimaryBtn")
        self.btn_pay.clicked.connect(self.pay_quota)
        right_layout.addWidget(self.btn_pay)

        right_layout.addStretch()

        layout.addWidget(left_panel)
        layout.addWidget(right_panel)

    def load_data(self):
        quotas = self.finance_controller.get_all_quotas()
        units = {u.id: u.identifier for u in self.property_controller.get_all_units()}

        populate_table(self.table, [
            [
                str(q.id),
                units.get(q.unit_id, str(q.unit_id)),
                q.issue_date.strftime("%Y-%m-%d"),
                q.due_date.strftime("%Y-%m-%d"),
                f"${q.amount:.2f}",
                q.quota_type,
                "Pagada" if q.is_paid else "Pendiente",
            ]
            for q in quotas
        ])
        self.load_units_combo()

    def load_units_combo(self):
        self.unit_combo.clear()
        units = self.property_controller.get_all_units()
        for u in units:
            self.unit_combo.addItem(u.identifier, u.id)

    def on_select(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            quota_id = self.table.item(row, 0).text()
            status = self.table.item(row, 6).text()

            self.pay_quota_id.setText(quota_id)
            if status == "Pagada":
                self.btn_pay.setEnabled(False)
                self.btn_pay.setText("Ya Pagada")
            else:
                self.btn_pay.setEnabled(True)
                self.btn_pay.setText("Registrar Pago")

    def generate_quotas(self):
        base_amt_str = self.base_amount_input.text().strip()
        if not base_amt_str:
            QMessageBox.warning(self, "Error", "Ingrese un monto base por alícuota")
            return

        try:
            base_amt = float(base_amt_str)
            if base_amt <= 0:
                QMessageBox.warning(self, "Error", "El monto base debe ser mayor a cero.")
                return

            due_date = datetime.date.today() + datetime.timedelta(days=15)
            count = self.finance_controller.generate_monthly_quotas(base_amt, due_date)
            self.load_data()
            QMessageBox.information(self, "Éxito", f"Se generaron {count} cuotas mensuales.")
        except ValueError as ve:
            QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al generar cuotas: {e}")

    def add_single_quota(self):
        unit_id = self.unit_combo.currentData()
        amount_str = self.amount_input.text().strip()

        if not unit_id or not amount_str:
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                QMessageBox.warning(self, "Error", "El monto de la cuota debe ser mayor a cero.")
                return

            due_date = self.due_date_input.date().toPyDate()
            self.finance_controller.add_quota(
                unit_id,
                due_date,
                amount,
                self.type_combo.currentText(),
                self.desc_input.text().strip()
            )
            self.load_data()
            self.amount_input.clear()
            self.desc_input.clear()
            QMessageBox.information(self, "Éxito", "Cuota creada")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def pay_quota(self):
        quota_id = self.pay_quota_id.text().strip()
        if not quota_id:
            return

        row = self.table.currentRow()
        amount_str = self.table.item(row, 4).text().replace('$', '')
        amount = float(amount_str)

        try:
            self.finance_controller.pay_quota(
                int(quota_id),
                amount,
                self.pay_method.currentText(),
                self.pay_ref.text().strip()
            )
            self.load_data()
            self.pay_quota_id.clear()
            self.pay_ref.clear()
            QMessageBox.information(self, "Éxito", "Pago registrado correctamente")
        except ValueError as ve:
            QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al registrar pago: {e}")
