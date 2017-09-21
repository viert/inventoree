# Conductor

Conductor leads you through the chaos of your infrastructure

**Disclaimer:** conductor is nothing more than a servers inventory. Originally such a project was created at Yandex to help system engineers to store and classify their servers combining them into groups which are combined into projects. Conductor is able to watch for your data structure consistency and check users' permissions to modify it. With a fast and well structured REST API it can be used by various CMS systems like Saltstack, Chef, Puppet and Ansible as an extra filter for running states and commands. With built-in conductor **tags** and **custom fields** one can store roles of groups or individual servers which is convenient for use as an extra data for state formulas.

Original version of conductor has an ability to track deployment and packages movement among repositories which won't be represented in this opensource version.

**Important:** this version is not based on the original one but created from scratch using absolutely separate technologies.

## Development bootstrap

Being in deep development and moving from one notebook to another, from MacOSX to Windows and Linux, the current conductor version has become very easy to set up. 

 * Clone repo and `cd` into its' directory. 
 * Run `pip install -r requirements.txt` to install the python requirements. Using virtualenv is highly recommended
 * This version requires mongodb 2.6+ server to be installed on localhost with conductor itself. You can change this behaviour in `config/db.py` file. Although it's tracked by git and no mechanism has been created for custom configuration yet. So just put mongodb right alongside your conductor installation, it's just the most appropriate solution at the moment.
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
 
## Roadmap

### v6.6

  * Mass actions for hosts and groups
  * Visual and UX improvements
  
### v6.7 
 
  * Plugin system for Authentication and additional controllers
  * Huge code refactoring
