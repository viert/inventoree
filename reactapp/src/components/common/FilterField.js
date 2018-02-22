import React, { Component } from 'react'

export default class FilterField extends Component {
    constructor(props) {
        super(props)
        this.state = {
            filter: props.filter || '',
            name: props.name || 'Filter' 
        }
    }

    componentWillReceiveProps(props) {
        this.setState({
            filter: props.filter || '',
            name: props.name || 'Filter'
        })
    }

    filterChange = (e) => {
        this.setState({
            filter: e.target.value
        })
        if (this.props.onChange) {
            this.props.onChange(e.target.value)
        }
    }

    render() {
        let { name, filter } = this.state
        return (
            <div className="input-group">
                <span className="input-group-addon">{name}</span>
                <input value={filter} onChange={this.filterChange} type="text" className="form-control" />
            </div>
        )
    }
}