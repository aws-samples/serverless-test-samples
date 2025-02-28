exports.handler = async (event, context) => {

    const sum = event.sum;

    return {
        'Payload': {
            'result': sum * sum
        }
    }
    
};