import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def handler(event, context):
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