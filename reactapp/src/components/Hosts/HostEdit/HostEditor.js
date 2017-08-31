import React, { Component } from 'react'
import Axios from 'axios'
import HttpErrorHandler from '../../../library/HttpErrorHandler'
import AlertStore from '../../../library/AlertBox'
import Loading from '../../common/Loading'

import HostForm from './HostForm'
import MultipleHosts from './MultipleHosts'

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
            isLoading: true,
            pattern: null
        }
    }

    componentDidMount() {
        let { id } = this.props.match.params
        if (id && id !== "new") {
            Axios.get(`/api/v1/hosts/${id}?_fields=fqdn,short_name,description,datacenter,group,datacenter_id,group_id,tags,custom_fields`)
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
        let host = response.data.data[0]
        if (!host.group) { host.group = { name: "" } }
        if (!host.datacenter) { host.datacenter = { name: "" }}
        this.setState({
            host,
            title: "Edit Host",
            isNew: false,
            isLoading: false
        })
    }

    handleSubmit(host) {
        if (this.state.pattern !== null) {
            host.fqdn_pattern = this.state.pattern
            delete(host.fqdn)
            delete(host.short_name)
        }

        let { id } = this.props.match.params
        let { fqdn } = host
        let action = this.state.isNew ? Axios.post("/api/v1/hosts/", host) : Axios.put(`/api/v1/hosts/${id}`, host)
        let message = `Host ${fqdn} has been successfully ` + (this.state.isNew ? "created" : "updated")
        action.then( response => {
            if (response.data.count && response.data.count > 1) {
                message = `${response.data.count} hosts have been created`
            }
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

    handleSetPattern(pattern) {
        this.setState({ pattern })
    }

    handleClearPattern() {
        this.setState({ pattern: null })
    }

    render() {

        var patternBlock = "";
        if (this.state.pattern !== null) {
            if (this.state.isNew) {
                patternBlock = (
                    <div>
                        <MultipleHosts pattern={this.state.pattern} />
                    </div>
                )
            } else {
                patternBlock = (
                    <div className="alert alert-danger">
                        Patterns are only allowed in Create mode.
                    </div>
                )
            }
        }
        

        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>{this.state.title}</h2>
                    <div className="row">
                        <div className="col-sm-7">
                            <HostForm 
                                    host={this.state.host}
                                    isNew={this.state.isNew}
                                    onSubmit={this.handleSubmit.bind(this)}
                                    onDestroy={this.handleDestroy.bind(this)}
                                    onSetPattern={this.handleSetPattern.bind(this)}
                                    onClearPattern={this.handleClearPattern.bind(this)} />
                        </div>
                        <div className="col-sm-5">
                            { patternBlock }            
                        </div>
                    </div>
                </div>
            }            
            </div>
        )
    }
}