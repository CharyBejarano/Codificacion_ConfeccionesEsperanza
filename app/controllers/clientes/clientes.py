from flask import Blueprint, render_template

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/')
def mostrar_clientes():
    return render_template('clientes/clientes.html')