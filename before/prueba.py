from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QRadioButton, QFileDialog
import sqlite3
import matplotlib.pyplot as plt
import sys

class MeshConvergenceApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("MeshConvergence v1.0")
        self.setGeometry(100, 100, 500, 800)
        layout = QVBoxLayout()

        # Logo
        try:
            self.logo_label = QLabel(self)
            pixmap = QtGui.QPixmap("logo.png").scaled(300, 175)
            self.logo_label.setPixmap(pixmap)
            layout.addWidget(self.logo_label)
        except Exception as e:
            print(f"No se pudo cargar la imagen: {e}")

        # Nombre del archivo
        layout.addWidget(QLabel("Nombre del archivo:"))
        self.archivo_entry = QLineEdit(self)
        layout.addWidget(self.archivo_entry)

        # Tipo de análisis
        layout.addWidget(QLabel("Tipo de análisis:"))
        self.tension_radio = QRadioButton("Tensiones")
        self.deflexion_radio = QRadioButton("Deflexiones")
        self.tension_radio.setChecked(True)
        layout.addWidget(self.tension_radio)
        layout.addWidget(self.deflexion_radio)

        # Número de elementos
        layout.addWidget(QLabel("Número de elementos:"))
        self.n_elementos_entry = QLineEdit(self)
        layout.addWidget(self.n_elementos_entry)

        # Resultado
        layout.addWidget(QLabel("Resultado:"))
        self.resultado_entry = QLineEdit(self)
        layout.addWidget(self.resultado_entry)

        # Botones
        self.guardar_btn = QPushButton("Guardar Datos")
        self.guardar_btn.clicked.connect(self.guardar_datos)
        layout.addWidget(self.guardar_btn)

        self.graficar_btn = QPushButton("Graficar")
        self.graficar_btn.clicked.connect(self.graficar)
        layout.addWidget(self.graficar_btn)

        # Tabla
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Elementos", "Resultado"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def conectar_db(self):
        archivo = self.archivo_entry.text().strip()
        if not archivo:
            QMessageBox.critical(self, "Error", "Ingrese un nombre de archivo")
            return None, None
        conn = sqlite3.connect(f"{archivo}.db")
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

        self.table.setRowCount(len(datos))
        for row_idx, row_data in enumerate(datos):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

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
        plt.plot(elementos, resultados, marker='o', linestyle='-', color='b', markersize=6,
                 label=f"Convergencia de {'Tensión' if self.tension_radio.isChecked() else 'Deflexión'}")
        plt.xscale("log")
        plt.xlabel("Número de Elementos")
        plt.ylabel("Resultado")
        plt.title("Convergencia de malla")
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.legend()
        plt.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MeshConvergenceApp()
    window.show()
    sys.exit(app.exec())
