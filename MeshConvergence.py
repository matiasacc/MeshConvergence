import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QFrame, QHeaderView)
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sqlite3
import matplotlib.pyplot as plt
import os


def ruta_recurso(rel_path):
    """Devuelve la ruta absoluta del recurso, compatible con PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

class MeshConvergenceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(ruta_recurso("frente.ico")))
        self.setWindowTitle("MeshConvergence v1.0")
        self.setGeometry(100, 100, 310, 500)
        
        layout = QVBoxLayout()
        
        # Logo
        self.logo_label = QLabel(self)
        pixmap = QPixmap(ruta_recurso("logo.png")).scaled(300, 175, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)
        
        # Espaciador
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Nombre del archivo
        layout.addWidget(QLabel("Nombre del archivo:"))
        self.archivo_entry = QLineEdit()
        layout.addWidget(self.archivo_entry)
        
        # Tipo de análisis
        layout.addWidget(QLabel("Tipo de análisis:"))
        self.tipo_var = QButtonGroup()
        self.radio_tensiones = QRadioButton("Tensiones")
        self.radio_deflexiones = QRadioButton("Deflexiones")
        self.radio_tensiones.setChecked(True)
        self.tipo_var.addButton(self.radio_tensiones, 0)
        self.tipo_var.addButton(self.radio_deflexiones, 1)
        
        tipo_layout = QHBoxLayout()
        tipo_layout.addWidget(self.radio_tensiones)
        tipo_layout.addWidget(self.radio_deflexiones)
        layout.addLayout(tipo_layout)
        
        # Entrada de datos
        layout.addWidget(QLabel("Número de elementos:"))
        self.n_elementos_entry = QLineEdit()
        layout.addWidget(self.n_elementos_entry)
        
        layout.addWidget(QLabel("Resultado:"))
        self.resultado_entry = QLineEdit()
        layout.addWidget(self.resultado_entry)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.guardar_btn = QPushButton("Guardar Datos")
        self.guardar_btn.clicked.connect(self.guardar_datos)
        btn_layout.addWidget(self.guardar_btn)
        
        self.graficar_btn = QPushButton("Graficar")
        self.graficar_btn.clicked.connect(self.graficar)
        btn_layout.addWidget(self.graficar_btn)
        
        layout.addLayout(btn_layout)
        
        # Espaciador
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Tabla de datos centrada
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Elementos", "Resultado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def conectar_db(self):
        archivo = self.archivo_entry.text().strip()
        if not archivo:
            QMessageBox.critical(self, "Error", "Ingrese un nombre de archivo")
            return None, None

        # Crear carpeta "database" si no existe
        db_folder = "database"
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)

        # Ruta completa al archivo .db dentro de la carpeta
        db_path = os.path.join(db_folder, f"{archivo}.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS simulaciones (
                            iteracion INTEGER PRIMARY KEY AUTOINCREMENT,
                            n_elementos INTEGER,
                            resultado REAL)''')
        return conn, cursor

    
    def guardar_datos(self):
        conn, cursor = self.conectar_db()
        if not conn:
            return
        try:
            n_elementos = int(self.n_elementos_entry.text().strip())
            resultado = float(self.resultado_entry.text().strip())
            cursor.execute("INSERT INTO simulaciones (n_elementos, resultado) VALUES (?, ?)", (n_elementos, resultado))
            conn.commit()
            conn.close()
            self.actualizar_tabla()
            self.n_elementos_entry.clear()
            self.resultado_entry.clear()
            QMessageBox.information(self, "Éxito", "Datos guardados correctamente")
        except ValueError:
            QMessageBox.critical(self, "Error", "Ingrese valores numéricos válidos")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def actualizar_tabla(self):
        conn, cursor = self.conectar_db()
        if not conn:
            return
        cursor.execute("SELECT n_elementos, resultado FROM simulaciones ORDER BY n_elementos ASC")
        datos = cursor.fetchall()
        conn.close()
        self.table.setRowCount(0)
        for row in datos:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_position, 1, QTableWidgetItem(str(row[1])))
    
    def graficar(self):
        conn, cursor = self.conectar_db()
        if not conn:
            return
        cursor.execute("SELECT n_elementos, resultado FROM simulaciones ORDER BY n_elementos ASC")
        datos = cursor.fetchall()
        conn.close()
        
        if not datos:
            QMessageBox.critical(self, "Error", "No hay datos para graficar")
            return
        
        elementos, resultados = zip(*datos)
        plt.figure(figsize=(8, 5))
        plt.plot(elementos, resultados, marker='o', linestyle='-', color='b', markersize=6, label=f"Convergencia de {'Tensión' if self.tipo_var.checkedId() == 0 else 'Deflexión'}")
        plt.xscale("log")
        plt.xlabel("Número de Elementos")
        plt.ylabel("Resultado")
        plt.title("Convergencia de malla")
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.legend()
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ruta_recurso("frente.ico")))
    window = MeshConvergenceApp()
    window.show()
    sys.exit(app.exec())


#pyinstaller --noconsole --onefile --icon=frente.ico --add-data "logo.png;." --add-data "frente.ico;." MeshConvergence.py
