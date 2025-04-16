def handler(event, context):

    sum_value = event.get('result', 0)
    square_result = sum_value * sum_value
    
    return {
        'Payload': {
            'result': square_result
        }
    }