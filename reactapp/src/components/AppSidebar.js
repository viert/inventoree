import React from 'react'
import { NavLink } from 'react-router-dom'
import './AppSidebar.css'

const AppSidebar = () => (
    <aside className="sidebar">
        <ul className="sidebar-menu">
            <li><NavLink to="/datacenters" activeClassName="active">locations</NavLink></li>
            <li><NavLink to="/projects" activeClassName="active">projects</NavLink></li>
            <li><NavLink to="/groups" activeClassName="active">groups</NavLink></li>
            <li><NavLink to="/hosts" activeClassName="active">hosts</NavLink></li>
            <hr/>
            <li><NavLink to="/structure/users" activeClassName="active">users</NavLink></li>
        </ul>
    </aside>
)

export default AppSidebar