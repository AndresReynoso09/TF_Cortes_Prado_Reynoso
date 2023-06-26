import pandas as pd
import networkx as nx
import tkinter as tk
from PIL import Image, ImageTk
import os

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

# Función para buscar canciones relacionadas
def buscar_canciones(relacion):
    resultados = []
    for index, row in canciones_df.iterrows():
        cancion = row['Canción']
        artista = row['Artista']
        album = row['Álbum']
        if relacion.lower() in cancion.lower() or relacion.lower() in artista.lower() or relacion.lower() in album.lower():
            resultados.append((cancion, artista, album))

    return resultados