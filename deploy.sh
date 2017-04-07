cp history.py lambda_deploy/
pushd lambda_deploy
zip -r ../history.zip . 
popd
aws lambda update-function-code --function-name history_monitor --zip-file fileb://history.zip 