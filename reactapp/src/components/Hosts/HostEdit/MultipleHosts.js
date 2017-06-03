import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { expandPattern } from '../../common/Permutation'
import './MultipleHosts.css'

export default class MultipleHost extends Component {
    constructor(props) {
        super(props)
        let hosts = this.getHosts(props.pattern)
        this.state = { hosts }
    }

    componentWillReceiveProps(props) {
        let hosts = this.getHosts(props.pattern)
        this.setState({ hosts })
    }

    getHosts(pattern) {
        let hosts = []
        let i = 0
        for (var host of expandPattern(pattern)) {
            if (i > 20) {
                hosts.push("...")
                break
            }
            hosts.push(host)
            i++
        }
        return hosts
    }

    render() {
        return (
            <div className="multiple-hosts">
                <h4>Warning: multiple host records will be created</h4>
                <ul className="multiple-hosts-list">
                    {
                        this.state.hosts.map( host => <li key={host}>{ host }</li> )
                    }
                </ul>
            </div>
        )
    }
}

MultipleHost.propTypes = {
    pattern: PropTypes.string.isRequired
}