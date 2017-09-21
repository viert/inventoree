import React, { Component } from 'react'
import { Route } from 'react-router-dom'
import './Main.css'

import AppSidebar from './AppSidebar'

import ProjectList from './Projects/ProjectList'
import ProjectView from './Projects/ProjectView'
import ProjectEditor from './Projects/ProjectEditor'

import GroupList from './Groups/GroupList'
import GroupView from './Groups/GroupView'
import GroupEditor from './Groups/GroupEdit/GroupEditor'

import DatacenterList from './Datacenters/DatacenterList'
import DatacenterView from './Datacenters/DatacenterView'
import DatacenterEditor from './Datacenters/DatacenterEditor'

import HostList from './Hosts/HostList'
import HostView from './Hosts/HostView'
import HostEditor from './Hosts/HostEdit/HostEditor'

import UserList from './Users/UserList'
import UserView from './Users/UserView'
import UserEditor from './Users/UserEdit/UserEditor'

import { AlertBox } from '../library/AlertBox'

class Main extends Component {
    render() {
        return (
            <div className="main">
                <AppSidebar />
                <div className="content">
                    <AlertBox />
                    <Route exact path="/projects" component={ProjectList} />
                    <Route exact path="/projects/:id" component={ProjectView} />
                    <Route exact path="/projects/:id/edit" component={ProjectEditor} />
                    
                    <Route exact path="/groups" component={GroupList} />
                    <Route exact path="/groups/:id" component={GroupView} />
                    <Route exact path="/groups/:id/edit" component={GroupEditor} />

                    <Route exact path="/datacenters" component={DatacenterList} />
                    <Route exact path="/datacenters/:id" component={DatacenterView} />
                    <Route exact path="/datacenters/:id/edit" component={DatacenterEditor} />
                    
                    <Route exact path="/hosts" component={HostList} />
                    <Route exact path="/hosts/:id" component={HostView} />
                    <Route exact path="/hosts/:id/edit" component={HostEditor} />

                    <Route exact path="/users" component={UserList} />
                    <Route exact path="/users/:id" component={UserView} />
                    <Route exact path="/users/:id/edit" component={UserEditor} />
                </div>
            </div>
        )
    }
}

export default Main;