import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def sendResponse(code, message):
    return {
        'statusCode': code,
        'body': json.dumps(message)
    }

# Main Handler, checks which HTTP method is being passed
def handler(event, context):
    print("Received event: " + json.dumps(event))
    httpMethod = event['httpMethod']

    if httpMethod == 'PUT':
        return createSpottedHandler(event)

    elif httpMethod == 'GET':
        return getSpottedHandler(event)

    elif httpMethod == 'POST':
        return modifySpottedHandler(event)

    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'HTTP Method not found!'})
        }


# Create spotted Handler, creates an event in the DynamoDB table
def createSpottedHandler(event):
    body = json.loads(event['body'])
    item = {
        'id': str(uuid.uuid4()),
        'name': body['name'],
        'date': body['date'],
        'location': body.get('location')  # Using .get to handle cases where location might be absent
    }
    print("Creating spotted with item: " + json.dumps(item))
    table.put_item(Item=item)
    return sendResponse(200, item)

# Get spotted Handler, gets an event from the DynamoDB table
def getSpottedHandler(event):
    spotted_id = event['queryStringParameters']['id']
    print("Getting spotted with id: " + spotted_id)
    response = table.get_item(Key={'id': spotted_id})

    item = response.get('Item')
    if not item:
        return sendResponse(404, "spotted not found")
    
    return sendResponse(200, item)

# Get spotted Handler, gets an event from the DynamoDB table
def getAllSpottedsHandler(event):
    print("Getting All spotteds:")
    response = table.get_item(Key={'id': spotted_id})

    item = response.get('Item')
    if not item:
        return sendResponse(404, "spotted not found")
    
    return sendResponse(200, item)

# Modify spotted Handler, modifies an event in the DynamoDB table
def modifySpottedHandler(event):
    try:
        body = json.loads(event['body'])
        spottedId = body['id']

        item = {
            'id': spottedId,
            'start date': body['start date'],
            'end date': body['end date'],
            'initial investment': body['initial investment'],

        }
        print("Modifying event with item: " + json.dumps(item))
        table.put_item(Item=item)
        return sendResponse(200, item)
    except Exception as e:
        print("Error in modifyspottedHandler: " + str(e))
        return sendResponse(500, str(e))
    
