# modelo_usuarios.py
def obtener_usuario_por_email(connection, email):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.Contraseña, u.Persona_num_identificacion, p.Nombre, p.Apellido 
            FROM Usuario u 
            INNER JOIN Persona p ON u.Persona_num_identificacion = p.num_identificacion 
            WHERE p.Correo = %s
        """, (email,))
        return cursor.fetchone()


def verificar_persona_existente(connection, num_identificacion):
    with connection.cursor() as cursor:
        cursor.execute("SELECT num_identificacion FROM Persona WHERE num_identificacion = %s", (num_identificacion,))
        return cursor.fetchone()


def verificar_correo_existente(connection, correo):
    with connection.cursor() as cursor:
        cursor.execute("SELECT Correo FROM Persona WHERE Correo = %s", (correo,))
        return cursor.fetchone()


def insertar_persona(connection, num_identificacion, nombre, apellido, correo, telefono, tipo_documento):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Persona (num_identificacion, Nombre, Apellido, Correo, Telefono, tipoDocumento_tipo_Doc) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (num_identificacion, nombre, apellido, correo, telefono, tipo_documento))


def insertar_usuario(connection, hashed_password, num_identificacion, tipo_documento):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Usuario (Contraseña, Rol, Estado, Persona_num_identificacion, Persona_tipoDocumento_tipo_Doc) 
            VALUES (%s, %s, %s, %s, %s)
        """, (hashed_password, 'USER', 'ACTIVO', num_identificacion, tipo_documento))


def obtener_datos_usuario(connection, user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.num_identificacion, p.Nombre, p.Apellido, p.Correo, p.Telefono, 
                   td.tipo_Doc, u.Rol, u.Estado
            FROM Persona p
            INNER JOIN Usuario u ON p.num_identificacion = u.Usuario_Persona_num_identificacion
            INNER JOIN tipoDocumento td ON p.Persona_tipoDocumento_tipo_Doc = td.tipo_Doc
            WHERE p.num_identificacion = %s
        """, (user_id,))
        return cursor.fetchone()
