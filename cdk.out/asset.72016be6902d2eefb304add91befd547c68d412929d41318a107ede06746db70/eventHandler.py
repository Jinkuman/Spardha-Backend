import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

# Main Handler, checks which HTTP method is being passed
def handler(event, context):
    httpMethod = event['httpMethod']

    if httpMethod == 'POST':
        createEventHandler(event)

    elif httpMethod == 'GET':
        getEventHandler(event)

    elif httpMethod == 'PUT':
        modifyEventHandler(event)

    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'HTTP Method not found!'})
        }
    
# Crete Event Handler, creates an event in the dynamoDB table
def createEventHandler(event):
    body = json.loads(event['body'])
    item = {
        'id': str(uuid.uuid4()),
        'name': body['name'],
        'date': body['date'],
        'location': body['location']
    }
    table.put_item(Item = item)

    return{
        'statusCode': 200,
        'body': json.dumps({'message': 'Event created successfully', 'event': item})
    }

# Get Event Handler, gets an event from the dynamoDB table
def getEventHandler(event):
    event_id = event['queryStringParameters']['id']
    response = table.get_item(Key={'id': event_id})

    item = response.get('Item')
    if not item:
        return{
            'statusCode': 404,
            'body': json.dumps({'message': 'Event not found!'})
        }

    return{
        'statusCode': 200,
        'body': json.dumps(item)
    }

# Modify Event Handler, modifies an event from the dynamoDB table
def modifyEventHandler(event):
    body = json.loads(event['body'])
    eventID = event['pathParameters']['id']

    updateExpression = "SET "
    expressionAttributeValues = {}

    for key, value in body.items():
        updateExpression += f"{key} = :{key}, "
        expressionAttributeValues[f":{key}"] = value

    updateExpression = updateExpression.rstrip(", ")

    try:
        response = table.update_item(
            Key= {'id': eventID},
            UpdateExpression = updateExpression,
            ExpressionAttributeValues = expressionAttributeValues,
            ReturnValues = "UPDATEDNEW"
        )
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Event Updated Successfully', 
                'Updated Attributes': repsonse['Attributes']
                }),
        }
    except Exception as e:
        return{
            'statusCode': 500,
            'body': json.dumps({'message': str(e)}),
        }
