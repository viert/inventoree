from commands import Command

class Run(Command):
    def run(self):
        from app import app
        app.run(debug=True)