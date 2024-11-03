import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as cognito from 'aws-cdk-lib/aws-cognito';

export class SrcStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    //Creating the DynamoDB table for storing 'spotteds'
    const spottedTable = new dynamodb.Table(this, 'spottedTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      tableName: 'spotted-table'
    })

    //Accessing the Lambda function to create spotteds
    const spottedHandler = new lambda.Function(this, 'spottedHandler', {
      runtime: lambda.Runtime.PYTHON_3_8,
      functionName: "spottedHandler",
      handler: 'spottedHandler.handler',
      code: lambda.Code.fromAsset('lambda'),
      environment: {
        TABLE_NAME : spottedTable.tableName,
      },
    });

      //Allow the lambda function to access the table
      spottedTable.grantReadWriteData(spottedHandler)

      //Create the API Gateway
      const spottedAPI = new apigw.RestApi(this, 'spottedAPI', {
        restApiName: 'spotted Service'
      });

      // //Create a Cognito User Pool 
      // const userPool = new cognito.UserPool(this, 'UserPool', {
      //   selfSignUpEnabled: true,
      //   signInAliases: {username: true, email: true}
      // });

      // //Create the user pool client
      // const userPoolClient = new cognito.UserPoolClient(this, 'UserPoolClient', {userPool});

      // //Create a Cognito Authorizer
      // const authorizer = new apigw.CognitoUserPoolsAuthorizer(this, 'APIAuthorizer', {cognitoUserPools: [userPool]});

      //Create an integration resource that will connect the lambda function to the api gateway
      const spottedIntegration = new apigw.LambdaIntegration(spottedHandler);
      const spottedResource = spottedAPI.root.addResource('spotted');

      spottedResource.addMethod('POST', spottedIntegration);
      spottedResource.addMethod('GET', spottedIntegration);
      spottedResource.addMethod('PUT', spottedIntegration);

    }
  
}
