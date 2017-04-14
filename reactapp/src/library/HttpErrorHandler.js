import AlertStore from './AlertBox'
import AuthState from './AuthState'

const HttpErrorHandler = (error) => {
    if (error.response) {
        if (error.response.status === 403) {
            AuthState.setState({
                authState: 'login',
                user: null
            })
            return
        }
        if (error.response.data && error.response.data.errors) {
            error.response.data.errors.forEach((item) => {
                AlertStore.Alert(item)
            })
        }
    }
}

export default HttpErrorHandler;