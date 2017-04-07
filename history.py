from __future__ import print_function
import sys
import time
import json
from spotipy import Spotify, SpotifyException
from spotipy.oauth2 import SpotifyOAuth
import boto3
from boto3.dynamodb.conditions import Key

RECENTLY_PLAYED_SCOPE = 'user-read-recently-played'


class SpotifyHistoryMonitor(object):
    """ """


    def __init__(self):
        self._dynamodb = boto3.resource('dynamodb')
        self._load_configuration()
        self._spotify = Spotify(auth=self._access_token)
        self._plays = None


    def _load_configuration(self):
        """
        Get the latest configuration from DynamoDB
        """
        configuration = self._dynamodb.Table('configuration')
        response = configuration.get_item(Key={'scope': 'spotify'})
        self._access_token = response['Item']['access_token']
        self._refresh_token = response['Item']['refresh_token']
        self._client_id = response['Item']['client_id']
        self._client_secret = response['Item']['client_secret']


    def _save_configuration(self):
        """
        Save the current configuration to DynamoDB
        """
        configuration = self._dynamodb.Table('configuration')
        configuration.put_item(Item={'scope': 'spotify',
                                     'access_token': self._access_token,
                                     'refresh_token': self._refresh_token,
                                     'client_id': self._client_id,
                                     'client_secret': self._client_secret})


    def _renew_tokens(self):
        spotify_oauth = SpotifyOAuth(self._client_id, self._client_secret,
                                     redirect_uri=None, scope=RECENTLY_PLAYED_SCOPE)
        tokens = spotify_oauth.refresh_access_token(self._refresh_token)
        self._access_token = tokens['access_token']
        self._refresh_token = tokens['refresh_token']
        self._spotify = Spotify(auth=self._access_token)
        self._save_configuration()


    def _retrieve_plays(self):
        """
        Retrieve up to 50 recently played tracks.

        The API is currently limited to return 50 entries.

        If the access_token has expired, 
        attempt to renew it and save to DynamoDB
        """
        try:
            recents = self._spotify._get("me/player/recently-played", limit=50)
        except SpotifyException as se:
            if 'The access token expired' in se.msg:
                self._renew_tokens()
                recents = self._spotify._get("me/player/recently-played", limit=50)
            else:
                raise
        self._plays = recents['items']


    @property
    def plays(self):
        if not self._plays:
            self._retrieve_plays()
        return self._plays


    def save_new_plays(self):
        spotify_plays = self._dynamodb.Table('spotify_plays')
        response = spotify_plays.query(KeyConditionExpression=Key('user').eq('andrewslotnick'),
                                       ProjectionExpression='played_at',
                                       ScanIndexForward=False, #reverse order
                                       Limit=1)
        if response['Count'] == 0:
            plays_to_write = self.plays
        else:
            last_played_at = response['Items'][0]['played_at']
            plays_to_write = [p for p in self.plays if p['played_at'] > last_played_at]

        with spotify_plays.batch_writer() as writer:
            for play in plays_to_write:
                play_with_key = {'user':'andrewslotnick'}
                play_with_key.update(play)
                writer.put_item(play_with_key)

        return len(plays_to_write)


def main():
    spotify_history = SpotifyHistoryMonitor()
    num_written = spotify_history.save_new_plays()
    print(num_written)


def lambda_handler(event, context):
    spotify_history = SpotifyHistoryMonitor()
    num_written = spotify_history.save_new_plays()
    return {'num_written': num_written}


def authenticate_manually():
    from spotipy.util import prompt_for_user_token
    tokens = prompt_for_user_token(username, RECENTLY_PLAYED_SCOPE, 
                                   redirect_uri='http://andrewslotnick.com')
    print(tokens)


if __name__ == '__main__':
    main()