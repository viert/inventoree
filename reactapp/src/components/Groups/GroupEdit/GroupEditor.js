import React, { Component } from 'react'
import Axios from 'axios'
import HttpErrorHandler from '../../../library/HttpErrorHandler'
// import AlertStore from '../../library/AlertBox'
import Loading from '../../common/Loading'

import GroupForm from './GroupForm'
import GroupRelationsForm from './GroupRelationsForm'

export default class GroupEditor extends Component {
    constructor(props) {
        super(props)
        this.state = {
            title: "New Group",
            group: {},
            isNew: true,
            isLoading: true
        }
    }

    componentDidMount() {
        var id = this.props.match.params.id;
        if (id && id !== "new") {
            Axios.get(`/api/v1/groups/${id}?_fields=children,name,description,project,tags,hosts`)
                .then( this.onDataLoaded.bind(this) )
                .catch( error => {
                    HttpErrorHandler(error)
                    this.props.history.push('/groups')
                })
        } else {
            this.setState({
                isLoading: false
            })
        }
    }

    onDataLoaded(response) {
        this.setState({
            group: response.data.data[0],
            title: "Edit Group",
            isNew: false,
            isLoading: false
        })        
    }

    handleSubmit(group) {
        console.log('in handleSubmit')
    }

    handleDestroy(group) {
        console.log('in handleDestroy')
    }

    handleSubmitRelations(child_ids, host_ids) {
        console.log('in handle submit relations', child_ids, host_ids)
    }

    render() {
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>{this.state.title}</h2>
                    <div className="row">
                        <div className="col-sm-4">
                            <GroupForm 
                                    group={this.state.group}
                                    isNew={this.state.isNew}
                                    onSubmit={this.handleSubmit.bind(this)}
                                    onDestroy={this.handleDestroy.bind(this)} />
                        </div>
                        <div className="col-sm-8">
                            {
                                this.state.isNew ? "" : 
                                <GroupRelationsForm
                                    group={this.state.group}
                                    onSubmitData={this.handleSubmitRelations.bind(this)} />
                            }
                        </div>
                    </div>
                </div>
            }            
            </div>
        )
    }

}