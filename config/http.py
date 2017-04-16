PORT = 3000
STATIC_FOLDER = "static"
ROUTES = [
    {
        "prefix": "/",
        "controller": "main"
    },
    {
        "prefix": "/api/v1/projects",
        "controller": "api.v1.projects"
    },
    {
        "prefix": "/api/v1/account",
        "controller": "api.v1.account"
    },
    {
        "prefix": "/api/v1/groups",
        "controller": "api.v1.groups"
    }
]