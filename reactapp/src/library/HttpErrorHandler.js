import React from 'react'
import AlertStore from './AlertBox'
import AuthState from './AuthState'

const HttpErrorHandler = (error) => {
    if (error.response) {
        if (error.response.status === 403) {
            if (error.response.data && error.response.data.state === "logged out") {
                AuthState.setAuthState({
                    authState: 'login',
                    user: null,
                    authUrl: error.response.data.auth_url,
                    authText: error.response.data.auth_text
                })
                return
            }
        }
        if (error.response.data && error.response.data.errors) {
            let prefix = error.response.data.error_type ? <b>{ error.response.data.error_type }: </b> : "" 
            error.response.data.errors.forEach((item) => {
                AlertStore.Alert(<div>{ prefix }{ item }</div>)
            })
            return
        }
        console.log(error)
    }
}

export default HttpErrorHandler;