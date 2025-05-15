class NodoPelicula:
    def __init__(self, titulo, descripcion, indice, imagen):
        self.titulo = titulo
        self.descripcion = descripcion
        self.siguiente = None  # Puntero al siguiente nodo (película)
        self.anterior = None  # Puntero al nodo anterior (película)
        self.indice = indice  # Índice de la película en la lista (posición)
        self.imagen = imagen  # Ruta o nombre de archivo de la imagen de la película

class ListaCircularEnlazada:
    def __init__(self):
        self.head = None  # Primer nodo
        self.tail = None  # Último nodo

    # Asegúrate de que el método acepte 4 parámetros
    def agregar_pelicula(self, titulo, descripcion, indice, imagen):
        nuevo_nodo = NodoPelicula(titulo, descripcion, indice, imagen)
        
        if not self.head:  # Si la lista está vacía
            self.head = nuevo_nodo
            self.tail = nuevo_nodo
            self.head.siguiente = self.head  # El siguiente de head es el mismo head (circular)
            self.head.anterior = self.tail  # El anterior de head es tail
        else:
            self.tail.siguiente = nuevo_nodo
            nuevo_nodo.anterior = self.tail
            nuevo_nodo.siguiente = self.head  # El siguiente del nuevo nodo apunta al head (circular)
            self.head.anterior = nuevo_nodo  # El anterior del head apunta al nuevo nodo
            self.tail = nuevo_nodo  # Ahora el nuevo nodo es el tail

    # Obtener la primera película
    def obtener_primera_pelicula(self):
        return self.head

    # Obtener la siguiente película
    def obtener_siguiente(self, pelicula_actual):
        return pelicula_actual.siguiente

    # Obtener la película anterior
    def obtener_anterior(self, pelicula_actual):
        return pelicula_actual.anterior
