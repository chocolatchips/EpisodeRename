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

def skip_split_episode(input_string):
    pattern = r'\(\d\)$'
    found = re.search(pattern, input_string)
    return found is not None
    
def sanitize_split_episode_name(input_string):
    pattern = r'\(\d\)$'
    sanitized_string = re.sub(pattern, '', input_string)
    return sanitized_string

def sanitize_filename(input_string):
    restricted_characters = r'[\\/:*?"<>|]'
    sanitized_string = re.sub(restricted_characters, '', input_string)
    
    return sanitized_string

def format_file_name(show_title, season_num, episode_num, episode_name):
    return f"{show_title} - s{season_num:02}e{episode_num:02} - {episode_name}.mp4"

def format_file_name_combine(show_title, season_num, episode_num, episode_name):
    return f"{show_title} - s{season_num:02}e{episode_num:02}-e{episode_num+1:02} - {episode_name}.mp4"

def rename_all_seasons(base_path, season_ids, merge, show_title, combine=False):
    for season_num in range(len(os.listdir(base_path))):
       rename_season(base_path, season_num+1, season_ids[season_num], merge, show_title, combine)

    print("All season renaming completed")

def rename_season(base_path, season_num, season_id, merge, show_title, combine=False):
    season_path = os.path.join(base_path, f"Season {season_num}")
    if not os.path.exists(season_path):
        print(f"{season_path} is not valid path")
        return

    episode_files = os.listdir(season_path)
    season_episodes = get_episodes_for_season_id(season_id)

    if combine:
        ep_to_rename = get_new_ep_names_combine(episode_files, season_episodes, show_title, season_num)
    else:
        ep_to_rename = get_new_ep_names(episode_files, season_episodes, merge, show_title, season_num)
    
    if verify_rewrite(ep_to_rename):
        rename_episodes(ep_to_rename, season_path)
        print(f"Season {season_num} completed")
    else:
        print(f"Season {season_num} skipped")
    

def verify_rewrite(ep_to_rename):
    print_for_verify(ep_to_rename)
    while(True):
        res = input("Confirm rewrite (Y/n):")
        if res == 'Y':
            return True
        if res == 'n':
            return False

def print_for_verify(ep_to_rename):
    for i in ep_to_rename:
        print(f"{i[0]} -> {i[1]}")

def get_new_ep_names(episode_files, season_episodes, merge, show_title, season_num):
    res = 0
    ep_to_rename = []
    for episode_num, episode in enumerate(episode_files):
            if episode_num >= len(season_episodes):
                return
            episode_name = sanitize_filename(season_episodes[episode_num + res]["name"])
            if merge and skip_split_episode(episode_name):
                res += 1
                episode_name = sanitize_split_episode_name(episode_name)

            formated = format_file_name(show_title, season_num, episode_num+1, episode_name)
            ep_to_rename.append((episode, formated))
            
    return ep_to_rename

def rename_episodes(ep_to_rename, season_path):
    for ep in ep_to_rename:
        os.rename(os.path.join(season_path, ep[0]), os.path.join(season_path, ep[1]))

def get_new_ep_names_combine(episode_files, season_episodes, show_title, season_num):
    res = 0
    ep_to_rename = []
    ep_count = iter(range(len(episode_files)))

    for ep_num in ep_count:
        if ep_num*2 >= len(season_episodes):
            return ep_to_rename
        episode_name = sanitize_filename(f"{season_episodes[ep_num*2 + res]['name']} & {season_episodes[ep_num*2 + res + 1]['name']}")
        
        formated = format_file_name_combine(show_title, season_num, ep_num*2 + 1, episode_name)
        ep_to_rename.append((episode_files[ep_num], formated))
    
    return ep_to_rename
    

def main():
    parser = argparse.ArgumentParser(description="Simple program to rename series files to match Plex Server naming conventions.")
    parser.add_argument("-n", "--name", type=str, help="Show name", required=True)
    parser.add_argument("-y", "--year", type=int, help="Year premiered", required=False)
    parser.add_argument("-p", "--path", type=str, help="Path to show", required=False)
    parser.add_argument("-s", "--season", type=int, help="Season to rename", required=False)
    parser.add_argument("-m", "--merge", action=argparse.BooleanOptionalAction, help="Merge split episodes")
    parser.add_argument("-c", "--combine", action=argparse.BooleanOptionalAction, help="Combine episode names")
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

    if args.season and 0 < args.season < len(season_ids):
        rename_season(base_path, args.season, season_ids[args.season-1], args.merge, show_title, args.combine)
    else:
        rename_all_seasons(base_path, season_ids, args.merge, show_title, args.combine)

    print("Episode renaming completed")

if __name__ == "__main__":
    main()