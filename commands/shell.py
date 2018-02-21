from commands import Command


class Shell(Command):

    DESCRIPTION = 'Run shell (using IPython if available)'

    def run(self):
        from app.models import *
        try:
            # trying IPython if installed...
            from IPython import embed
            embed()
        except ImportError:
            # ... or python default console if not
            try:
                # optional readline interface for history if installed
                import readline
            except ImportError:
                pass
            import code
            variables = globals().copy()
            variables.update(locals())
            shell = code.InteractiveConsole(variables)
            shell.interact()