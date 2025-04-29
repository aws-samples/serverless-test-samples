def handler(event, context):

    x = event.get('x', 0)
    y = event.get('y', 0)
    z = event.get('z', 0)
    
    sum_result = x + y + z
    
    return {
        'Payload': {
            'result': sum_result
        }
}