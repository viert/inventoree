# Conductor

Conductor leads you through the chaos of your infrastructure

**Disclaimer:** conductor is nothing more than a servers inventory. Originally such a project was created at Yandex to help system engineers to store and to classify their servers joining them into groups which are joined into projects. Conductor is able to watch your data structure consistency and check users' permissions to modify it. With a fast and well structured REST API it can be used by various CMS systems like Saltstack, Chef, Puppet and Ansible as an extra filter for running states and commands. With built-in conductor **tags** one can store roles of groups or individual servers which is convenient for use as an extra data for state formulas.

Original version of conductor has an ability to track deployment and packages movement among repositories which won't be represented in this opensource version.

**Important:** this version is not based on the original one but created from scratch using absolutely separate technologies.

## Roadmap

### Python API

 * ~~Datacenter model and unittests~~
 * ~~Project model and unittests~~
 * ~~Group model and unittests~~
 * ~~Host model and unittests~~
 * ~~User model and unittests~~
