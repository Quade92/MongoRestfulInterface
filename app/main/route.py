import resources
import factory


def init_route():
    factory.api.add_resource(resources.LatestRecord, "/latest-record")
    factory.api.add_resource(resources.LatestRecordSet, "/latest-record-set/<int:amount>")
    factory.api.add_resource(resources.Record, "/record")
    factory.api.add_resource(resources.RecordSeries, "/record-series/<int:start>/<int:end>")
    factory.api.add_resource(resources.AuthenticateByPassword, "/authenticate")
    factory.api.add_resource(resources.Register, "/register")
    return 0