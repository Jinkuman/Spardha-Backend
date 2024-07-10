import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as cognito from 'aws-cdk-lib/aws-cognito';

export class SrcStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    //Creating the DynamoDB table for storing 'Challenges'
    const challengeTable = new dynamodb.Table(this, 'challengeTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      tableName: 'challenge-table'
    })

    //Accessing the Lambda function to create challenges
    const challengeHandler = new lambda.Function(this, 'challengeHandler', {
      runtime: lambda.Runtime.PYTHON_3_8,
      functionName: "ChallengeHandler",
      handler: 'challengeHandler.handler',
      code: lambda.Code.fromAsset('lambda'),
      environment: {
        TABLE_NAME : challengeTable.tableName,
      },
    });

      //Allow the lambda function to access the table
      challengeTable.grantReadWriteData(challengeHandler)

      //Create the API Gateway
      const challengeAPI = new apigw.RestApi(this, 'challengeAPI', {
        restApiName: 'Challenge Service'
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
      const challengeIntegration = new apigw.LambdaIntegration(challengeHandler);
      const challengeResource = challengeAPI.root.addResource('challenge');

      challengeResource.addMethod('POST', challengeIntegration);
      challengeResource.addMethod('GET', challengeIntegration);
      challengeResource.addMethod('PUT', challengeIntegration);

    }
  
}
