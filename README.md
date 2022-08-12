# aws-lambda-pyodbc-3-9-layer

## Overview
This repo contains a zip file with the dependencies to import the pyodbc module into a AWS Lambda function with the Python 3.9 runtime which allows connections to MS SQL databases.


The pyodbc module requires `unixODBC`, the `Microsoft ODBC Driver` and the `pyodbc` python module which are not provided in the AWS Lambda environment by default and must therefore be provided though an additional layer.


This zip file for the layer is prepared in the `pyodbc-3-9.zip` file in this repo.


Full credit goes to Randy Westergren for providing this guide and the Dockerfile also in this repo.

https://randywestergren.com/building-pyodbc-for-lambdas-python-3-9-runtime/


## Example Deployment
Along with the prepared layer zip file, this repo also contains an example CloudFormation template and a sample Python script.

### Sample Python Script
The sample Python script provided is a simple script to run a `SELECT TOP 100 * FROM Users` query. Naturally this can be changed and expanded upon to suit the database.

The script has 4 stages:
1. Retreive the secret from AWS Secret Manager which contains the SQL database connection details and credentials.
2. Parse the secret key/value pairs and connect to the SQL server using the ODBC driver provided in the Lambda layer.
3. Run the SQL query against the database.
4. Print the results to stdout which will be available in the CloudWatch Log Group.

### CloudFormation - template.yaml
#### Parameters:
- `LambdaVPCId`: The ID of the VPC in which Lambda will run in order to access database resources (such as EC2 or RDS) within the VPC.
- `LambdaSubnetId`: The ID of the subnet in which Lambda will run in order to access database resources (such as EC2 or RDS) within the VPC.

#### Resources:
- `PythonODBCLambdaLayer`: Deploys the zip file which contains the pyodbc module dependancies as a Lambda layer to be used alongside the Lambda function.
- `LambdaFunction`: Creates a Lambda function to run the Python code. An ENI is created in the specified VPC/Subnet in the parameters to allow access to local resorces.
- `LambdaRole`: Create an IAM role which Lambda will use to access AWS services. This role allows Lambda to write to a log group, and retrieve a secret from AWS Secrets Manager
- `LambdaSecurityGroup`: Creates an empty security group to attach to the ENI. Lambda only needs to make outbound connections in this example which is allowed by default.
- `LambdaLogGroup`: Creates a CloudWatch Log Group and specifies a default retention period.
- `SqlCredsSecretKmsKey`: Creates a KMS Key to encrypt secrets stored in AWS Secrets Manager.
- `SqlCredsSecret`: Creates a secret in AWS Secrets Manager containing the connection details and credentials for the database. A placeholder value is set on first deploy so must be changed manually after. The name off this secret is provided to Lambda as an environment variable.



### Deployment
Using the AWS SAM CLI, run the following commands to deploy the Lambda layer and sample function. Change the `sam deploy` parameters as necessary.
~~~
sam build
~~~

~~~
sam deploy \
    --stack-name "Example-Lambda-SQL" \
    --region "eu-west-2" \
    --capabilities CAPABILITY_IAM \
    --s3-bucket "CHANGE-ME" \
    --parameter-overrides \
    LambdaVpcId="CHANGE-ME" \
    LambdaSubnetId="CHANGE-ME"
~~~