import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def handler(event, context):
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