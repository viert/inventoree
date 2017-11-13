import AlertStore from './AlertBox'
import AuthState from './AuthState'

const HttpErrorHandler = (error) => {
    if (error.response) {
        if (error.response.status === 403) {
            if (error.response.data && error.response.data.state === "logged out") {
                // For external auth urls
                if (error.response.data.auth_url) {
                    window.location.href = error.response.data.auth_url
                }
                AuthState.setAuthState({
                    authState: 'login',
                    user: null
                })
                return
            }
        }
        if (error.response.data && error.response.data.errors) {
            error.response.data.errors.forEach((item) => {
                AlertStore.Alert(item)
            })
            return
        }
        console.log(error)
    }
}

export default HttpErrorHandler;