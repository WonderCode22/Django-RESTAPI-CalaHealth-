from cala_health.clinic.views import *
from cala_health import api

api.add_resource(
    UserApi,
    '/api/v1/users',
    '/api/v1/users/<int:id>'
)

api.add_resource(
    ClinicApi,
    '/api/v1/clinic',
    '/api/v1/clinic/<int:clinic_id>'
)
