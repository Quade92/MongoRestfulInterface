from models import LastRecord
from app import api

api.add_resource(LastRecord, '/')
