import random

def lambda_handler(event, _):
    """
    Reformat the record and add a random initial status.
    Validate the Unicorn Name and location
    """

    if event.get("Unicorn Name", None) is None:
        raise Exception("Unicorn Name not provided")
    
    if event.get("Unicorn Location", None) is None:
        raise Exception("Unicorn Location not provided")

    if random.uniform(0, 1) < 0.20:
        initial_status = "IN_TRAINING"
    else:
        initial_status = "AVAILABLE"
    
    return {"PK":event["Unicorn Name"],"LOCATION":event["Unicorn Location"],'STATUS' : initial_status}