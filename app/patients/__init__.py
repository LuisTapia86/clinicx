from flask import Blueprint

patients_bp = Blueprint('patients', __name__)

from app.patients import routes
