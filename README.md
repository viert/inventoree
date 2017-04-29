# Conductor

Conductor leads you through the chaos of your infrastructure

**Disclaimer:** conductor is nothing more than a servers inventory. Originally such a project was created at Yandex to help system engineers to store and to classify their servers joining them into groups which are joined into projects. Conductor is able to watch your data structure consistency and check users' permissions to modify it. With a fast and well structured REST API it can be used by various CMS systems like Saltstack, Chef, Puppet and Ansible as an extra filter for running states and commands. With built-in conductor **tags** one can store roles of groups or individual servers which is convenient for use as an extra data for state formulas.

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

*Strikedthrough ones are ready to use*

### Python API

 * ~~Datacenter model and unittests~~
 * ~~Project model and unittests~~
 * ~~Group model and unittests~~
 * ~~Host model and unittests~~
 * ~~User model and unittests~~
 * ~~Importing test data~~
 * Benchmarks
 
### HTTP API
 * ~~User Sessions and Authentication~~ (TODO: move from pbkdf2 to bcrypt)
 * /api/v1/datacenters (~~list~~, ~~show~~, ~~create~~, ~~update~~, ~~delete~~)
 * /api/v1/groups (~~list~~, ~~show~~, create, update, delete)
 * /api/v1/hosts (list, show, create, update, delete)
 * /api/v1/projects (~~list~~, ~~show~~, ~~create~~, ~~update~~, ~~delete~~)
 * suggestions/filters should be switched to golang-based https://github.com/viert/simplesuggest for better performance
 * readonly non-auth cached helpers like *groups2hosts*, *projects2groups* to use in CMSes and command line tools
 
### HTTP Frontend
 
 React.js-based frontend can be considered as very amateur being my first one after years of developing of Angular.js apps. Any help would be highly valuable. As well as any help on python part
