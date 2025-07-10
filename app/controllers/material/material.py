from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from app.models import modelo_materiales as modelo

material_bp = Blueprint('material', __name__, url_prefix='/material')

@material_bp.route('/')
def mostrar_material():
    return render_template('material/material.html')

@material_bp.route('/consultar_material', methods=['GET', 'POST'])
def consultar_material():
    connection = current_app.connection
    materiales = []
    materiales_encontrados = []
    mensaje = None
    tipo_busqueda = None

    try:
        materiales = modelo.obtener_materiales(connection)
    except Exception as e:
        flash('Error al cargar la lista de materiales para consulta.', 'error')
        current_app.logger.error(f"Error al cargar materiales: {str(e)}")

    if request.method == 'GET':
        id_material_url = request.args.get('id_material')
        tipo_material_url = request.args.get('tipo_material')

        if id_material_url:
            try:
                material = modelo.buscar_material_por_id(connection, id_material_url)
                if material:
                    materiales_encontrados = [material]
                    tipo_busqueda = 'id'
                    mensaje = 'Material encontrado exitosamente.'
                else:
                    mensaje = 'No se encontró el material especificado.'
            except Exception as e:
                mensaje = f'Error al buscar material: {str(e)}'
                current_app.logger.error(f"Error al buscar material por ID: {str(e)}")
                
        elif tipo_material_url:
            try:
                materiales_encontrados = modelo.buscar_material_por_tipo(connection, tipo_material_url)
                tipo_busqueda = 'tipo'
                if materiales_encontrados:
                    mensaje = f'Se encontraron {len(materiales_encontrados)} materiales.'
                else:
                    mensaje = 'No se encontraron materiales del tipo especificado.'
            except Exception as e:
                mensaje = f'Error al buscar por tipo: {str(e)}'
                current_app.logger.error(f"Error al buscar por tipo: {str(e)}")

    elif request.method == 'POST':
        search_action = request.form.get('search_action')
        id_material_seleccionado = request.form.get('id_material')
        tipo_material_seleccionado = request.form.get('tipo_material')

        try:
            if search_action == 'search_by_list' and id_material_seleccionado:
                material = modelo.buscar_material_por_id(connection, id_material_seleccionado)
                if material:
                    materiales_encontrados = [material]
                    tipo_busqueda = 'id'
                    mensaje = 'Material encontrado exitosamente.'
                else:
                    mensaje = 'No se encontró el material seleccionado.'
                    
            elif search_action == 'search_by_type' and tipo_material_seleccionado:
                materiales_encontrados = modelo.buscar_material_por_tipo(connection, tipo_material_seleccionado)
                tipo_busqueda = 'tipo'
                if materiales_encontrados:
                    mensaje = f'Se encontraron {len(materiales_encontrados)} materiales.'
                else:
                    mensaje = 'No se encontraron materiales del tipo especificado.'
            else:
                flash('Por favor, selecciona un material o ingresa un tipo de búsqueda.', 'info')
                
        except Exception as e:
            mensaje = f'Error al buscar material: {str(e)}'
            current_app.logger.error(f"Error en búsqueda: {str(e)}")

    return render_template('material/consultar_material.html',
                         materiales=materiales,
                         materiales_encontrados=materiales_encontrados,
                         mensaje=mensaje,
                         tipo_busqueda=tipo_busqueda)

@material_bp.route('/registrar_material', methods=['GET', 'POST'])
def registrar_material():
    if request.method == 'GET':
        return render_template('material/registrar_material.html')

    connection = current_app.connection
    
    try:
        # Obtener datos del formulario
        datos = {
            'nombre': request.form['nombre'],
            'tipo_material': request.form.get('tipo_material', ''),
            'cantidad': int(request.form['cantidad']),
            'unidad_medida': request.form['unidad_medida'],
            'proveedor': request.form.get('proveedor', ''),
            'fecha_entrada': request.form['fecha_entrada']
        }

        # Validar si el material existe
        if modelo.material_existente(connection, datos['nombre']):
            flash('Ya existe un material con ese nombre', 'error')
            return redirect(url_for('material.registrar_material'))

        # Registrar el material
        modelo.registrar_material(connection, datos)
        connection.commit()
        flash('Material registrado exitosamente', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        connection.rollback()
        flash(f'Error al registrar material: {str(e)}', 'error')
        current_app.logger.error(f"Error al registrar material: {str(e)}")

    return redirect(url_for('material.registrar_material'))