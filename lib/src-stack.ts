import { Duration, Stack, StackProps, RemovalPolicy } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';

export class SrcStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Creating the DynamoDB table for storing 'spotteds'
    const spottedTable = new dynamodb.Table(this, 'spottedTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      tableName: 'spotted-table',
    });

    // Creating an S3 bucket for storing images
    const spottedBucket = new s3.Bucket(this, 'SpottedImagesBucket', {
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });   

    // Creating the Lambda function for handling spotted operations
    const spottedHandler = new lambda.Function(this, 'spottedHandler', {
      runtime: lambda.Runtime.PYTHON_3_8,
      functionName: 'spottedHandler',
      handler: 'spottedHandler.handler',
      code: lambda.Code.fromAsset('lambda'),
      environment: {
        TABLE_NAME: spottedTable.tableName,
        BUCKET_NAME: spottedBucket.bucketName, // Pass the S3 bucket name to Lambda
      },
    });

    // Grant the Lambda function permission to read/write to the DynamoDB table
    spottedTable.grantReadWriteData(spottedHandler);

    // Grant the Lambda function permission to upload to the S3 bucket
    spottedBucket.grantReadWrite(spottedHandler);

    // Create the API Gateway
    const spottedAPI = new apigw.RestApi(this, 'spottedAPI', {
      restApiName: 'spotted Service',
    });

    // Create an integration resource that will connect the Lambda function to the API Gateway
    const spottedIntegration = new apigw.LambdaIntegration(spottedHandler);
    const spottedResource = spottedAPI.root.addResource('spotted');

    spottedResource.addMethod('POST', spottedIntegration);
    spottedResource.addMethod('GET', spottedIntegration);
    spottedResource.addMethod('PUT', spottedIntegration);
    spottedHandler.addEnvironment('BUCKET_NAME', spottedBucket.bucketName);
  }
}
