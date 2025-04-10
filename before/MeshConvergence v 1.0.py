import sqlite3
import matplotlib.pyplot as plt


# Solicitar el nombre del archivo
archivo=input("Ingrese nombre del archivo: ").strip()
while not archivo:
    archivo=input("Ingrese nombre del archivo: ").strip()

# Conectar a la base de datos
conn=sqlite3.connect(f"{archivo}.db")
cursor=conn.cursor()

# Crear la tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS simulaciones (
                    iteracion INTEGER PRIMARY KEY AUTOINCREMENT,
                    n_elementos INTEGER,
                    resultado REAL)''')

# Selección de tipo de análisis
while True:
    entrada=input("Tensiones(0) / Deflexiones(1): ").strip()
    if entrada in ["0", "1"]:
        break
    print("Error: Debe ingresar 0 o 1.")

dato = "tensión" if entrada=="0" else "deflexión"
print(f"Seleccionaste: {dato.capitalize()}")

# Cargar datos en la base de datos
while True:
    try:
        n_elementos=input("Ingrese el número de elementos (o 'salir' para terminar): ").strip()
        if n_elementos.lower()=='salir':
            break
        
        resultado=input(f"Ingrese el resultado de la {dato}: ").strip()

        cursor.execute("INSERT INTO simulaciones (n_elementos, resultado) VALUES (?, ?)", 
                    (int(n_elementos), float(resultado)))
        conn.commit()
        print("Datos guardados correctamente.\n")

    except ValueError:
        print("Error: Ingrese números válidos para la malla y el resultado.\n")
    except KeyboardInterrupt:
        print("\nInterrupción detectada. Cerrando el programa.")
        break

# Obtener datos para graficar
def graficar():
    cursor.execute("SELECT n_elementos, resultado FROM simulaciones ORDER BY n_elementos ASC")
    datos = cursor.fetchall()
    conn.close()

    #Extraer listas
    elementos=[element[0] for element in datos]
    resultados=[element[1] for element in datos]

    #Graficar convergencia
    plt.figure(figsize=(8, 5))
    plt.plot(elementos, resultados, marker='o', linestyle='-', color='b', markersize=6, label=f"Convergencia de {dato}")

    #Ajustes visuales
    plt.xscale("log")  # Escala logarítmica en el eje X
    plt.xlabel("Número de Elementos")
    plt.ylabel(f"{dato.capitalize()}")
    plt.title(f"Convergencia de malla")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.show()



#DATASHEET
def datasheet():
#Conectar a la base de datos
    conn = sqlite3.connect(f"{archivo}.db")
    cursor = conn.cursor()

    #Obtener todos los datos
    cursor.execute("SELECT * FROM simulaciones")  
    datos = cursor.fetchall()  # Trae todas las filas de la tabla

    #Mostrar los datos
    print("Datos de la base de datos:")

    anterior=[0]
    for lista in datos:
        error_rel=(lista[2]-anterior[0])/lista[2]
        anterior[0]=lista[2] 
        print(abs(error_rel))
        
    #Error relativo porcentual

    #Cerrar conexión
    conn.close()

graficar()
datasheet()




