# app/modelos/modelo_empleados.py
def obtener_usuarios(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.num_identificacion as id_usuario, 
                   CONCAT(p.Nombre, ' ', p.Apellido) as nombre_usuario,
                   p.Correo as email,
                   p.Telefono as telefono,
                   p.tipoDocumento_tipo_Doc as tipo_documento,
                   u.Rol as rol,
                   u.Estado as estado,
                   NOW() as fecha_registro
            FROM Persona p
            INNER JOIN Usuario u ON p.num_identificacion = u.Persona_num_identificacion
            ORDER BY p.Nombre, p.Apellido
        """)
        return cursor.fetchall()


def buscar_empleado_por_id(connection, id_usuario):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.num_identificacion as id_usuario, 
                   p.Nombre as nombre,
                   p.Apellido as apellido,
                   CONCAT(p.Nombre, ' ', p.Apellido) as nombre_completo,
                   p.Correo as email,
                   p.Telefono as telefono,
                   p.tipoDocumento_tipo_Doc as tipo_documento,
                   u.Rol as rol,
                   u.Estado as estado,
                   NOW() as fecha_registro
            FROM Persona p
            INNER JOIN Usuario u ON p.num_identificacion = u.Persona_num_identificacion
            WHERE p.num_identificacion = %s
        """, (id_usuario,))
        return cursor.fetchone()


def buscar_empleado_por_criterio(connection, criterio, valor):
    with connection.cursor() as cursor:
        if criterio == 'id':
            cursor.execute("""
                SELECT p.num_identificacion as id_usuario, 
                       p.Nombre as nombre,
                       p.Apellido as apellido,
                       CONCAT(p.Nombre, ' ', p.Apellido) as nombre_completo,
                       p.Correo as email,
                       p.Telefono as telefono,
                       p.tipoDocumento_tipo_Doc as tipo_documento,
                       u.Rol as rol,
                       u.Estado as estado,
                       NOW() as fecha_registro
                FROM Persona p
                INNER JOIN Usuario u ON p.num_identificacion = u.Persona_num_identificacion
                WHERE p.num_identificacion = %s
            """, (valor,))
        elif criterio == 'nombre':
            cursor.execute("""
                SELECT p.num_identificacion as id_usuario, 
                       p.Nombre as nombre,
                       p.Apellido as apellido,
                       CONCAT(p.Nombre, ' ', p.Apellido) as nombre_completo,
                       p.Correo as email,
                       p.Telefono as telefono,
                       p.tipoDocumento_tipo_Doc as tipo_documento,
                       u.Rol as rol,
                       u.Estado as estado,
                       NOW() as fecha_registro
                FROM Persona p
                INNER JOIN Usuario u ON p.num_identificacion = u.Persona_num_identificacion
                WHERE p.Nombre LIKE %s OR p.Apellido LIKE %s OR CONCAT(p.Nombre, ' ', p.Apellido) LIKE %s
            """, (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
        elif criterio == 'email':
            cursor.execute("""
                SELECT p.num_identificacion as id_usuario, 
                       p.Nombre as nombre,
                       p.Apellido as apellido,
                       CONCAT(p.Nombre, ' ', p.Apellido) as nombre_completo,
                       p.Correo as email,
                       p.Telefono as telefono,
                       p.tipoDocumento_tipo_Doc as tipo_documento,
                       u.Rol as rol,
                       u.Estado as estado,
                       NOW() as fecha_registro
                FROM Persona p
                INNER JOIN Usuario u ON p.num_identificacion = u.Persona_num_identificacion
                WHERE p.Correo LIKE %s
            """, (f'%{valor}%',))
        return cursor.fetchone()


def persona_existente(connection, id_usuario):
    with connection.cursor() as cursor:
        cursor.execute("SELECT num_identificacion FROM Persona WHERE num_identificacion = %s", (id_usuario,))
        return cursor.fetchone()


def correo_existente(connection, correo, exclude_id=None):
    with connection.cursor() as cursor:
        if exclude_id:
            cursor.execute("SELECT num_identificacion FROM Persona WHERE Correo = %s AND num_identificacion != %s", (correo, exclude_id))
        else:
            cursor.execute("SELECT Correo FROM Persona WHERE Correo = %s", (correo,))
        return cursor.fetchone()


def registrar_persona(connection, datos):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Persona (num_identificacion, Nombre, Apellido, Correo, Telefono, tipoDocumento_tipo_Doc)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, datos)


def registrar_usuario(connection, datos):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Usuario (Contraseña, Rol, Estado, Persona_num_identificacion, Persona_tipoDocumento_tipo_Doc)
            VALUES (%s, %s, %s, %s, %s)
        """, datos)


def actualizar_persona(connection, nombre, apellido, correo, id_usuario):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE Persona SET Nombre = %s, Apellido = %s, Correo = %s
            WHERE num_identificacion = %s
        """, (nombre, apellido, correo, id_usuario))


def actualizar_contraseña(connection, hashed_password, id_usuario):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE Usuario SET Contraseña = %s
            WHERE Persona_num_identificacion = %s
        """, (hashed_password, id_usuario))


def eliminar_usuario(connection, id_usuario):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM Usuario WHERE Persona_num_identificacion = %s", (id_usuario,))
        cursor.execute("DELETE FROM Persona WHERE num_identificacion = %s", (id_usuario,))


def cargar_datos_edicion(connection, id_usuario):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.num_identificacion as id_usuario, 
                   CONCAT(p.Nombre, ' ', p.Apellido) as nombre_usuario,
                   p.Correo as email,
                   NOW() as fecha_registro
            FROM Persona p
            INNER JOIN Usuario u ON p.num_identificacion = u.Persona_num_identificacion
            WHERE p.num_identificacion = %s
        """, (id_usuario,))
        return cursor.fetchone()