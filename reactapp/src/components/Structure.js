import React, { Component } from 'react';
import { NavLink, Route } from 'react-router-dom';
import './Structure.css';

import ProjectList from './Projects/ProjectList';
import DatacenterList from './Datacenters/DatacenterList';

class Structure extends Component {
    render() {
        return ( 
            <div className="main">
                <aside className="sidebar">
                    <ul className="sidebar-menu">
                        <li><NavLink to="/structure/datacenters" activeClassName="active">datacenters</NavLink></li>
                        <li><NavLink to="/structure/projects" activeClassName="active">projects</NavLink></li>
                        <li><NavLink to="/structure/groups" activeClassName="active">groups</NavLink></li>
                        <li><NavLink to="/structure/hosts" activeClassName="active">hosts</NavLink></li>
                        <hr/>
                        <li><NavLink to="/structure/users" activeClassName="active">users</NavLink></li>
                    </ul>
                </aside>
                <div className="content">
                    <Route path="/structure/projects" component={ProjectList} />
                    <Route path="/structure/datacenters" component={DatacenterList} />
                </div>
            </div>
        )
    }
}

export default Structure;