import React, { Component } from 'react'
import Axios from 'axios';
import HttpErrorHandler from '../../library/HttpErrorHandler'
import AlertStore from '../../library/AlertBox'
import Loading from '../common/Loading'

import DatacenterForm from './DatacenterForm'

export default class DatacenterEditor extends Component {
    constructor(props) {
        super(props)
        this.state = {
            title: "New Datacenter",
            datacenter: {},
            isNew: true,
            isLoading: true
        }
    }

    componentDidMount() {
        const id = this.props.match.params.id;
        if (id && id !== "new") {
            Axios.get(`/api/v1/datacenters/${id}?_fields=_id,name,human_readable,parent_id,parent`)
                .then((response) => {
                    this.setState({
                        datacenter: response.data.data[0],
                        title: "Edit Datacenter",
                        isNew: false,
                        isLoading: false
                    })
                })
                .catch( error => {
                    HttpErrorHandler(error)
                    this.props.history.push('/datacenters')
                })
        } else {
            this.setState({
                isLoading: false
            })
        }
    }

    handleSubmit(datacenter) {
        var action;
        const parent_id = datacenter.parent_id === "" ? null : datacenter.parent_id
        const payload = {
            name: datacenter.name,
            human_readable: datacenter.human_readable,
            parent_id: parent_id
        }

        if (datacenter._id) {
            action = Axios.put(`/api/v1/datacenters/${datacenter._id}`, payload)
        } else {
            action = Axios.post('/api/v1/datacenters/', payload)
        }

        action
            .then( response => {
                AlertStore.Notice(`Datacenter ${datacenter.name} has been saved successfully`)
                this.props.history.push("/datacenters")
            })
            .catch(HttpErrorHandler)
    }

    handleDestroy(datacenter) {
        Axios.delete(`/api/v1/datacenters/${datacenter._id}`)
            .then( response => {
                AlertStore.Notice(`Datacenter ${datacenter.name} has been successfully deleted`)
                this.props.history.push("/datacenters")
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
                        <div className="col-sm-6">
                            <DatacenterForm 
                                    datacenter={this.state.datacenter}
                                    isNew={this.state.isNew}
                                    onSubmit={this.handleSubmit.bind(this)}
                                    onDestroy={this.handleDestroy.bind(this)} />
                        </div>
                    </div>
                </div>
            }
            </div>
        )
    }
}