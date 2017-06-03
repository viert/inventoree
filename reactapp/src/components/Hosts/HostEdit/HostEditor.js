import React, { Component } from 'react'
import Axios from 'axios'
import HttpErrorHandler from '../../../library/HttpErrorHandler'
import AlertStore from '../../../library/AlertBox'
import Loading from '../../common/Loading'

import HostForm from './HostForm'

export default class HostEditor extends Component {
    constructor(props) {
        super(props)
        this.state = {
            title: "Add Host(s)",
            host: {
                fqdn: "",
                short_name: "",
                tags: [],
                group: {
                    name: ""
                },
                datacenter: {
                    name: ""
                }
            },
            isNew: true,
            isLoading: true
        }
    }

    componentDidMount() {
        let { id } = this.props.match.params
        if (id && id !== "new") {
            Axios.get(`/api/v1/hosts/${id}?_fields=fqdn,short_name,description,datacenter,group,datacenter_id,group_id,tags`)
                .then( this.onDataLoaded.bind(this) )
                .catch( error => {
                    HttpErrorHandler(error)
                    this.props.history.push('/hosts')
                })
        } else {
            this.setState({
                isLoading: false
            })
        }
    }

    onDataLoaded(response) {
        this.setState({
            host: response.data.data[0],
            title: "Edit Host",
            isNew: false,
            isLoading: false
        })
    }

    handleSubmit(host) {
        let { id } = this.props.match.params
        let { fqdn } = host
        let action = this.state.isNew ? Axios.post("/api/v1/hosts/", host) : Axios.put(`/api/v1/hosts/${id}`, host)
        let message = `Host ${fqdn} has been successfully ` + (this.state.isNew ? "created" : "updated")
        action.then( response => {
            AlertStore.Notice(message)
            this.props.history.push("/hosts")
        })
        .catch(HttpErrorHandler)
    }

    handleDestroy(host) {
        let { id } = this.props.match.params
        Axios.delete(`/api/v1/hosts/${id}`)
            .then( response => {
                let { fqdn } = host
                AlertStore.Notice(`Host ${fqdn} has been successfully destroyed`)
                this.props.history.push("/hosts")
            })
            .catch(HttpErrorHandler)
    }

    render() {
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>{this.state.title}</h2>
                    <div className="row">
                        <div className="col-sm-5">
                            <HostForm 
                                    host={this.state.host}
                                    isNew={this.state.isNew}
                                    onSubmit={this.handleSubmit.bind(this)}
                                    onDestroy={this.handleDestroy.bind(this)} />
                        </div>
                        <div className="col-sm-7">
                            Placeholder for fqdn pattern expander
                        </div>
                    </div>
                </div>
            }            
            </div>
        )
    }
}