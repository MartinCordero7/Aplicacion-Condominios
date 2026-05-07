"""Utilidades compartidas para las vistas PyQt6.

Contiene helpers para crear y poblar QTableWidgets, evitando la
repetición del mismo boilerplate de configuración en cada vista.
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView


def create_table(headers: list[str]) -> QTableWidget:
    """Crea y configura un QTableWidget estándar.

    Args:
        headers: Lista de etiquetas para las columnas.

    Returns:
        Un QTableWidget configurado con las columnas dadas, redimensionado
        para ocupar el ancho disponible y con selección por fila completa.
    """
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    return table


def populate_table(table: QTableWidget, rows: list[list[str]]) -> None:
    """Rellena un QTableWidget con las filas proporcionadas.

    Limpia el contenido existente antes de insertar los nuevos datos.

    Args:
        table: El QTableWidget que se va a poblar.
        rows: Lista de filas; cada fila es una lista de strings,
              uno por columna.
    """
    table.setRowCount(0)
    for i, row in enumerate(rows):
        table.insertRow(i)
        for j, value in enumerate(row):
            table.setItem(i, j, QTableWidgetItem(str(value)))
