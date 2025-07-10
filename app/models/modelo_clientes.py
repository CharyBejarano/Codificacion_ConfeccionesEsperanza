#modelo_clientes.py
def obtener_clientes(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.num_identificacion,
                p.tipoDocumento_tipo_Doc,
                CONCAT(p.Nombre, ' ', p.Apellido) as nombre_cliente,
                p.Correo,
                p.Telefono,
                c.NIT,
                c.Direccion AS cliente_direccion 
            FROM Persona p
            INNER JOIN Cliente c ON p.num_identificacion = c.Persona_num_identificacion
                       AND p.tipoDocumento_tipo_Doc = c.Persona_tipoDocumento_tipo_Doc   
            ORDER BY p.Nombre, p.Apellido
        """)
        return cursor.fetchall()


def buscar_cliente_por_identificacion(connection, num_identificacion, tipo_documento):
    with connection.cursor() as cursor: 
        cursor.execute("""
            SELECT
                p.num_identificacion, p.tipoDocumento_tipo_Doc, p.Nombre, p.Apellido, CONCAT(p.Nombre, ' ', p.Apellido) as nombre_cliente, p.Correo, p.Telefono,
                c.NIT, c.Direccion AS cliente_direccion
            FROM Persona p
            JOIN Cliente c ON p.num_identificacion = c.Persona_num_identificacion
            WHERE p.num_identificacion = %s AND p.tipoDocumento_tipo_Doc = %s
        """, (num_identificacion, tipo_documento))
        return cursor.fetchone()
    
def buscar_cliente_por_nit(connection, nit):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.num_identificacion, p.tipoDocumento_tipo_Doc, p.Nombre, p.Apellido, CONCAT(p.Nombre, ' ', p.Apellido) as nombre_cliente, p.Correo, p.Telefono,
                c.NIT, c.Direccion AS cliente_direccion
            FROM Persona p
            JOIN Cliente c ON p.num_identificacion = c.Persona_num_identificacion
            WHERE c.NIT = %s
        """, (nit,))
        return cursor.fetchone()

def buscar_cliente_por_criterio(connection, criterio, valor, tipo_documento_busqueda=None): # Añadido tipo_documento_busqueda como parámetro
    with connection.cursor() as cursor: 
        query = """
            SELECT p.num_identificacion,
                   p.tipoDocumento_tipo_Doc,
                   p.Nombre,
                   p.Apellido,
                   CONCAT(p.Nombre, ' ', p.Apellido) as nombre_cliente,
                   p.Correo,
                   p.Telefono,
                   c.NIT,
                   c.Direccion AS cliente_direccion
            FROM Persona p
            INNER JOIN Cliente c ON p.num_identificacion = c.Persona_num_identificacion
                                AND p.tipoDocumento_tipo_Doc = c.Persona_tipoDocumento_tipo_Doc
            WHERE 1=1 
        """
        params = []

        if criterio == 'num_identificacion':
            query += " AND p.num_identificacion = %s"
            params.append(valor)
            if tipo_documento_busqueda: # Añadir esta condición si el tipo de documento es relevante para la búsqueda por ID
                query += " AND p.tipoDocumento_tipo_Doc = %s"
                params.append(tipo_documento_busqueda)
        elif criterio == 'nombre':
            query += " AND (p.Nombre LIKE %s OR p.Apellido LIKE %s)"
            params.extend([f'%{valor}%', f'%{valor}%'])
        elif criterio == 'email':
            query += " AND p.Correo LIKE %s"
            params.append(f'%{valor}%')
        elif criterio == 'nit':
            query += " AND c.NIT LIKE %s"
            params.append(f'%{valor}%')
        
        # Añadir un ORDER BY opcional para resultados consistentes
        query += " ORDER BY p.Nombre, p.Apellido"

        cursor.execute(query, tuple(params))
        return cursor.fetchone()

def persona_existente(connection, num_identificacion, tipo_documento):
    with connection.cursor() as cursor:
        cursor.execute("SELECT num_identificacion FROM Persona WHERE num_identificacion = %s AND tipoDocumento_tipo_Doc = %s", (num_identificacion, tipo_documento))
        return cursor.fetchone()

def cliente_existente(connection, nit):
    with connection.cursor() as cursor:
        cursor.execute("SELECT NIT FROM Cliente WHERE NIT = %s", (nit,))
        return cursor.fetchone()

def correo_existente(connection, correo, exclude_num_identificacion=None, exclude_tipo_documento=None):
    with connection.cursor() as cursor:
        if exclude_num_identificacion and exclude_tipo_documento:
            cursor.execute("SELECT num_identificacion FROM Persona WHERE Correo = %s AND NOT (num_identificacion = %s AND tipoDocumento_tipo_Doc = %s)",
                           (correo, exclude_num_identificacion, exclude_tipo_documento))
        else:
            cursor.execute("SELECT Correo FROM Persona WHERE Correo = %s", (correo,))
        return cursor.fetchone()

def registrar_persona(connection, datos):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Persona (num_identificacion, Nombre, Apellido, Correo, Telefono, tipoDocumento_tipo_Doc)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, datos)

def registrar_cliente(connection, datos):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Cliente (NIT, Direccion, Persona_num_identificacion, Persona_tipoDocumento_tipo_Doc)
            VALUES (%s, %s, %s, %s)
        """, datos)
    
def actualizar_persona_db(connection, datos_persona):
    with connection.cursor() as cursor:
        query = """
            UPDATE Persona
            SET num_identificacion = %s, Nombre = %s, Apellido = %s, Correo = %s, Telefono = %s, tipoDocumento_tipo_Doc = %s
            WHERE num_identificacion = %s AND tipoDocumento_tipo_Doc = %s
        """
        cursor.execute(query, datos_persona)
        return cursor.rowcount

def actualizar_cliente_db(connection, datos_cliente):
    with connection.cursor() as cursor:
        query = """
            UPDATE Cliente
            SET NIT = %s, Direccion = %s, Persona_num_identificacion = %s, Persona_tipoDocumento_tipo_Doc = %s
            WHERE Persona_num_identificacion = %s AND Persona_tipoDocumento_tipo_Doc = %s AND NIT = %s
        """
        cursor.execute(query, datos_cliente)
        return cursor.rowcount


def eliminar_cliente_db(connection, num_identificacion, tipo_documento):
    """Elimina un cliente de la tabla Cliente y devuelve el número de filas afectadas."""
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM Cliente
            WHERE Persona_num_identificacion = %s AND Persona_tipoDocumento_tipo_Doc = %s
        """, (num_identificacion, tipo_documento))
        return cursor.rowcount # Devuelve el número de filas que fueron eliminadas

def eliminar_persona_db(connection, num_identificacion, tipo_documento):
    """Elimina una persona de la tabla Persona y devuelve el número de filas afectadas."""
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM Persona
            WHERE num_identificacion = %s AND tipoDocumento_tipo_Doc = %s
        """, (num_identificacion, tipo_documento))
        return cursor.rowcount

def cliente_existente_por_persona_id(connection, num_identificacion, tipo_documento):
    with connection.cursor() as cursor:
        query = """
            SELECT COUNT(*) FROM Cliente
            WHERE Persona_num_identificacion = %s AND Persona_tipoDocumento_tipo_Doc = %s
        """
        cursor.execute(query, (num_identificacion, tipo_documento))
        return cursor.fetchone()[0] > 0

def cargar_datos_edicion(connection, num_identificacion, tipo_documento):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.num_identificacion,
                   p.tipoDocumento_tipo_Doc,
                   p.Nombre,
                   p.Apellido,
                   p.Correo,
                   p.Telefono,
                   c.NIT,
                   c.Direccion AS cliente_direccion
            FROM Persona p
            INNER JOIN Cliente c ON p.num_identificacion = c.Persona_num_identificacion
                              AND p.tipoDocumento_tipo_Doc = c.Persona_tipoDocumento_tipo_Doc
            WHERE p.num_identificacion = %s AND p.tipoDocumento_tipo_Doc = %s
        """, (num_identificacion, tipo_documento))
        return cursor.fetchone()