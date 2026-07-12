# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFormLayout, QMessageBox, QComboBox)
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import Qt, QTimer
from controllers.property_controller import PropertyController
from views.utils import create_table, populate_table

# ENUMs exactos del schema.sql
TIPO_UNIDAD_ENUM = ["DEPARTAMENTO", "CASA", "LOCAL", "OFICINA"]
# id 1 = HABITADO, id 2 = DESHABITADO, id 3 = EN_MANTENIMIENTO (según datos semilla)
ESTADO_UNIDAD_OPTIONS = [
    ("HABITADO", 1),
    ("DESHABITADO", 2),
    ("EN_MANTENIMIENTO", 3),
]


class UnitsView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PropertyController()
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

        title = QLabel("Gestión de Unidades")
        title.setObjectName("ViewTitle")
        left_layout.addWidget(title)

        self.table = create_table(["ID", "Identificador", "Tipo", "Alícuota %", "Ocupado"])
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

        # numero — campo obligatorio (NOT NULL en schema)
        self.identifier_input = QLineEdit()
        self.identifier_input.setPlaceholderText("Ej. A-101")

        # piso — campo opcional (NULL en schema)
        self.piso_input = QLineEdit()
        self.piso_input.setPlaceholderText("Ej. 3")

        # tipo — ENUM: DEPARTAMENTO | CASA | LOCAL | OFICINA
        self.type_combo = QComboBox()
        self.type_combo.addItems(TIPO_UNIDAD_ENUM)

        # alicuota — numeric(8,6), opcional
        self.alicuota_input = QLineEdit()
        self.alicuota_input.setPlaceholderText("Ej. 45.50")

        # estadoId — FK a estado_unidad (NOT NULL en schema)
        self.estado_combo = QComboBox()
        for label, _ in ESTADO_UNIDAD_OPTIONS:
            self.estado_combo.addItem(label)

        form_layout.addRow("ID:", self.id_input)
        form_layout.addRow("Número*:", self.identifier_input)
        form_layout.addRow("Piso:", self.piso_input)
        form_layout.addRow("Tipo*:", self.type_combo)
        form_layout.addRow("Alícuota:", self.alicuota_input)
        form_layout.addRow("Estado*:", self.estado_combo)

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

    def _get_estado_id(self):
        """Devuelve el estadoId (int) correspondiente al item seleccionado en estado_combo."""
        idx = self.estado_combo.currentIndex()
        if 0 <= idx < len(ESTADO_UNIDAD_OPTIONS):
            return ESTADO_UNIDAD_OPTIONS[idx][1]
        return 1  # fallback: HABITADO

    def load_data(self):
        selected = self.table.selectedItems()
        selected_id = None
        if selected:
            row = selected[0].row()
            selected_id = self.table.item(row, 0).text()

        units = self.controller.get_all_units()
        
        self.table.blockSignals(True)
        populate_table(self.table, [
            [str(u.id), u.identifier, u.unit_type, str(u.alicuota), u.estado_nombre]
            for u in units
        ])

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
            self.id_input.setText(self.table.item(row, 0).text())
            self.identifier_input.setText(self.table.item(row, 1).text())
            self.type_combo.setCurrentText(self.table.item(row, 2).text())
            self.alicuota_input.setText(self.table.item(row, 3).text())
            # Restaurar estado en el combo por nombre
            estado_nombre = self.table.item(row, 4).text()
            for i, (label, _) in enumerate(ESTADO_UNIDAD_OPTIONS):
                if label == estado_nombre:
                    self.estado_combo.setCurrentIndex(i)
                    break

    def save_unit(self):
        identifier = self.identifier_input.text().strip()
        if not identifier:
            QMessageBox.warning(self, "Error", "El número de unidad es obligatorio")
            return

        try:
            alicuota_str = self.alicuota_input.text().strip()
            alicuota = float(alicuota_str) if alicuota_str else 0.0
            if alicuota < 0:
                QMessageBox.warning(self, "Error", "La alícuota no puede ser negativa.")
                return

            piso = self.piso_input.text().strip() or None
            estado_id = self._get_estado_id()

            self.controller.add_unit(
                numero=identifier,
                tipo=self.type_combo.currentText(),   # ya en UPPERCASE por el ENUM
                alicuota=alicuota,
                piso=piso,
                estado_id=estado_id
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
            QMessageBox.warning(self, "Error", "El número de unidad es obligatorio")
            return

        try:
            alicuota_str = self.alicuota_input.text().strip()
            alicuota = float(alicuota_str) if alicuota_str else 0.0
            if alicuota < 0:
                QMessageBox.warning(self, "Error", "La alícuota no puede ser negativa.")
                return

            piso = self.piso_input.text().strip() or None
            estado_id = self._get_estado_id()

            self.controller.update_unit(
                unit_id=int(unit_id),
                numero=identifier,
                tipo=self.type_combo.currentText(),
                alicuota=alicuota,
                piso=piso,
                estado_id=estado_id
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
        self.piso_input.clear()
        self.alicuota_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.estado_combo.setCurrentIndex(0)
        self.table.clearSelection()
