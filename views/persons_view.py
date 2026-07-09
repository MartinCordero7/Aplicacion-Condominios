# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFormLayout, QMessageBox,
                             QComboBox, QDateEdit)
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import Qt, QDate, QTimer
from controllers.property_controller import PropertyController
from views.utils import create_table, populate_table


class PersonsView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PropertyController()
        self.current_persons = []
        self.setup_ui()
        self.load_data()

        # Timer to refresh data silently every 15 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        self.timer.start(15000)

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # Left panel: Table
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        title = QLabel("Gestión de Propietarios e Inquilinos")
        title.setObjectName("ViewTitle")
        left_layout.addWidget(title)

        self.table = create_table(["ID", "Cédula", "Nombre", "Teléfono", "Correo"])
        self.table.itemSelectionChanged.connect(self.on_select)
        left_layout.addWidget(self.table)

        # Right panel: Form
        right_panel = QWidget()
        right_panel.setFixedWidth(300)
        right_layout = QVBoxLayout(right_panel)

        form_title = QLabel("Detalles de Persona")
        form_title.setObjectName("FormTitle")
        right_layout.addWidget(form_title)

        form_layout = QFormLayout()
        
        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        
        self.tipo_id_input = QComboBox()
        self.tipo_id_input.addItems(["CEDULA", "PASAPORTE", "RUC"])
        
        self.cedula_input = QLineEdit()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        self.fecha_nac_input = QLineEdit()
        self.fecha_nac_input.setPlaceholderText("YYYY-MM-DD")
        
        self.direccion_input = QLineEdit()
        
        self.estado_input = QComboBox()
        self.estado_input.addItems(["ACTIVO", "INACTIVO"])

        form_layout.addRow("ID:", self.id_input)
        form_layout.addRow("Tipo Identidad:", self.tipo_id_input)
        form_layout.addRow("Número Identidad:", self.cedula_input)
        form_layout.addRow("Nombre:", self.name_input)
        form_layout.addRow("Teléfono:", self.phone_input)
        form_layout.addRow("Correo:", self.email_input)
        form_layout.addRow("Fecha Nacimiento:", self.fecha_nac_input)
        form_layout.addRow("Dirección:", self.direccion_input)
        form_layout.addRow("Estado:", self.estado_input)

        right_layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Guardar Nuevo")
        self.btn_update = QPushButton("Actualizar")
        self.btn_delete = QPushButton("Eliminar")
        self.btn_clear = QPushButton("Limpiar")

        self.btn_save.clicked.connect(self.save_person)
        self.btn_update.clicked.connect(self.update_person)
        self.btn_delete.clicked.connect(self.delete_person)
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
        # Save current selection to restore it after loading
        selected = self.table.selectedItems()
        selected_id = None
        if selected:
            row = selected[0].row()
            selected_id = self.table.item(row, 0).text()

        self.current_persons = self.controller.get_all_persons()
        
        # Block signals so the selection changes don't overwrite user input in the form
        self.table.blockSignals(True)
        populate_table(self.table, [
            [str(p.id), p.cedula, p.name, p.phone or "", p.email or ""]
            for p in self.current_persons
        ])

        # Restore selection if it still exists
        if selected_id:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text() == selected_id:
                    self.table.selectRow(row)
                    break
        self.table.blockSignals(False)

    def on_select(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            person_id_str = self.table.item(row, 0).text()
            person = next((p for p in self.current_persons if str(p.id) == person_id_str), None)
            
            if person:
                self.id_input.setText(str(person.id))
                self.tipo_id_input.setCurrentText(person.tipoIdentificacion)
                self.cedula_input.setText(person.cedula)
                self.name_input.setText(person.name)
                self.phone_input.setText(person.phone or "")
                self.email_input.setText(person.email or "")
                self.fecha_nac_input.setText(person.fechaNacimiento or "")
                self.direccion_input.setText(person.direccion or "")
                self.estado_input.setCurrentText(person.estado)

    def save_person(self):
        tipo_id = self.tipo_id_input.currentText()
        cedula = self.cedula_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        fecha_nac = self.fecha_nac_input.text().strip() or "1990-01-01"
        direccion = self.direccion_input.text().strip()
        estado = self.estado_input.currentText()

        if not cedula or not name:
            QMessageBox.warning(self, "Error", "Número de Identificación y Nombre son obligatorios")
            return

        try:
            self.controller.add_person(cedula, name, phone, email, tipo_id, fecha_nac, direccion, estado)
            self.load_data()
            self.clear_form()
            QMessageBox.information(self, "Éxito", "Persona agregada correctamente")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar: {e}")

    def update_person(self):
        person_id = self.id_input.text().strip()
        if not person_id:
            QMessageBox.warning(self, "Error", "Seleccione una persona para actualizar")
            return

        tipo_id = self.tipo_id_input.currentText()
        cedula = self.cedula_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        fecha_nac = self.fecha_nac_input.text().strip() or "1990-01-01"
        direccion = self.direccion_input.text().strip()
        estado = self.estado_input.currentText()

        if not cedula or not name:
            QMessageBox.warning(self, "Error", "Número de Identificación y Nombre son obligatorios")
            return

        try:
            self.controller.update_person(int(person_id), cedula, name, phone, email, tipo_id, fecha_nac, direccion, estado)
            self.load_data()
            QMessageBox.information(self, "Éxito", "Persona actualizada")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar: {e}")

    def delete_person(self):
        person_id = self.id_input.text()
        if not person_id:
            return

        reply = QMessageBox.question(self, 'Confirmar', '¿Seguro que desea eliminar esta persona?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.controller.delete_person(int(person_id)):
                    self.load_data()
                    self.clear_form()
                    QMessageBox.information(self, "Éxito", "Persona eliminada")
                else:
                    QMessageBox.warning(self, "Error", "No se encontró la persona seleccionada.")
            except ValueError as ve:
                QMessageBox.warning(self, "No se puede eliminar", str(ve))
            except Exception as e:
                QMessageBox.warning(self, "Error inesperado", f"Ocurrió un error: {e}")

    def clear_form(self):
        self.id_input.clear()
        self.tipo_id_input.setCurrentIndex(0)
        self.cedula_input.clear()
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.fecha_nac_input.clear()
        self.direccion_input.clear()
        self.estado_input.setCurrentIndex(0)
        self.table.clearSelection()
