from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel, QLineEdit, 
                             QFormLayout, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from controllers.property_controller import PropertyController
import re

class PersonsView(QWidget):
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
        
        title = QLabel("Gestión de Propietarios e Inquilinos")
        title.setObjectName("ViewTitle")
        left_layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Cédula", "Nombre", "Teléfono", "Correo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
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
        self.cedula_input = QLineEdit()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()

        form_layout.addRow("ID:", self.id_input)
        form_layout.addRow("Cédula:", self.cedula_input)
        form_layout.addRow("Nombre:", self.name_input)
        form_layout.addRow("Teléfono:", self.phone_input)
        form_layout.addRow("Correo:", self.email_input)
        
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
        self.table.setRowCount(0)
        persons = self.controller.get_all_persons()
        for i, p in enumerate(persons):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 1, QTableWidgetItem(p.cedula))
            self.table.setItem(i, 2, QTableWidgetItem(p.name))
            self.table.setItem(i, 3, QTableWidgetItem(p.phone or ""))
            self.table.setItem(i, 4, QTableWidgetItem(p.email or ""))

    def on_select(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.id_input.setText(self.table.item(row, 0).text())
            self.cedula_input.setText(self.table.item(row, 1).text())
            self.name_input.setText(self.table.item(row, 2).text())
            self.phone_input.setText(self.table.item(row, 3).text())
            self.email_input.setText(self.table.item(row, 4).text())

    def save_person(self):
        cedula = self.cedula_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        if not cedula or not name:
            QMessageBox.warning(self, "Error", "Cédula y Nombre son obligatorios")
            return
            
        if not re.match(r'^\d{10}$', cedula):
            QMessageBox.warning(self, "Error", "La cédula debe tener exactamente 10 dígitos numéricos.")
            return
            
        if phone and not re.match(r'^\d{9,10}$', phone):
            QMessageBox.warning(self, "Error", "El teléfono debe tener entre 9 y 10 dígitos numéricos.")
            return
            
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            QMessageBox.warning(self, "Error", "El formato del correo es inválido.")
            return
        
        try:
            self.controller.add_person(cedula, name, phone, email)
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

        cedula = self.cedula_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        if not cedula or not name:
            QMessageBox.warning(self, "Error", "Cédula y Nombre son obligatorios")
            return

        if not re.match(r'^\d{10}$', cedula):
            QMessageBox.warning(self, "Error", "La cédula debe tener exactamente 10 dígitos numéricos.")
            return
            
        if phone and not re.match(r'^\d{9,10}$', phone):
            QMessageBox.warning(self, "Error", "El teléfono debe tener entre 9 y 10 dígitos numéricos.")
            return
            
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            QMessageBox.warning(self, "Error", "El formato del correo es inválido.")
            return

        try:
            self.controller.update_person(int(person_id), cedula, name, phone, email)
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
            if self.controller.delete_person(int(person_id)):
                self.load_data()
                self.clear_form()
                QMessageBox.information(self, "Éxito", "Persona eliminada")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar")

    def clear_form(self):
        self.id_input.clear()
        self.cedula_input.clear()
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.table.clearSelection()
