from library.engine.baseapp import BaseApp


class App(BaseApp):

    def configure_routes(self):
        self.logger.info("Configuring conductor endpoints")

        self.logger.debug("main_ctrl at /")
        from app.controllers.main import main_ctrl
        self.flask.register_blueprint(main_ctrl, url_prefix="/")

        self.logger.debug("doc_ctrl at /api")
        from app.controllers.api.doc import doc_ctrl
        self.flask.register_blueprint(doc_ctrl, url_prefix="/api")

        self.logger.debug("projects_ctrl at /api/v1/projects")
        from app.controllers.api.v1.projects import projects_ctrl
        self.flask.register_blueprint(projects_ctrl, url_prefix="/api/v1/projects")

        self.logger.debug("account_ctrl at /api/v1/account")
        from app.controllers.api.v1.account import account_ctrl
        self.flask.register_blueprint(account_ctrl, url_prefix="/api/v1/account")

        self.logger.debug("datacenters_ctrl at /api/v1/datacenters")
        from app.controllers.api.v1.datacenters import datacenters_ctrl
        self.flask.register_blueprint(datacenters_ctrl, url_prefix="/api/v1/datacenters")

        self.logger.debug("groups_ctrl at /api/v1/groups")
        from app.controllers.api.v1.groups import groups_ctrl
        self.flask.register_blueprint(groups_ctrl, url_prefix="/api/v1/groups")

        self.logger.debug("hosts_ctrl at /api/v1/hosts")
        from app.controllers.api.v1.hosts import hosts_ctrl
        self.flask.register_blueprint(hosts_ctrl, url_prefix="/api/v1/hosts")

        self.logger.debug("users_ctrl at /api/v1/users")
        from app.controllers.api.v1.users import users_ctrl
        self.flask.register_blueprint(users_ctrl, url_prefix="/api/v1/users")

        self.logger.debug("actions_ctrl at /api/v1/actions")
        from app.controllers.api.v1.actions import actions_ctrl
        self.flask.register_blueprint(actions_ctrl, url_prefix="/api/v1/actions")

        self.logger.debug("open_ctrl at /api/v1/open")
        from app.controllers.api.v1.open import open_ctrl
        self.flask.register_blueprint(open_ctrl, url_prefix="/api/v1/open")

    def after_configured(self):
        self.action_logging = self.config.app.get("ACTION_LOGGING", False)


app = App()
