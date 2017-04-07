# my_spotify_history
Periodically pull a user's 50 most recent plays and save them.

The Spotify Web API offers the endpoint "me/player/recently-played" which returns up to 50 recently played tracks.
Since there's no way (that I know of) to request more than 50, this project simply monitors the endpoint and dumps the information into DynamoDB for later analysis.

## Execution
* Every F minutes, where F is less than the average time it takes to play 50 tracks, the process should launch on AWS Lambda and retrieve the 50 available plays from Spotify.

* Tokens are saved in the "configuration" table in DynamoDB. If the user's access_token has expired, renew the tokens using the refresh_token. Then save the new values back to the database.

* Query for most recent track saved in the "spotify_plays" table in DynamoDB. Compare to the plays retrieved from Spotify, and save any new ones to the database.

## Known issues:
* Only built to support a single user at the moment.

* The access_token and refresh_token need to be set manually the first time.

* The data is only being collected at this point and no processing or analysis is being performed. But since this data is only available for a limited amount of time, it makes sense to start collecting it as soon as possible.