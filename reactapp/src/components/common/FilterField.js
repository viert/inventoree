import React, { Component } from 'react'

export default class FilterField extends Component {
    constructor(props) {
        super(props)
        this.state = {
            filter: props.filter || ''
        }
    }

    componentWillReceiveProps(props) {
        this.setState({
            filter: props.filter
        })
    }

    filterChange(e) {
        this.setState({
            filter: e.target.value
        })
        if (this.props.onChange) {
            this.props.onChange(e.target.value)
        }
    }


    render() {
        return (
            <div className="input-group">
                <span className="input-group-addon">Filter</span>
                <input value={this.state.filter} onChange={this.filterChange.bind(this)} type="text" className="form-control" />
            </div>
        )
    }
}