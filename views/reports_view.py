from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QFileDialog)
from controllers.finance_controller import FinanceController
from controllers.operations_controller import OperationsController
import os

class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.fin_controller = FinanceController()
        self.op_controller = OperationsController()
        self.setup_ui()

    def _get_pandas(self):
        """Importa pandas y muestra advertencia si no está instalado.

        Returns:
            El módulo ``pandas`` si está disponible, ``None`` en caso contrario.
        """
        try:
            import pandas as pd
            return pd
        except ImportError:
            QMessageBox.warning(
                self, "Dependencia Faltante",
                "La librería 'pandas' no está instalada. "
                "Ejecute 'pip install pandas' para habilitar los reportes."
            )
            return None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Generación de Reportes")
        title.setObjectName("ViewTitle")
        layout.addWidget(title)
        
        lbl_info = QLabel("Exporta los datos del sistema a Excel para análisis detallado.")
        layout.addWidget(lbl_info)
        
        btn_layout = QHBoxLayout()
        
        self.btn_export_quotas = QPushButton("Exportar Cuotas (Excel)")
        self.btn_export_quotas.setObjectName("SuccessBtn")
        self.btn_export_quotas.clicked.connect(self.export_quotas)
        
        self.btn_export_expenses = QPushButton("Exportar Egresos (Excel)")
        self.btn_export_expenses.setObjectName("PrimaryBtn")
        self.btn_export_expenses.clicked.connect(self.export_expenses)
        
        btn_layout.addWidget(self.btn_export_quotas)
        btn_layout.addWidget(self.btn_export_expenses)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()

    def export_quotas(self):
        pd = self._get_pandas()
        if pd is None:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", "Cuotas.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return
            
        quotas = self.fin_controller.get_all_quotas()
        data = [{
            "ID": q.id, "Unidad ID": q.unit_id, "Emision": q.issue_date, 
            "Vencimiento": q.due_date, "Monto": q.amount, 
            "Tipo": q.quota_type, "Pagada": "Si" if q.is_paid else "No"
        } for q in quotas]
        
        try:
            df = pd.DataFrame(data)
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Éxito", "Reporte de Cuotas exportado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Fallo al exportar: {e}")

    def export_expenses(self):
        pd = self._get_pandas()
        if pd is None:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", "Egresos.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return
            
        expenses = self.op_controller.get_all_expenses()
        data = [{
            "ID": e.id, "Fecha": e.date, "Monto": e.amount, 
            "Categoria": e.category, "Descripcion": e.description
        } for e in expenses]
        
        try:
            df = pd.DataFrame(data)
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Éxito", "Reporte de Egresos exportado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Fallo al exportar: {e}")
