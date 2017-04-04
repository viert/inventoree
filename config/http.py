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
    }
]