from flask import Flask, render_template, request #convierte los datos a formato json 
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
    cursor = mysql.connection.cursor() #nuestro puente para la conexion con la db
    cursor.execute("SELECT titulo, descripcion, imagen FROM Peliculas")
    peliculas = cursor.fetchall() #nos devuelve la info en tuplas

    # Agregar las películas a la lista circular
    for idx, pelicula in enumerate(peliculas):  #recorremos todas las peliculas
        lista_peliculas.agregar_pelicula(pelicula[0], pelicula[1], idx, pelicula[2], None)  # guardamos el titulo la descipcion y la imagen en una lista enlazada y el 'None' ya que no se está usando el género aquí

    # Obtener las tres películas
    pelicula_actual = lista_peliculas.obtener_primera_pelicula()  #dame la primera pelicula 
    pelicula_siguiente = lista_peliculas.obtener_siguiente(pelicula_actual)  #dame la siguiente 
    pelicula_tercera = lista_peliculas.obtener_siguiente(pelicula_siguiente)  # luego la q sigue 

    # Obtener la anterior de la actual
    pelicula_anterior = lista_peliculas.obtener_anterior(pelicula_actual)  #la anterior a la primera 
    pelicula_siguiente_siguiente = lista_peliculas.obtener_siguiente(pelicula_tercera)  #una mas q sigue 

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
        lista_peliculas.agregar_pelicula(pelicula[0], pelicula[1], idx, pelicula[2], None)  # 'None' aquí también para no usar género

    # Obtener la película actual a partir del índice
    pelicula_actual = lista_peliculas.obtener_primera_pelicula()
    while pelicula_actual:
        if pelicula_actual.indice == indice:
            break
        pelicula_actual = lista_peliculas.obtener_siguiente(pelicula_actual)

    # Obtener las siguientes y anteriores películas
    pelicula_anterior = lista_peliculas.obtener_anterior(pelicula_actual)
    pelicula_siguiente = lista_peliculas.obtener_siguiente(pelicula_actual)
    pelicula_siguiente_siguiente = lista_peliculas.obtener_siguiente(pelicula_siguiente)
    
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
        'pelicula_tercera': pelicula_tercera  # Añadimos correctamente 'pelicula_tercera'
    }

    return render_template('index.html', data=data)

@app.route('/peliculas', methods=['GET', 'POST'])
def peliculas():
    cursor = mysql.connection.cursor()

    # Obtener géneros y películas para los desplegables
    cursor.execute("SELECT id, nombre FROM Generos")
    generos = cursor.fetchall()

    cursor.execute("SELECT id, titulo, descripcion, imagen, genero_id FROM Peliculas")
    peliculas_db = cursor.fetchall()

    lista_peliculas = ListaCircularEnlazada()
    for idx, pelicula in enumerate(peliculas_db):
        genero = next((g[1] for g in generos if g[0] == pelicula[4]), None)
        lista_peliculas.agregar_pelicula(pelicula[1], pelicula[2], idx, pelicula[3], genero)

    # Variables para pasar al template
    peliculas_desplegable = []
    resultados = None
    tipo_busqueda = 'genero'  # valor por defecto
    busqueda_seleccionada = None

    if request.method == 'POST':
        tipo_busqueda = request.form.get('tipo_busqueda')
        busqueda_seleccionada = request.form.get('busqueda')

        if tipo_busqueda == 'genero':
            resultados = lista_peliculas.buscar_por_genero(busqueda_seleccionada)
            peliculas_desplegable = [{'nombre': g[1]} for g in generos]
        elif tipo_busqueda == 'nombre':
            pelicula = lista_peliculas.buscar_por_nombre(busqueda_seleccionada)
            resultados = [pelicula] if pelicula else []
            peliculas_desplegable = [{'titulo': p[1]} for p in peliculas_db]
    else:
        # GET: mostrar todos
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
    return render_template('registrarse.html')  # Asegúrate de tener esta plantilla

if __name__ == '__main__':
    app.run(debug=True)
