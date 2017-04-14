import AlertStore from './AlertBox'
import AuthState from './AuthState'

const HttpErrorHandler = (error) => {
    console.log('in http error handler', error)
    if (error.response) {
        if (error.response.status === 403) {
            if (error.response.data && error.response.data.state === "logged out") {
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