# Conductor

Conductor leads you through the chaos of your infrastructure

**Disclaimer:** conductor is nothing more than a servers inventory. Originally such a project was created at Yandex to help system engineers to store and to classify their servers joining them into groups which are joined into projects. Conductor is able to watch your data structure consistency and check users' permissions to modify it. With a fast and well structured REST API it can be used by various CMS systems like Saltstack, Chef, Puppet and Ansible as an extra filter for running states and commands. With built-in conductor **tags** one can store roles of groups or individual servers which is convenient for use as an extra data for state formulas.

Original version of conductor has an ability to track deployment and packages movement among repositories which won't be represented in this opensource version.

**Important:** this version is not based on the original one but created from scratch using absolutely separate technologies.

## Development bootstrap

Being in deep development and moving from one notebook to another, from MacOSX to Windows and Linux, the current conductor version has become very easy to set up. 

 * Clone repo and `cd` into its' directory. 
 * Run `pip install -r requirements.txt`  

sd
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
 * /api/v1/datacenters (~~list~~, ~~show~~, create, update, delete)
 * /api/v1/groups (~~list~~, ~~show~~, create, update, delete)
 * /api/v1/hosts (list, show, create, update, delete)
 * /api/v1/projects (~~list~~, ~~show~~, ~~create~~, ~~update~~, ~~delete~~)
 * suggestions/filters should be switched to golang-based https://github.com/viert/simplesuggest for better performance
 * readonly non-auth cached helpers like *groups2hosts*, *projects2groups* to use in CMSes and command line tools
 
### HTTP Frontend
 
 React.js-based frontend can be considered as very amateur being my first one after years of developing of Angular.js apps. Any help would be highly valuable. As well as any help on python part
