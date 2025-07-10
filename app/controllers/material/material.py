from flask import Blueprint, render_template

material_bp = Blueprint('material', __name__, url_prefix='/material')

@material_bp.route('/')
def mostrar_material():
    return render_template('material/material.html')