import React, { Component } from 'react'

export default class Pagination extends Component {

    constructor(props) {
        super(props)
        this.state = {
            pages: Pagination.calculatePager(props)
        }
    }

    static calculatePager(props) {
        let { current, total, spread=3 } = props
        
        // some sanity checks
        if (current < 1) { current = 1 }
        if (current > total) { current = total }

        // always show the first page
        let result = [
            { id: "prev", page: <span>&laquo;</span>, disabled: current === 1 },
            { id: 1, page: 1, disabled: current === 1 }
        ]

        let i = 2
        if ((current - spread) > 2) {
            result.push({ id: 2, page: '...', disabled: true })
            i = current - spread
        }
        while (i <= current + spread && i <= total) {
            result.push({ id: i, page: i, disabled: current === i })
            i++
        }
        if (i < total - 1) {
            result.push({ id: i, page: '...', disabled: true })
        }

        // show the last page
        if (total > current) {
            result.push({ id: total, page: total, disabled: current === total })
        }
        result.push({ id: "next", page: <span>&raquo;</span>, disabled: current === total })
        return result
    }

    pageClick(page, e) {
        e.preventDefault()
        if (page.disabled) return

        var newPage
        switch (page.id) {
            case "prev":
                newPage = this.props.current - 1
                break;
            case "next":
                newPage = this.props.current + 1
                break;
            default:
                newPage = page.page
        }
        this.props.onChangePage(newPage)
    }

    componentWillReceiveProps(props) {
        this.setState({
            pages: Pagination.calculatePager(props)
        })
    }

    render() {
        return (
            <nav aria-label="Page navigation" className={this.props.className}>
                {
                    this.props.total > 1 ?
                        <ul className="pagination">
                        {
                            this.state.pages.map((page) => {
                                return <li className={page.disabled? 'disabled': ''} key={page.id}><a href="#" onClick={this.pageClick.bind(this, page)}>{ page.page }</a></li>
                            })
                        }
                        </ul>
                    : ''
                }
            </nav>        
        )
    }
}

window.Pagination = Pagination