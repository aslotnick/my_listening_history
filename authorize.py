import argparse
from spotipy.util import prompt_for_user_token
from spotifyhistorymonitor import RECENTLY_PLAYED_SCOPE


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Provide parameters associated with your application on developer.spotify.com')
    parser.add_argument('username')
    parser.add_argument('client_id')
    parser.add_argument('client_secret')
    parser.add_argument('redirect_uri')

    args = parser.parse_args()
    prompt_for_user_token(args.username,
                          RECENTLY_PLAYED_SCOPE, 
                          args.client_id,
                          args.client_secret,
                          args.redirect_uri)
    # retrieve from the cache
    with open('.cache-{}'.format(args.username)) as f:
        print(f.read())