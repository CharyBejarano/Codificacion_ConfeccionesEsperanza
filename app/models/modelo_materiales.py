
#modelo_materiales.py
def registrar_material(connection, datos_material):
    """Registra un nuevo material en la base de datos"""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Material 
            (Nombre, tipo_material, cantidad, Unidad_medida, proveedor, Fecha_entrada)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datos_material['nombre'],
            datos_material['tipo_material'],
            datos_material['cantidad'],
            datos_material['unidad_medida'],
            datos_material['proveedor'],
            datos_material['fecha_entrada']
        ))
        return cursor.lastrowid

def obtener_materiales(connection):
    """Obtiene todos los materiales de la base de datos"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id_material,
                Nombre,
                tipo_material,
                cantidad,
                Unidad_medida,
                proveedor,
                Fecha_entrada
            FROM Material
            ORDER BY Nombre
        """)
        return cursor.fetchall()

def buscar_material_por_id(connection, material_id):
    """Busca un material por su ID"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id_material,
                Nombre,
                tipo_material,
                cantidad,
                Unidad_medida,
                proveedor,
                Fecha_entrada
            FROM Material
            WHERE id_material = %s
        """, (material_id,))
        return cursor.fetchone()

def buscar_material_por_tipo(connection, tipo_material):
    """Busca materiales por tipo"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id_material,
                Nombre,
                tipo_material,
                cantidad,
                Unidad_medida,
                proveedor,
                Fecha_entrada
            FROM Material
            WHERE tipo_material = %s
            ORDER BY Nombre
        """, (tipo_material,))
        return cursor.fetchall()

def material_existente(connection, nombre_material):
    """Verifica si un material ya existe por su nombre"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_material FROM Material WHERE Nombre = %s", (nombre_material,))
        return cursor.fetchone() is not None


