import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Autosuggest from 'react-autosuggest'
import './AutosuggestContainer.css'

const getSuggestionValue = suggestion => suggestion.name
const renderSuggestion = suggestion => (
    <div>
        {suggestion.name}
    </div>
)

export default class AutosuggestContainer extends Component {
    constructor(props) {
        super(props)
        this.state = {
            suggestions: [],
            value: this.props.value
        }
    }

    handleChange(event, { newValue }) {
        this.setState({
            value: newValue
        })
    }

    loadData(value, callback) {
    }

    handleSuggestionsFetchRequested({ value }) {
        this.loadData( value, data => {
            this.props.onDataClear()
            this.setState({
                suggestions: data
            })
        })
    }

    handleSuggestionsClearRequested() {
        this.setState({
            suggestion: []
        })
    }

    handleSuggestionSelected(event, { suggestion }) {
        this.props.onDataPicked(suggestion)
    }

    render() {
        const { value, suggestions } = this.state
        const inputProps = {
            placeholder: this.props.placeholder,
            id: "inputDatacenterParent",
            className: "form-control",
            value,
            onChange: this.handleChange.bind(this)
        }

        return (
            <Autosuggest
                suggestions={suggestions}
                onSuggestionsFetchRequested={this.handleSuggestionsFetchRequested.bind(this)}
                onSuggestionsClearRequested={this.handleSuggestionsClearRequested.bind(this)}
                onSuggestionSelected={this.handleSuggestionSelected.bind(this)}
                getSuggestionValue={getSuggestionValue}
                renderSuggestion={renderSuggestion}
                inputProps={inputProps} />
        )
    }
}

AutosuggestContainer.propTypes = {
    onDataPicked: PropTypes.func.isRequired,
    onDataClear: PropTypes.func.isRequired,
    placeholder: PropTypes.string
}