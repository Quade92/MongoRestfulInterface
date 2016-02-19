import resources
from app import api

api.add_resource(resources.LatestRecord, "/latest-record")
api.add_resource(resources.LatestRecordSet, "/latest-record-set/<int:amount>")
api.add_resource(resources.Record, "/record")
api.add_resource(resources.RecordSeries, "/record-series/<int:start>/<int:end>")
api.add_resource(resources.Authenticate, "/authenticate")