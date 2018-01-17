user_create_schema = {
    "type": "object",
    "properties": {
        "firstname": {
            "type": "string",
            "minLength": 1
        },
        "lastname": {
            "type": "string",
            "minLength": 1
        },
        "username": {
            "type": "string",
            "minLength": 1
        },
        "address": {
            "type": "string",
        },
        "phone_no": {
            "type": "string",
        },
        "role_id": {
            "type": "number"
        }
    },
    "required": ["firstname", "lastname", "username"]
}

# This variable contains the info of each role's creatable user role array
role_match_creatable = [
    [2, 3, 5, 7], #SuperUpser can create Researcher, Restricted, Clinic SuperUser, Patient
    [],
    [],
    [],
    [5, 6, 7], #Clinic Superuser can create Clinic SuperUser, Clinician, Patient
    [7], #Clinician can create Patient
    []
]
#
# role_match_viewable = [
#     []
# ]