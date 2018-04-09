# Inventoree

Inventoree leads you through the chaos of your infrastructure

**Disclaimer:** inventoree (previously known as conductor) is nothing more than a servers inventory. Originally such a project was created at Yandex to help system engineers to store and classify their servers combining them into groups which are combined into projects. Inventoree is able to watch for your data structure consistency and check users' permissions to modify it. With a fast and well structured REST API it can be used by various CMS systems like Saltstack, Chef, Puppet and Ansible as an extra filter for running states and commands. With built-in inventoree **tags** and **custom fields** one can store roles of groups or individual servers which is convenient for use as an extra data for state formulas.

Original version of conductor has an ability to track deployment and packages movement among repositories which won't be implemented in Inventoree.

**Important:** this version is not based on the original one but created from scratch using absolutely separate technologies.

## Development bootstrap

Being in deep development and moving from one laptop to another, from MacOSX to Windows and Linux, the current inventoree version has become very easy to set up. 

 * Clone repo and `cd` into its' directory. 
 * Run `pip install -r requirements.txt` to install the python requirements. Using virtualenv is highly recommended
 * This version requires mongodb 2.6+ server to be installed on localhost with inventoree itself. You can change this behaviour in `config/db.py` file. Although it's tracked by git and no mechanism has been created for custom configuration yet. So just put mongodb right alongside your inventoree installation, it's just the most appropriate solution at the moment.
 * Run `./micro.py index` to create indexes. Be sure your mongodb server is up and running.
 * Run `./micro.py shell` to start project shell. If you have IPython installed in your virtualenv, it will be used automatically.
 * Create a supervisor user like described below:
```
from app.models import User
user = User(username="<your_nickname>", password_raw="<your_password_in_plaintext>", supervisor=True)
user.save()
```
 * Exit the shell using `Ctrl-D` and run `./micro.py run` to start python development server. By default it binds on port 5000, you can check it with a browser or something like curl using url `http://localhost:5000/api/v1/account/me` - it will give you Unauthorized error.
 * `cd` to `reactapp` and run `npm install` to install React.js and all the react application dependencies. You must have node.js 6+ installed
 * Run `npm start` to build react application, don't be scared when it starts your browser automatically.
 * Log in using your supervisor username and password

## Experimental Web UI

Inventoree has a new nice looking redesigned web ui written using vue.js. To replace the original one follow the steps:
 * Update `webui` submodule using `git submodule init; git submodule update`. This will pull the new ui sources from [inventoree-ui](https://github.com/viert/inventoree-ui) repository into `webui` directory
 * Instead of "cd-ing into `reactapp`" step `cd` into `webui` and run `npm install` to install Vue.js and all its dependencies. You must have node.js 6+ installed.
 * Run `npm run dev` to build the application and serve it using built-in nodejs http server. To create optimized production-ready static files use `npm run build` instead. 

## Note on external authentication

Example authorizer (via vk.com) is located in `plugins` folder. The only thing is mandatory in authorizer is the `get_authentication_url` method. If this method returns an actual url like
`https://oauth.vk.com/authorize?client_id=...` the button *EXTERNAL AUTH* appears on Login page automatically (and leads to that url). In case of example vk authorizer there's a *NAME* class property assigned which makes button text change to *VK LOGIN*. 

The second thing you have to do is create a special handler in flask (that's why authorizers get flask app in constructor) which is supposed to handle callbacks from external auth services (All modern authentication systems like OAuth, SAML SSO and OpenID act like this). This handler is aimed to find an actual local user related to external user data you receive. If user doesn't exist, your task is to create it first and connect to the external data (`ext_id` field in `User` model serves for this purpose and is indexed by default). Next time user logins your handler should find it by `ext_id`.

The last task you have to do in callback handler is put the local `_id` field of found user instance to session["user_id"] - that's how Inventoree gets user authenticated.

Don't forget to set `AUTHORIZER="<YourAuthorizer>"` in app config to actually set up your authorizer. All plugins in `plugins` directory are loaded automatically but no
authorizer is set until configured explicitly.

## Roadmap

### v6.9

  * Action Logging UI
  * Tag search
  * Host Aliases

### v6.10
  * Applications Registry
