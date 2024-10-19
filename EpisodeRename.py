import argparse
import json
import os
import re
import requests

base_url = "https://api.tvmaze.com"
single_search_url = f"{base_url}/singlesearch/shows?q="
multi_search_url = f"{base_url}/search/shows?q="


def get_show_info(title):
    response = requests.get(single_search_url + title)
    return response.json()



def get_show_info_year(title, year):
    response = requests.get(multi_search_url+title)
    info = response.json()
    for show in info:
        details = show["show"]
        if details["premiered"][0:4] == str(year):
            return details



def get_show_id(res):
    return res["id"]



def get_show_premier(res):
    return res["premiered"][0:4]



def get_show_episode_list(id):
    episode_list_url = f"{base_url}/shows/{str(id)}/episodes"
    response = requests.get(episode_list_url)
    return response.json()
    


def get_episode_info(id, season, number):
    episode_url = f"{base_url}/shows/{str(id)}/episodebynumber?season={str(season)}&number={str(number)}"
    response = requests.get(episode_url)
    return response.json()



def get_episode_name(id, season, number):
    res = get_episode_info(id, season, number)
    return res["name"]



def get_show_seasons(id):
    url = f"https://api.tvmaze.com/shows/{str(id)}/seasons"
    response = requests.get(url)
    return response.json()



def get_show_season_ids(id):
    res = get_show_seasons(id)
    ids = []
    for season in res:
        ids.append(season["id"])
    return ids



def get_episodes_for_season_id(id):
    url = f"https://api.tvmaze.com/seasons/{id}/episodes"
    response = requests.get(url)
    return response.json()



def find_disc_num(input):
    index = input.find("_D")

    if index != -1 and index + 2 < len(input):
        return input[index + 2]
    
    disc_string = "Disc "
    index = input.find(disc_string)

    if index != -1 and index + len(disc_string) < len(input):
        return input[index + len(disc_string)]
    
    return None



def sanitize_filename(input_string):
    restricted_characters = r'[\\/:*?"<>|]'
    sanitized_string = re.sub(restricted_characters, '', input_string)
    
    return sanitized_string



def format_file_name(show_title, season_num, episode_num, episode_name):
    return f"{show_title} - s{season_num:02}e{episode_num:02} - {episode_name}.mp4"



def main():

    parser = argparse.ArgumentParser(description="Simple program to rename series files to match Plex Server naming conventions.")
    parser.add_argument("-n", "--name", type=str, help="Show name", required=True)
    parser.add_argument("-y", "--year", type=int, help="Year premiered", required=False)
    parser.add_argument("-p", "--path", type=str, help="Path to show", required=False)

    args = parser.parse_args()
    
    title = args.name

    if args.year:
        premier = args.year
        info = get_show_info_year(title, premier)

    else:
        info = get_show_info(title)
        premier = get_show_premier(info)

    id = get_show_id(info)     

    show_title = f"{title} ({premier})"

    if args.path:
        base_path = args.path

    else:
        file_name = "configuration.json"

        with open(file_name, 'r') as jf:
            json_string = jf.read()

        dir_path = json.loads(json_string)
        base_path = dir_path["base_path"]

        if not base_path:
            base_path = os.getcwd()
        else:
            base_path = os.path.join(base_path, show_title)

    if not os.path.exists(base_path):
        exit(f"Failed to find path: {base_path}")

    season_ids = get_show_season_ids(id)
    
    for season_num, season in enumerate(os.scandir(base_path)):
        season_path = os.path.join(base_path, season.name)
        season_episodes = get_episodes_for_season_id(season_ids[season_num])
        
        for episode_num, episode in enumerate(os.scandir(season_path)):
            episode_name = sanitize_filename(season_episodes[episode_num]["name"])
            formated = format_file_name(show_title, season_num+1, episode_num+1, episode_name)
            ep_path = os.path.join(season_path, episode.name)
            updated_path = os.path.join(season_path, formated)
            os.rename(ep_path, updated_path)

if __name__ == "__main__":
    main()