const HttpErrorHandler = (error) => {
    if (error.response && error.response.data && error.response.data.errors) {
        error.response.data.errors.forEach((item) => {
            console.log(item);
        });
    }
}

export default HttpErrorHandler;