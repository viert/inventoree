import React, { Component } from 'react'
import PropTypes from 'prop-types'
import './CustomField.css'

export default class CustomField extends Component {
    render() {
        let cfClass = "custom_field" + 
            (this.props.derived? " custom_field--derived" : "") +
            (this.props.desaturate? " custom_field--desaturate" : "")
        let cfTitle = this.props.derived? "field derived from parent" : ""
        return ( 
            <div className={cfClass} title={cfTitle}>
                <span className="custom_field-key">{this.props.field.key}:</span> 
                <span className="custom_field-value">{this.props.field.value}</span> 
            </div>
        )
    }
}

CustomField.propTypes = {
    derived: PropTypes.bool,
    desaturate: PropTypes.bool,
    field: PropTypes.shape({
        key: PropTypes.string,
        value: PropTypes.string
    })
}