import json
import boto3
import os
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)
bucket_name = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')


# Custom JSON encoder for Decimal
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj) 
    raise TypeError

# Usage in your `sendResponse` function
def sendResponse(code, message):
    return {
        'statusCode': code,
        'body': json.dumps(message, default=decimal_default)
    }

# Main Handler, checks which HTTP method is being passed
def handler(event, context):
    print("Received event: " + json.dumps(event))
    httpMethod = event['httpMethod']

    if httpMethod == 'POST':
        return createSpottedHandler(event)

    elif httpMethod == 'GET':
        return getSpottedHandler(event)

    elif httpMethod == 'PUT':
        return modifySpottedHandler(event)

    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'HTTP Method not found!'})
        }


# Create spotted Handler, creates an event in the DynamoDB table
def createSpottedHandler(event):
    body = json.loads(event['body'])
    
    # Create a unique ID and time published
    item = {
        'id': str(uuid.uuid4()),
        'author': body['author'],
        'timePublished': body['timePublished'],
        'guesses': '0',
        'averageDistanceOffBy': 'N/A',
        'location': body['location'],
        'hint': body['hint']
    }
    
    # Generate presigned URL for image upload
    try:
        bucket_name = os.environ['BUCKET_NAME']
        key = f"spotted_images/{item['id']}.jpg"  # Define the path/key for the image
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        item['imageUrl'] = f"s3://{bucket_name}/{key}"  # Store S3 path in item
    except Exception as e:
        print("Error generating presigned URL:", e)
        return sendResponse(500, "Error generating presigned URL")

    # Insert item into DynamoDB
    table_name = os.environ['TABLE_NAME']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        table.put_item(Item=item)
    except Exception as e:
        print("Error writing to DynamoDB:", e)
        return sendResponse(500, "Error writing to DynamoDB")

    # Send the presigned URL back in the response
    response = {
        'message': 'Spotted item created',
        'spottedId': item['id'],
        'presignedUrl': presigned_url,
        'timePublished': item['timePublished']
    }
    
    return sendResponse(200, response)

    # Create the DynamoDB item
    item = {
        'id': spotted_id,
        'author': body.get('author', 'Unknown'),
        'timePublished': datetime.now().isoformat(),
        'guesses': 0,
        'averageDistanceOffBy': 'N/A',
        'hint': body.get('hint', ''),
        'location': body.get('location', {}),
        'imageUrl': f"s3://{bucket_name}/{image_key}"
    }
    table.put_item(Item=item)

    # Return the item and presigned URL for the frontend to use
    return {
        'statusCode': 200,
        'body': json.dumps({'item': item, 'uploadUrl': presigned_url})
    }

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
    print("Getting all spotteds:")
    response = table.scan()  # Scan for all items in the table

    items = response.get('Items')
    if not items:
        return sendResponse(404, "No spotteds found")
    
    return sendResponse(200, items)


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
    
