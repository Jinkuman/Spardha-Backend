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
        return createRankingHandler(event)

    elif httpMethod == 'GET':
        return getRankingHandler(event)

    elif httpMethod == 'POST':
        return modifyRankingHandler(event)

    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'HTTP Method not found!'})
        }


# Create ranking Handler, creates an event in the DynamoDB table
def createRankingHandler(event):
    body = json.loads(event['body'])
    item = {
        'id': str(uuid.uuid4()),
        'name': body['name'],
        'date': body['date'],
        'location': body.get('location')  # Using .get to handle cases where location might be absent
    }
    print("Creating ranking with item: " + json.dumps(item))
    table.put_item(Item=item)
    return sendResponse(200, item)

# Get ranking Handler, gets an event from the DynamoDB table
def getRankingHandler(event):
    ranking_id = event['queryStringParameters']['id']
    print("Getting ranking with id: " + ranking_id)
    response = table.get_item(Key={'id': ranking_id})

    item = response.get('Item')
    if not item:
        return sendResponse(404, "ranking not found")
    
    return sendResponse(200, item)

# Get ranking Handler, gets an event from the DynamoDB table
def getAllRankingsHandler(event):
    print("Getting All rankings:")
    response = table.get_item(Key={'id': ranking_id})

    item = response.get('Item')
    if not item:
        return sendResponse(404, "ranking not found")
    
    return sendResponse(200, item)

# Modify ranking Handler, modifies an event in the DynamoDB table
def modifyRankingHandler(event):
    try:
        body = json.loads(event['body'])
        rankingId = body['id']

        item = {
            'id': rankingId,
            'start date': body['start date'],
            'end date': body['end date'],
            'initial investment': body['initial investment'],

        }
        print("Modifying event with item: " + json.dumps(item))
        table.put_item(Item=item)
        return sendResponse(200, item)
    except Exception as e:
        print("Error in modifyrankingHandler: " + str(e))
        return sendResponse(500, str(e))
    
