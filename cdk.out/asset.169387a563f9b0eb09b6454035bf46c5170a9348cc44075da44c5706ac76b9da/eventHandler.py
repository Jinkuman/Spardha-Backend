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
        return createEventHandler(event)

    elif httpMethod == 'GET':
        return getEventHandler(event)

    elif httpMethod == 'POST':
        return modifyEventHandler(event)

    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'HTTP Method not found!'})
        }


# Create Event Handler, creates an event in the DynamoDB table
def createEventHandler(event):
    body = json.loads(event['body'])
    item = {
        'id': str(uuid.uuid4()),
        'name': body['name'],
        'date': body['date'],
        'location': body.get('location')  # Using .get to handle cases where location might be absent
    }
    print("Creating event with item: " + json.dumps(item))
    table.put_item(Item=item)
    return sendResponse(200, item)

# Get Event Handler, gets an event from the DynamoDB table
def getEventHandler(event):
    event_id = event['queryStringParameters']['id']
    print("Getting event with id: " + event_id)
    response = table.get_item(Key={'id': event_id})

    item = response.get('Item')
    if not item:
        return sendResponse(404, "Event not found")
    
    return sendResponse(200, item)

# Modify Event Handler, modifies an event in the DynamoDB table
def modifyEventHandler(event):
    try:
        body = json.loads(event['body'])
        eventID = event['pathParameters']['id']
        item = {
            'id': eventID,
            'name': body['name'],
            'date': body['date'],
            'location': body.get('location')
        }
        print("Modifying event with item: " + json.dumps(item))
        table.put_item(Item=item)
        return sendResponse(200, item)
    except Exception as e:
        print("Error in modifyEventHandler: " + str(e))
        return sendResponse(500, str(e))