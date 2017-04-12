import AlertStore from './AlertBox'

const HttpErrorHandler = (error) => {
    if (error.response && error.response.data && error.response.data.errors) {
        error.response.data.errors.forEach((item) => {
            AlertStore.Alert(item)
        });
    }
}

export default HttpErrorHandler;