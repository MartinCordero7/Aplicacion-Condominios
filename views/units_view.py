from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel, QLineEdit, 
                             QFormLayout, QMessageBox, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt
from controllers.property_controller import PropertyController

class UnitsView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PropertyController()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # Left panel: Table
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        title = QLabel("Gestión de Unidades")
        title.setObjectName("ViewTitle")
        left_layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Identificador", "Tipo", "Alícuota %", "Ocupado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_select)
        left_layout.addWidget(self.table)

        # Right panel: Form
        right_panel = QWidget()
        right_panel.setFixedWidth(300)
        right_layout = QVBoxLayout(right_panel)
        
        form_title = QLabel("Detalles de Unidad")
        form_title.setObjectName("FormTitle")
        right_layout.addWidget(form_title)

        form_layout = QFormLayout()
        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        self.identifier_input = QLineEdit()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Departamento", "Casa", "Local", "Oficina", "Otro"])
        
        self.alicuota_input = QLineEdit()
        self.alicuota_input.setPlaceholderText("Ej. 2.5")
        
        self.owner_combo = QComboBox()
        self.tenant_combo = QComboBox()

        form_layout.addRow("ID:", self.id_input)
        form_layout.addRow("Identificador:", self.identifier_input)
        form_layout.addRow("Tipo:", self.type_combo)
        form_layout.addRow("Alícuota (%):", self.alicuota_input)
        form_layout.addRow("Propietario:", self.owner_combo)
        form_layout.addRow("Inquilino:", self.tenant_combo)
        
        right_layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Guardar Nuevo")
        self.btn_update = QPushButton("Actualizar")
        self.btn_delete = QPushButton("Eliminar")
        self.btn_clear = QPushButton("Limpiar")

        self.btn_save.clicked.connect(self.save_unit)
        self.btn_update.clicked.connect(self.update_unit)
        self.btn_delete.clicked.connect(self.delete_unit)
        self.btn_clear.clicked.connect(self.clear_form)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_update)
        
        btn_layout2 = QHBoxLayout()
        btn_layout2.addWidget(self.btn_delete)
        btn_layout2.addWidget(self.btn_clear)

        right_layout.addLayout(btn_layout)
        right_layout.addLayout(btn_layout2)
        right_layout.addStretch()

        layout.addWidget(left_panel)
        layout.addWidget(right_panel)

    def load_data(self):
        self.table.setRowCount(0)
        units = self.controller.get_all_units()
        for i, u in enumerate(units):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(u.id)))
            self.table.setItem(i, 1, QTableWidgetItem(u.identifier))
            self.table.setItem(i, 2, QTableWidgetItem(u.unit_type))
            self.table.setItem(i, 3, QTableWidgetItem(str(u.alicuota)))
            self.table.setItem(i, 4, QTableWidgetItem("Sí" if u.is_occupied else "No"))
            
        self.load_persons_combos()

    def load_persons_combos(self):
        self.owner_combo.clear()
        self.tenant_combo.clear()
        self.owner_combo.addItem("Ninguno", None)
        self.tenant_combo.addItem("Ninguno", None)
        
        persons = self.controller.get_all_persons()
        for p in persons:
            self.owner_combo.addItem(f"{p.cedula} - {p.name}", p.id)
            self.tenant_combo.addItem(f"{p.cedula} - {p.name}", p.id)

    def on_select(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            unit_id = self.table.item(row, 0).text()
            self.id_input.setText(unit_id)
            self.identifier_input.setText(self.table.item(row, 1).text())
            self.type_combo.setCurrentText(self.table.item(row, 2).text())
            self.alicuota_input.setText(self.table.item(row, 3).text())
            
            units = self.controller.get_all_units()
            for u in units:
                if str(u.id) == unit_id:
                    self.set_combo_by_data(self.owner_combo, u.owner_id)
                    self.set_combo_by_data(self.tenant_combo, u.tenant_id)
                    break

    def set_combo_by_data(self, combo, data):
        for i in range(combo.count()):
            if combo.itemData(i) == data:
                combo.setCurrentIndex(i)
                return

    def save_unit(self):
        identifier = self.identifier_input.text().strip()
        if not identifier:
            QMessageBox.warning(self, "Error", "El identificador es obligatorio")
            return
        
        try:
            alicuota_str = self.alicuota_input.text().strip()
            alicuota = float(alicuota_str) if alicuota_str else 0.0
            if alicuota < 0:
                QMessageBox.warning(self, "Error", "La alícuota no puede ser negativa.")
                return

            self.controller.add_unit(
                identifier,
                self.type_combo.currentText(),
                alicuota,
                self.owner_combo.currentData(),
                self.tenant_combo.currentData()
            )
            self.load_data()
            self.clear_form()
            QMessageBox.information(self, "Éxito", "Unidad agregada correctamente")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar: {e}")

    def update_unit(self):
        unit_id = self.id_input.text().strip()
        if not unit_id:
            QMessageBox.warning(self, "Error", "Seleccione una unidad para actualizar")
            return

        identifier = self.identifier_input.text().strip()
        if not identifier:
            QMessageBox.warning(self, "Error", "El identificador es obligatorio")
            return

        try:
            alicuota_str = self.alicuota_input.text().strip()
            alicuota = float(alicuota_str) if alicuota_str else 0.0
            if alicuota < 0:
                QMessageBox.warning(self, "Error", "La alícuota no puede ser negativa.")
                return

            self.controller.update_unit(
                int(unit_id),
                identifier,
                self.type_combo.currentText(),
                alicuota,
                self.owner_combo.currentData(),
                self.tenant_combo.currentData()
            )
            self.load_data()
            QMessageBox.information(self, "Éxito", "Unidad actualizada")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar: {e}")

    def delete_unit(self):
        unit_id = self.id_input.text().strip()
        if not unit_id:
            return
            
        reply = QMessageBox.question(self, 'Confirmar', '¿Seguro que desea eliminar esta unidad?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.controller.delete_unit(int(unit_id)):
                    self.load_data()
                    self.clear_form()
                    QMessageBox.information(self, "Éxito", "Unidad eliminada")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar")
            except ValueError as ve:
                QMessageBox.warning(self, "Error", str(ve))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error inesperado: {e}")

    def clear_form(self):
        self.id_input.clear()
        self.identifier_input.clear()
        self.alicuota_input.clear()
        self.owner_combo.setCurrentIndex(0)
        self.tenant_combo.setCurrentIndex(0)
        self.table.clearSelection()
