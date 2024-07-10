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
        return createChallengeHandler(event)

    elif httpMethod == 'GET':
        return getChallengeHandler(event)

    elif httpMethod == 'POST':
        return modifyChallengeHandler(event)

    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'HTTP Method not found!'})
        }


# Create Challenge Handler, creates an event in the DynamoDB table
def createChallengeHandler(event):
    body = json.loads(event['body'])
    item = {
        'id': str(uuid.uuid4()),
        'name': body['name'],
        'date': body['date'],
        'location': body.get('location')  # Using .get to handle cases where location might be absent
    }
    print("Creating challenge with item: " + json.dumps(item))
    table.put_item(Item=item)
    return sendResponse(200, item)

# Get Challenge Handler, gets an event from the DynamoDB table
def getChallengeHandler(event):
    challenge_id = event['queryStringParameters']['id']
    print("Getting challenge with id: " + challenge_id)
    response = table.get_item(Key={'id': challenge_id})

    item = response.get('Item')
    if not item:
        return sendResponse(404, "Challenge not found")
    
    return sendResponse(200, item)

# Get Challenge Handler, gets an event from the DynamoDB table
def getAllChallengesHandler(event):
    print("Getting All Challenges:")
    response = table.get_item(Key={'id': challenge_id})

    item = response.get('Item')
    if not item:
        return sendResponse(404, "Challenge not found")
    
    return sendResponse(200, item)

# Modify Challenge Handler, modifies an event in the DynamoDB table
def modifyChallengeHandler(event):
    try:
        body = json.loads(event['body'])
        challengeId = body['id']

        item = {
            'id': challengeId,
            'start date': body['start date'],
            'end date': body['end date'],
            'initial investment': body['initial investment'],

        }
        print("Modifying event with item: " + json.dumps(item))
        table.put_item(Item=item)
        return sendResponse(200, item)
    except Exception as e:
        print("Error in modifyChallengeHandler: " + str(e))
        return sendResponse(500, str(e))