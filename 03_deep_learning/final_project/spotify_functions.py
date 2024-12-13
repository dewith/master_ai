import pandas as pd


def offset_api_limit(sp, sp_call):
    """
    Get all (non-limited) artists/tracks from a Spotify API call.
    :param sp: Spotify OAuth
    :param sp_call: API function all
    :return: list of artists/tracks
    """
    results = sp_call
    if 'items' not in results.keys():
        results = results['artists']
    data = results['items']
    while results['next']:
        results = sp.next(results)
        if 'items' not in results.keys():
            results = results['artists']
        data.extend(results['items'])
    return data

