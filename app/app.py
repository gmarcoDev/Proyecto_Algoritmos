# convierte los datos a formato json
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from models.models import NodoPelicula, ListaCircularEnlazada

app = Flask(__name__)

# Conexión a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1590'
app.config['MYSQL_DB'] = 'cinedb'

mysql = MySQL(app)

# Ruta para la página principal


@app.route('/')
def index():
    # Crear una lista circular enlazada
    lista_peliculas = ListaCircularEnlazada()

    # Consulta de las películas en la base de datos
    cursor = mysql.connection.cursor()  # nuestro puente para la conexion con la db
    cursor.execute("SELECT titulo, descripcion, imagen FROM Peliculas")
    peliculas = cursor.fetchall()  # nos devuelve la info en tuplas

    # Agregar las películas a la lista circular
    # recorremos todas las peliculas
    for idx, pelicula in enumerate(peliculas):
        # guardamos el titulo la descipcion y la imagen en una lista enlazada y el 'None' ya que no se está usando el género aquí
        lista_peliculas.agregar_pelicula(
            pelicula[0], pelicula[1], idx, pelicula[2], None)

    # Obtener las tres películas
    # dame la primera pelicula
    pelicula_actual = lista_peliculas.obtener_primera_pelicula()
    pelicula_siguiente = lista_peliculas.obtener_siguiente(
        pelicula_actual)  # dame la siguiente
    pelicula_tercera = lista_peliculas.obtener_siguiente(
        pelicula_siguiente)  # luego la q sigue

    # Obtener la anterior de la actual
    pelicula_anterior = lista_peliculas.obtener_anterior(
        pelicula_actual)  # la anterior a la primera
    pelicula_siguiente_siguiente = lista_peliculas.obtener_siguiente(
        pelicula_tercera)  # una mas q sigue

    # Pasar las películas actuales a la plantilla para mostrar en el index
    data = {
        'titulo': 'Peliculas en Estreno',
        'bienvenida': '¡Disfruta de nuestra selección de películas!',
        'pelicula_actual': pelicula_actual,
        'pelicula_siguiente': pelicula_siguiente,
        'pelicula_tercera': pelicula_tercera,
        'pelicula_anterior': pelicula_anterior,
        'pelicula_siguiente_siguiente': pelicula_siguiente_siguiente
    }

    return render_template('index.html', data=data)


@app.route('/pelicula/<int:indice>', methods=['GET'])
def ver_pelicula(indice):
    # Crear una lista circular enlazada
    lista_peliculas = ListaCircularEnlazada()

    # Consulta de las películas en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT titulo, descripcion, imagen FROM Peliculas")
    peliculas = cursor.fetchall()

    # Agregar las películas a la lista circular
    for idx, pelicula in enumerate(peliculas):
        # 'None' aquí también para no usar género
        lista_peliculas.agregar_pelicula(
            pelicula[0], pelicula[1], idx, pelicula[2], None)

    # Obtener la película actual a partir del índice
    pelicula_actual = lista_peliculas.obtener_primera_pelicula()
    while pelicula_actual:
        if pelicula_actual.indice == indice:
            break
        pelicula_actual = lista_peliculas.obtener_siguiente(pelicula_actual)

    # Obtener las siguientes y anteriores películas
    pelicula_anterior = lista_peliculas.obtener_anterior(pelicula_actual)
    pelicula_siguiente = lista_peliculas.obtener_siguiente(pelicula_actual)
    pelicula_siguiente_siguiente = lista_peliculas.obtener_siguiente(
        pelicula_siguiente)

    # Aquí nos aseguramos de que la clave 'pelicula_tercera' esté correctamente definida
    pelicula_tercera = pelicula_siguiente_siguiente

    # Pasar las películas actuales a la plantilla
    data = {
        'titulo': 'Peliculas en Estreno',
        'bienvenida': '¡Disfruta de nuestra selección de películas!',
        'pelicula_actual': pelicula_actual,
        'pelicula_anterior': pelicula_anterior,
        'pelicula_siguiente': pelicula_siguiente,
        'pelicula_siguiente_siguiente': pelicula_siguiente_siguiente,  # Esto ya está aquí
        # Añadimos correctamente 'pelicula_tercera'
        'pelicula_tercera': pelicula_tercera
    }

    return render_template('index.html', data=data)


@app.route('/peliculas', methods=['GET', 'POST'])
def peliculas():
    cursor = mysql.connection.cursor()

    # Obtener géneros y películas para desplegables
    cursor.execute("SELECT id, nombre FROM Generos")
    generos = cursor.fetchall()

    cursor.execute(
        "SELECT id, titulo, descripcion, imagen, genero_id FROM Peliculas")
    peliculas_db = cursor.fetchall()

    lista_peliculas = ListaCircularEnlazada()
    for idx, pelicula in enumerate(peliculas_db):
        genero = next((g[1] for g in generos if g[0] == pelicula[4]), None)
        lista_peliculas.agregar_pelicula(
            pelicula[1], pelicula[2], idx, pelicula[3], genero)

    tipo_busqueda = 'genero'
    busqueda_seleccionada = None
    resultados = None
    peliculas_desplegable = []

    if request.method == 'POST':
        tipo_busqueda = request.form.get('tipo_busqueda')
        busqueda_seleccionada = request.form.get('busqueda')

        # Normalizar valores "vacío" o "Todas" a None para facilitar lógica
        if busqueda_seleccionada in [None, '', 'Todas']:
            busqueda_seleccionada = None

        if tipo_busqueda == 'genero':
            if not busqueda_seleccionada:
                # Mostrar todas las películas
                peliculas_formateadas = []
                for idx, pelicula in enumerate(peliculas_db):
                    genero = next(
                        (g[1] for g in generos if g[0] == pelicula[4]), None)
                    peliculas_formateadas.append({
                        'indice': idx,
                        'titulo': pelicula[1],
                        'descripcion': pelicula[2],
                        'imagen': pelicula[3],
                        'genero': genero,
                    })
                resultados = peliculas_formateadas
            else:
                resultados = lista_peliculas.buscar_por_genero(
                    busqueda_seleccionada)
                if not resultados:
                    # Si no hay resultados, mostrar todas las películas
                    peliculas_formateadas = []
                    for idx, pelicula in enumerate(peliculas_db):
                        genero = next(
                            (g[1] for g in generos if g[0] == pelicula[4]), None)
                        peliculas_formateadas.append({
                            'indice': idx,
                            'titulo': pelicula[1],
                            'descripcion': pelicula[2],
                            'imagen': pelicula[3],
                            'genero': genero,
                        })
                    resultados = peliculas_formateadas
            peliculas_desplegable = [{'nombre': g[1]} for g in generos]

        elif tipo_busqueda == 'nombre':
            if busqueda_seleccionada:
                pelicula = lista_peliculas.buscar_por_nombre(
                    busqueda_seleccionada)
                resultados = [pelicula] if pelicula else []
            else:
                # Mostrar todas si no se selecciona nombre
                peliculas_formateadas = []
                for idx, pelicula in enumerate(peliculas_db):
                    genero = next(
                        (g[1] for g in generos if g[0] == pelicula[4]), None)
                    peliculas_formateadas.append({
                        'indice': idx,
                        'titulo': pelicula[1],
                        'descripcion': pelicula[2],
                        'imagen': pelicula[3],
                        'genero': genero,
                    })
                resultados = peliculas_formateadas
            peliculas_desplegable = [{'titulo': p[1]} for p in peliculas_db]

    else:
        # GET: mostrar todas las películas
        peliculas_formateadas = []
        for idx, pelicula in enumerate(peliculas_db):
            genero = next((g[1] for g in generos if g[0] == pelicula[4]), None)
            peliculas_formateadas.append({
                'indice': idx,
                'titulo': pelicula[1],
                'descripcion': pelicula[2],
                'imagen': pelicula[3],
                'genero': genero,
            })
        resultados = peliculas_formateadas
        peliculas_desplegable = [{'nombre': g[1]} for g in generos]

    return render_template('peliculas.html',
                           generos=generos,
                           peliculas_desplegable=peliculas_desplegable,
                           resultados=resultados,
                           tipo_busqueda=tipo_busqueda,
                           busqueda_seleccionada=busqueda_seleccionada)


@app.route('/login')
def login():
    return render_template('login.html')  # Asegúrate de tener esta plantilla


@app.route('/registrarse')
def registrarse():
    # Asegúrate de tener esta plantilla
    return render_template('registrarse.html')


@app.route('/cines')
def cines():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nombre, direccion, telefono FROM Cines")
        cines_db = cursor.fetchall()
        cines = [{'id': c[0], 'nombre': c[1], 'direccion': c[2], 'telefono': c[3]} for c in cines_db]
        return render_template('cines.html', cines=cines)
    except Exception as e:
        return f"<h1>Error en la página Cines:</h1><pre>{e}</pre>"




if __name__ == '__main__':
    app.run(debug=True)
