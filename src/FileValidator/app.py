import json

def lambda_handler(event, context):
    # TODO implement
    contents=str(event)
    print(contents)
    for entry in contents.split(","):
         if "Unicorn" in entry:
            if len(entry.split(":")) != 2:
                raise Exception("Not a unicorn File")
    
    return {"unicorn_name":event["Unicorn Name"],"LOCATION":event["Unicorn Location"],'STATUS' : "AVAILABLE"}