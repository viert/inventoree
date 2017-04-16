import React, { Component } from 'react'
import { Route } from 'react-router-dom'
import './Structure.css'

import AppSidebar from './AppSidebar'
import ProjectList from './Projects/ProjectList'
import ProjectEditor from './Projects/ProjectEditor'
import DatacenterList from './Datacenters/DatacenterList'
import { AlertBox } from '../library/AlertBox'

class Structure extends Component {
    render() {
        return ( 
            <div className="main">
                <AppSidebar />
                <div className="content">
                    <AlertBox />
                    <Route exact path="/projects" component={ProjectList} />
                    <Route path="/projects/:id" component={ProjectEditor} />
                    <Route path="/datacenters" component={DatacenterList} />
                </div>
            </div>
        )
    }
}

export default Structure;