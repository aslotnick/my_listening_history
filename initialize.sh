# usage:
# ./initialize.sh <aws_account_id> <client_id> <client_secret> <access_token> <refresh_token>
AWS_ACCOUNT_ID=$0
CLIENT_ID=$1
CLIENT_SECRET=$2
ACCESS_TOKEN=$3
REFRESH_TOKEN=$4

cp spotifyhistorymonitor.py lambda_deploy/
pushd lambda_deploy
zip -r ../lambda_deploy.zip . 
popd

aws lambda create-function \
    --function-name spotify_history_monitor \
    --runtime python2.7 \
    --role arn:aws:iam::$AWS_ACCOUNT_ID:role/service-role/history_monitor_lambda_role \
    --handler history.lambda_handler \
    --zip-file fileb://lambda_deploy.zip \
    --memory-size 128 \
    --timeout 60

aws dynamodb create-table \
    --table-name configuration \
    --attribute-definitions AttributeName=scope,AttributeType=S \
    --key-schema KeyType=HASH,AttributeName=scope \
    --provisioned-throughput "WriteCapacityUnits=1, ReadCapacityUnits=1"

aws dynamodb create-table \
    --table-name spotify_plays \
    --attribute-definitions AttributeName=played_at,AttributeType=S AttributeName=user,AttributeType=S \
    --key-schema KeyType=HASH,AttributeName=user KeyType=RANGE,AttributeName=played_at \
    --provisioned-throughput "WriteCapacityUnits=1, ReadCapacityUnits=1"

aws dynamodb put-item \
    --table-name configuration \
    --item scope={"S"="spotify"},client_id={"S"="$CLIENT_ID"},client_secret={"S"="$CLIENT_SECRET"},access_token={"S"="$ACCESS_TOKEN"},refresh_token={"S"="$REFRESH_TOKEN"}


