from flask import Blueprint, render_template, redirect, url_for, request

from flask import session

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def Home():
  if session and session['email']:
    return render_template('home/index.html')
  return redirect(url_for('usuarios_bp.iniciarSesion'))