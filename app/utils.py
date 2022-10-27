#!/usr/bin/env python3
from thefuzz import process, fuzz

def artist_names_from_result(items):
    artist_names = set()

    for idx, track in enumerate(items):
        artist_names.add(track['artists'][0]['name'])
    return artist_names


def fuzzy_match_artist(artist_names: set, track_input: str) -> bool: 
    match_grade = process.extract(track_input, artist_names, limit=3, scorer=fuzz.token_sort_ratio)
    if match_grade[0][1] > 70:
        print(f'Fuzy match found {match_grade}')
        return True
    else:
        print(f'Fuzy match not found {match_grade}')
        return False