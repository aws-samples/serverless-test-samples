exports.handler = async (event, context) => {

    const x = event.x;
    const y = event.y;
    const z = event.z;

    const sum = x + y + z;

    return {
        'Payload': {
            'result': sum
        }
    }
    
};