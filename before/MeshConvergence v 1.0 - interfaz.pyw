import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import matplotlib.pyplot as plt

class MeshConvergenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MeshConvergence v1.0")
        self.root.geometry("500x800")
        self.root.configure(bg='white')

        try:
            imagen = Image.open("logo.png")
            imagen = imagen.resize((300, 175))
            self.logo = ImageTk.PhotoImage(imagen)  # Asigna la imagen a una variable de instancia
            label_logo = tk.Label(root, image=self.logo, bg="white")  # Usa self.logo en vez de logo
            label_logo.pack(pady=10)
        except Exception as e:
            print(f"No se pudo cargar la imagen: {e}")
        
        # Contenedor principal
        frame = tk.Frame(root, padx=10, pady=10, bg='white')
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nombre del archivo
        tk.Label(frame, text="Nombre del archivo:", bg='white', fg='black').pack(anchor="w")
        self.archivo_entry = tk.Entry(frame)
        self.archivo_entry.pack(fill=tk.X, pady=5)
        
        # Selector de análisis
        self.tipo_var = tk.StringVar(value="0")
        frame_tipo = tk.Frame(frame, bg='white')
        frame_tipo.pack(fill=tk.X, pady=5)
        tk.Label(frame_tipo, text="Tipo de análisis:", bg='white', fg='black').pack(anchor="w")
        tk.Radiobutton(frame_tipo, text="Tensiones", variable=self.tipo_var, value="0", bg='white', fg='black').pack(side=tk.LEFT)
        tk.Radiobutton(frame_tipo, text="Deflexiones", variable=self.tipo_var, value="1", bg='white', fg='black').pack(side=tk.LEFT)
        
        # Entrada de datos
        tk.Label(frame, text="Número de elementos:", bg='white', fg='black').pack(anchor="w")
        self.n_elementos_entry = tk.Entry(frame)
        self.n_elementos_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text="Resultado:", bg='white', fg='black').pack(anchor="w")
        self.resultado_entry = tk.Entry(frame)
        self.resultado_entry.pack(fill=tk.X, pady=5)
        
        # Botones
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Guardar Datos", command=self.guardar_datos).pack(side=tk.LEFT, expand=True)
        tk.Button(btn_frame, text="Graficar", command=self.graficar).pack(side=tk.RIGHT, expand=True)
        
        # Tabla de datos
        self.tree = ttk.Treeview(frame, columns=("#1", "#2"), show='headings', height=6)
        self.tree.heading("#1", text="Elementos")
        self.tree.heading("#2", text="Resultado")
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def conectar_db(self):
        archivo = self.archivo_entry.get().strip()
        if not archivo:
            messagebox.showerror("Error", "Ingrese un nombre de archivo")
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
            n_elementos = int(self.n_elementos_entry.get().strip())
            resultado = float(self.resultado_entry.get().strip())
            cursor.execute("INSERT INTO simulaciones (n_elementos, resultado) VALUES (?, ?)", (n_elementos, resultado))
            conn.commit()
            conn.close()
            self.actualizar_tabla()
            self.n_elementos_entry.delete(0, tk.END)
            self.resultado_entry.delete(0, tk.END)
            messagebox.showinfo("Éxito", "Datos guardados correctamente")
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def actualizar_tabla(self):
        conn, cursor = self.conectar_db()
        if not conn:
            return
        cursor.execute("SELECT n_elementos, resultado FROM simulaciones ORDER BY n_elementos ASC")
        datos = cursor.fetchall()
        conn.close()
        self.tree.delete(*self.tree.get_children())
        for row in datos:
            self.tree.insert("", "end", values=row)
    
    def graficar(self):
        conn, cursor = self.conectar_db()
        if not conn:
            return
        cursor.execute("SELECT n_elementos, resultado FROM simulaciones ORDER BY n_elementos ASC")
        datos = cursor.fetchall()
        conn.close()
        
        if not datos:
            messagebox.showerror("Error", "No hay datos para graficar")
            return
        
        elementos, resultados = zip(*datos)
        plt.figure(figsize=(8, 5))
        plt.plot(elementos, resultados, marker='o', linestyle='-', color='b', markersize=6, label=f"Convergencia de {'Tensión' if self.tipo_var.get() == '0' else 'Deflexión'}")
        plt.xscale("log")
        plt.xlabel("Número de Elementos")
        plt.ylabel("Resultado")
        plt.title("Convergencia de malla")
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.legend()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = MeshConvergenceApp(root)
    root.mainloop()
