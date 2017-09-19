import React, { Component } from 'react'
import Axios from 'axios'
import { observer } from 'mobx-react'
import { Link } from 'react-router-dom'
import AuthState from '../library/AuthState'
import AppInfo from '../library/AppInfo'
import './AppHeader.css'

// brand should be printed as image using Days One font 25px size

const AppHeader = observer(class AppHeader extends Component {

    componentDidMount() {
        Axios.get("/api/v1/open/app")
        .then(response => {
            AppInfo.setData(response.data)
        })
    }

    getUser() {
        var user = AuthState.getCurrentUser()
        if (user === null) {
            return {}
        } else {
            return user;
        }
    }

    render() {
        return (
            <div className="appheader">
                <div className="appheader-logo">
                    <Link to="/">Conductor</Link>
                    <small className="appheader-info">
                        v{AppInfo.getVersion()} (flask/{AppInfo.getFlaskVersion()}, 
                        mongodb/{AppInfo.getMongoVersion()})
                    </small>
                </div>
                <div className="appheader-account">
                    Logged in as {this.getUser().username}
                </div>
            </div>
        )
    }
})

export default AppHeader;
