exports.lambdaHandler = async (event) => {
    const response = {
        statusCode: 200,
        body: JSON.stringify('This is mock response'),
    };
    return response;
};
