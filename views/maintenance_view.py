from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel, QLineEdit, 
                             QFormLayout, QMessageBox, QHeaderView, QComboBox)
from controllers.operations_controller import OperationsController
from controllers.property_controller import PropertyController

class MaintenanceView(QWidget):
    def __init__(self):
        super().__init__()
        self.op_controller = OperationsController()
        self.prop_controller = PropertyController()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # Left panel: Table
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        title = QLabel("Tickets de Mantenimiento")
        title.setObjectName("ViewTitle")
        left_layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Fecha", "Unidad", "Descripción", "Costo", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_select)
        left_layout.addWidget(self.table)

        # Right panel: Form
        right_panel = QWidget()
        right_panel.setFixedWidth(300)
        right_layout = QVBoxLayout(right_panel)
        
        form_title = QLabel("Nuevo Ticket")
        form_title.setObjectName("FormTitle")
        right_layout.addWidget(form_title)

        form_layout = QFormLayout()
        self.unit_combo = QComboBox()
        self.desc_input = QLineEdit()
        
        form_layout.addRow("Unidad:", self.unit_combo)
        form_layout.addRow("Desc:", self.desc_input)
        right_layout.addLayout(form_layout)

        self.btn_save = QPushButton("Reportar Incidencia")
        self.btn_save.setObjectName("PrimaryBtn")
        self.btn_save.clicked.connect(self.add_maintenance)
        right_layout.addWidget(self.btn_save)
        
        right_layout.addSpacing(20)
        
        update_title = QLabel("Actualizar Estado")
        update_title.setObjectName("FormTitle")
        right_layout.addWidget(update_title)
        
        update_form = QFormLayout()
        self.maint_id_input = QLineEdit()
        self.maint_id_input.setReadOnly(True)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pendiente", "En Proceso", "Finalizado"])
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("Costo final (opcional)")
        
        update_form.addRow("ID Ticket:", self.maint_id_input)
        update_form.addRow("Estado:", self.status_combo)
        update_form.addRow("Costo ($):", self.cost_input)
        right_layout.addLayout(update_form)

        self.btn_update = QPushButton("Guardar Cambios")
        self.btn_update.setObjectName("SuccessBtn")
        self.btn_update.clicked.connect(self.update_status)
        right_layout.addWidget(self.btn_update)

        right_layout.addStretch()

        layout.addWidget(left_panel)
        layout.addWidget(right_panel)

    def load_data(self):
        self.table.setRowCount(0)
        tickets = self.op_controller.get_all_maintenance()
        units = {u.id: u.identifier for u in self.prop_controller.get_all_units()}
        
        for i, t in enumerate(tickets):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.table.setItem(i, 1, QTableWidgetItem(t.report_date.strftime("%Y-%m-%d")))
            unit_name = units.get(t.unit_id, "Área Común") if t.unit_id else "Área Común"
            self.table.setItem(i, 2, QTableWidgetItem(unit_name))
            self.table.setItem(i, 3, QTableWidgetItem(t.description))
            self.table.setItem(i, 4, QTableWidgetItem(f"${t.cost:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(t.status))
            
        self.unit_combo.clear()
        self.unit_combo.addItem("Área Común", None)
        for u_id, u_ident in units.items():
            self.unit_combo.addItem(u_ident, u_id)

    def on_select(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.maint_id_input.setText(self.table.item(row, 0).text())
            self.status_combo.setCurrentText(self.table.item(row, 5).text())

    def add_maintenance(self):
        desc = self.desc_input.text().strip()
        if not desc:
            return
        try:
            self.op_controller.add_maintenance(
                desc,
                self.unit_combo.currentData()
            )
            self.load_data()
            self.desc_input.clear()
            QMessageBox.information(self, "Éxito", "Ticket creado")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def update_status(self):
        maint_id = self.maint_id_input.text().strip()
        if not maint_id:
            return
            
        cost_str = self.cost_input.text().strip()
        try:
            cost = float(cost_str) if cost_str else 0.0
            if cost < 0:
                QMessageBox.warning(self, "Error", "El costo no puede ser negativo.")
                return
                
            self.op_controller.update_maintenance_status(
                int(maint_id),
                self.status_combo.currentText(),
                cost
            )
            self.load_data()
            self.maint_id_input.clear(); self.cost_input.clear()
            QMessageBox.information(self, "Éxito", "Estado actualizado")
        except ValueError as ve:
            QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
