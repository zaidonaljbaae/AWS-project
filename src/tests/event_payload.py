def set_up_api(path, http_method, query_param, body):
    return {
        "body": body,
        "resource": "/{proxy+}",
        "path": path,
        "httpMethod": http_method,
        "queryStringParameters": query_param,
        "pathParameters": {
            "proxy": "/path/to/resource"
        },
        "stageVariables": {
            "baz": "qux"
        },
        "headers": {
            "Authorization": "Bearer eyJraWQiOiJ1QUU5c2NXOWo4a09wT1FkK0pjUzRDTlVMcVhiNGg0WUF6cXk0Y2c1dE1ZPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI3NGM4MjQzOC0wMGExLTcwOWQtODUyNC0wNTdmYzE5ZTZmNGUiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9KUndROXk0SmciLCJjbGllbnRfaWQiOiI1dmxpbG90a3I5bXRkcHZiNDdmanY5ZmQ3MyIsIm9yaWdpbl9qdGkiOiJiMzZkN2JlNy0zNzAwLTRmNjMtODBhNS00MDY2MTIwYzUxNWUiLCJldmVudF9pZCI6IjJlZmI3MDQ1LTlmZjYtNGQ0Zi04MTBmLTE4YmQ3MjlmZmI2NSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3MzAxNDQ2NDYsImV4cCI6MTczMTQxNDg5MSwiaWF0IjoxNzMxNDExMjkxLCJqdGkiOiI4YjE0YTlhYi04ZmE0LTRiMmItYTUxNi00MGI0OGY1YThiOWUiLCJ1c2VybmFtZSI6Ijc0YzgyNDM4LTAwYTEtNzA5ZC04NTI0LTA1N2ZjMTllNmY0ZSJ9.PwdoHpyyXlogjZMq0e5C_GBNTVB5jh5TBu2tUL1AnE4fs_rmw4h0x4Oq830AwjHvb19pdoYj7PWw9bJzbEHET8y7I3YF7Ffn-Didm6U-IsNq2lmHiCrS7F-QayuCGBqrzWpYv1M6ESYQtU-3eFe4gtUJqXTInRLaPrATORvkEEwKhhgCx5lKzXg4Z_d_pV-E0m2nuOc5BKkYhTC54Xz4j95PwU_-qJuTlbp6DK51qEX8EfGDoARYw4aK-C91y_r-JenEgmBBYgPvXwBrOOWfvoLP6MZSROXiz5cATiuat7DyAPA-rKq496JNxmTOGZDDj9Rop89OzsesCw4ttthxaw",
            "Content-Type": "application/json",
            "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "pt,en;q=0.8",
            "Cache-Control": "max-age=0",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "US",
            "Host": "1234567890.execute-api.{dns_suffix}",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Custom User Agent String",
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "X-Forwarded-For": "",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "requestContext": {
            "accountId": "123456789012",
            "resourceId": "123456",
            "stage": "prod",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "apiKey": None,
                "sourceIp": "",
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "Custom User Agent String",
                "user": None
            },
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "apiId": "1234567890"
        },
        "isBase64Encoded": False
        }

def set_up_dynamo(id, event_name):
    return {
        "Records": 
        [
            {
                "eventID": "1",
                "eventName": {event_name},
                "eventVersion": "1.0",
                "eventSource": "aws:dynamodb",
                "awsRegion": "{region}",
                "dynamodb": {
                    "Keys": {
                        "Id": {
                            "S": {id}
                            }
                        },
                    "NewImage": {
                        "Message": {
                            "S": "New item!"
                            },
                        "Id": {
                            "N": "101"
                            }
                        },
                    "SequenceNumber": "111",
                    "SizeBytes": 26,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": "arn:{partition}:dynamodb:{region}:account-id:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899"
            }
        ]
    }

def set_up_s3(bucket_name, key):
    return {
        "Records": 
        [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "{region}",
                "eventTime": "1970-01-01T00:00:00Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "responseElements": {
                    "x-amz-request-id": "EXAMPLE123456789",
                    "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": {bucket_name},
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        },
                        "arn": "arn:{partition}:s3:::mybucket"
                    },
                    "object": {
                        "key": {key},
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901"
                    }
                }
            }
        ]
    }
