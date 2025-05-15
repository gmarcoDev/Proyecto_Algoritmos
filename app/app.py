from flask import Flask, render_template, jsonify  # render es una función para devolver nuestra plantilla index
from flask_mysqldb import MySQL
from models.models import NodoPelicula, ListaCircularEnlazada

app = Flask(__name__)

# Conexión a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'cinedb'

mysql = MySQL(app)

# Ruta para la página principal
@app.route('/')
def index():
    # Crear una lista circular enlazada
    lista_peliculas = ListaCircularEnlazada()

    # Consulta de las películas en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT titulo, descripcion, imagen FROM Peliculas")
    peliculas = cursor.fetchall()

    # Agregar las películas a la lista circular
    for idx, pelicula in enumerate(peliculas):
        lista_peliculas.agregar_pelicula(pelicula[0], pelicula[1], idx, pelicula[2])  # Ahora también pasamos 'imagen'

    # Obtener la primera película
    pelicula_actual = lista_peliculas.obtener_primera_pelicula()

    # Pasar la película actual a la plantilla
    data = {
        'titulo': 'Peliculas en Estreno',
        'bienvenida': '¡Disfruta de nuestra selección de películas!',
        'pelicula_actual': pelicula_actual
    }

    return render_template('index.html', data=data)

# Ruta para ver una película específica
@app.route('/pelicula/<int:indice>', methods=['GET'])
def ver_pelicula(indice):
    # Crear una lista circular enlazada
    lista_peliculas = ListaCircularEnlazada()

    # Consulta de las películas en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT titulo, descripcion, imagen FROM Peliculas")  # Ahora traemos 'imagen' también
    peliculas = cursor.fetchall()

    # Agregar las películas a la lista circular
    for idx, pelicula in enumerate(peliculas):
        lista_peliculas.agregar_pelicula(pelicula[0], pelicula[1], idx, pelicula[2])  # Pasamos 'imagen' aquí también

    # Obtener la película actual a partir del índice
    pelicula_actual = lista_peliculas.obtener_primera_pelicula()
    while pelicula_actual:
        if pelicula_actual.indice == indice:
            break
        pelicula_actual = lista_peliculas.obtener_siguiente(pelicula_actual)

    # Pasar la película actual a la plantilla
    data = {
        'titulo': 'Peliculas en Estreno',
        'bienvenida': '¡Disfruta de nuestra selección de películas!',
        'pelicula_actual': pelicula_actual
    }

    return render_template('index.html', data=data)

@app.route('/login')
def login():
    return render_template('login.html')  # Asegúrate de tener esta plantilla

@app.route('/registrarse')
def registrarse():
    return render_template('registrarse.html')  # Asegúrate de tener esta plantilla



if __name__ == '__main__':
    app.run(debug=True)
