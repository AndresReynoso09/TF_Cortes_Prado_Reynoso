import pandas as pd
import networkx as nx
import tkinter as tk
from PIL import Image, ImageTk
import os

# Implementación del algoritmo UFDS
class UFDS:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x != root_y:
            if self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            elif self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1

# Cargar los datos del archivo CSV
canciones_df = pd.read_csv('canciones.csv')
nodos_df = pd.read_csv('canciones_nodos.csv')
aristas_df = pd.read_csv('canciones_aristas.csv')

# Obtener la ruta relativa de la carpeta de imágenes
carpeta_imagenes = 'imagenes_Canciones'

# Obtener la ruta absoluta del archivo de código Python
ruta_actual = os.path.dirname(os.path.abspath(__file__))

# Crear un diccionario para mapear los nombres de las canciones con sus imágenes correspondientes
imagenes = {}
for index, row in nodos_df.iterrows():
    cancion = row['Canción']
    imagen_nombre = f'{cancion}.jpg'
    imagen_path = os.path.join(ruta_actual, carpeta_imagenes, imagen_nombre)

    try:
        imagen = Image.open(imagen_path)
        imagenes[cancion] = imagen
    except IOError:
        imagenes[cancion] = None

# Crear el grafo a partir de los datos de los nodos y las aristas
grafo = nx.from_pandas_edgelist(aristas_df, 'Source', 'Target', ['Weight', 'Label', 'Type'])

# Función para buscar canciones relacionadas utilizando UFDS
def buscar_canciones(relacion):
    resultados = []
    
    # Crear instancias de UFDS para agrupar canciones por artista y álbum
    ufds_artista = UFDS(len(canciones_df))
    ufds_album = UFDS(len(canciones_df))

    for index, row in canciones_df.iterrows():
        cancion = row['Canción']
        artista = row['Artista']
        album = row['Álbum']
        
        # Realizar uniones basadas en el nombre de canción, artista y álbum
        if relacion.lower() in cancion.lower() or relacion.lower() in artista.lower() or relacion.lower() in album.lower():
            resultados.append((cancion, artista, album))

            # Realizar uniones basadas en el índice de la canción
            ufds_artista.union(index, 0)
            ufds_album.union(index, 0)

    # Obtener los conjuntos disjuntos finales
    conjuntos_artista = []
    conjuntos_album = []
    for i in range(len(canciones_df)):
        if ufds_artista.find(i) == 0:
            conjunto_artista = set()
            conjunto_album = set()
            for j in range(len(canciones_df)):
                if ufds_artista.find(j) == 0 and ufds_artista.find(j) == ufds_artista.find(i):
                    conjunto_artista.add(j)
                if ufds_album.find(j) == 0 and ufds_album.find(j) == ufds_album.find(i):
                    conjunto_album.add(j)
            conjuntos_artista.append(conjunto_artista)
            conjuntos_album.append(conjunto_album)

    return resultados, conjuntos_artista, conjuntos_album

# Función para mostrar los resultados de la búsqueda en la interfaz gráfica
def mostrar_resultados():
    relacion = entrada.get()
    canciones_relacionadas, conjuntos_artista, conjuntos_album = buscar_canciones(relacion)

    for widget in resultados_frame.winfo_children():
        widget.destroy()

    for i, resultado in enumerate(canciones_relacionadas):
        # Calcular las coordenadas de las celdas en la cuadrícula
        row = i // 3  # Número de fila
        column = i % 3  # Número de columna

        # Crear un Frame para cada conjunto de datos de canción
        cancion_frame = tk.LabelFrame(resultados_frame, bg='black', padx=10, pady=5)
        cancion_frame.grid(row=row, column=column, padx=10, pady=5)

        # Crear un Frame interno para la imagen y los datos
        contenido_frame = tk.Frame(cancion_frame, bg='gray')
        contenido_frame.pack(padx=5, pady=5)

        imagen = imagenes.get(resultado[0])
        if imagen:
            imagen = imagen.resize((80, 80), Image.ANTIALIAS)
            imagen = ImageTk.PhotoImage(imagen)
            imagen_label = tk.Label(contenido_frame, image=imagen, bg='gray')
            imagen_label.image = imagen
            imagen_label.pack()

        cancion_label = tk.Label(contenido_frame, text=resultado[0], font=('Arial', 12, 'bold'), wraplength=200, anchor='w', bg='gray')
        cancion_label.pack()

        artista_label = tk.Label(contenido_frame, text=resultado[1], font=('Arial', 10), wraplength=200, anchor='w', bg='gray')
        artista_label.pack()

        album_label = tk.Label(contenido_frame, text=resultado[2], font=('Arial', 10), wraplength=200, anchor='w', bg='gray')
        album_label.pack()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("TrackTastic - Búsqueda de canciones")
ventana.geometry("1137x600")
ventana.config(bg="green")

# Crear el canvas para los resultados con barra de desplazamiento
canvas = tk.Canvas(ventana)
canvas.pack(side="left", fill="both", expand=True)

scrollbar_vertical = tk.Scrollbar(ventana, command=canvas.yview)
scrollbar_vertical.pack(side="right", fill="y")

resultados_frame = tk.Frame(canvas, bg='black')  # Establecer color de fondo de la sección de canciones a negro
resultados_frame.pack(pady=10)

canvas.create_window((0, 0), window=resultados_frame, anchor="nw")
canvas.config(yscrollcommand=scrollbar_vertical.set)

# Configurar el desplazamiento
def configure_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

resultados_frame.bind("<Configure>", configure_canvas)
canvas.configure(yscrollcommand=scrollbar_vertical.set)

# Crear los elementos de la interfaz gráfica
etiqueta = tk.Label(ventana, text="Ingrese una palabra o letra relacionada:", font=('Arial', 14))
etiqueta.pack(padx=10, pady=10)

entrada = tk.Entry(ventana, font=('Arial', 12))
entrada.pack(padx=10, pady=10)

boton = tk.Button(ventana, text='Buscar', font=('Arial', 14), command=mostrar_resultados)
boton.pack(padx=10, pady=10)

# Posicionar el logo más abajo
logo_label = tk.Label(ventana, text="TrackTastic", font=('Arial', 20, 'bold'), fg="#020202")
logo_label.place(relx=0.83, rely=0.5, anchor='center')  # Ajusta la posición vertical con rely

ventana.mainloop()
