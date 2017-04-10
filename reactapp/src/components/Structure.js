import React, { Component } from 'react';
import { NavLink, Route } from 'react-router-dom';
import './Structure.css';

import ProjectList from './Projects/ProjectList';
import ProjectNew from './Projects/ProjectNew';
import DatacenterList from './Datacenters/DatacenterList';

class Structure extends Component {
    render() {
        return ( 
            <div className="main">
                <aside className="sidebar">
                    <ul className="sidebar-menu">
                        <li><NavLink to="/datacenters" activeClassName="active">datacenters</NavLink></li>
                        <li><NavLink to="/projects" activeClassName="active">projects</NavLink></li>
                        <li><NavLink to="/groups" activeClassName="active">groups</NavLink></li>
                        <li><NavLink to="/hosts" activeClassName="active">hosts</NavLink></li>
                        <hr/>
                        <li><NavLink to="/structure/users" activeClassName="active">users</NavLink></li>
                    </ul>
                </aside>
                <div className="content">
                    <Route exact path="/projects" component={ProjectList} />
                    <Route exact path="/projects/new" component={ProjectNew} />
                    <Route path="/datacenters" component={DatacenterList} />
                </div>
            </div>
        )
    }
}

export default Structure;