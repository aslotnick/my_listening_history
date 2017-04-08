cp spotifyhistorymonitor.py lambda_deploy/
pushd lambda_deploy
zip -r ../lambda_deploy.zip . 
popd
aws lambda update-function-code --function-name spotify_history_monitor --zip-file fileb://lambda_deploy.zip 