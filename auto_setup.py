
import os.path
import configparser
import logging #TODO
import json

def load_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data
        
# verify json file
def verify_json(json_file):
    if (os.path.isfile(json_file)):
        data = load_json(json_file)
        if not data:
            raise Exception("Something wrong" + json_file)

def verify_config_file(config_file_path):
    if os.path.isfile(config_file_path) == True:
           # init configurations
        config = configparser.ConfigParser()
        config.read(config_file_path)
        
        base_url = config["SERVER"]["base_url"]
        stagging_dir = config["SERVER"]["stagging_dir"]
        published_dir = config["SERVER"]["published_dir"]
        item_per_page = config["PAGE"]["item_per_page"]

        if not base_url or not stagging_dir or not published_dir or not item_per_page:
            raise Exception("Invalid config parameters")
        
        return config
    else:
        raise Exception("Config file not found! config.ini must be present")


def check_backend_initialization_state(config):
    stagging_dir = config["SERVER"]["stagging_dir"]
    published_dir = config["SERVER"]["published_dir"]
    
    if os.path.isdir(stagging_dir) == False and os.path.isdir(published_dir) == False:
        raise Exception("Backend directories are missing")

def validate_backend(published_dir):
    SERVER_JSON = "server.json"
    PAGE_JSON = "page.json"

    verify_json(SERVER_JSON)
    
    published_page_json = load_json(os.path.join(published_dir,PAGE_JSON))
    for i, page in enumerate(published_page_json):
        page_json = load_json(os.path.join(published_dir,page["path"],PAGE_JSON))
        for page_number in range(page_json["total_pages"]):
            pass

        
        

if __name__ == "__main__":
    # validate config files and its parameters
    config = verify_config_file("config.ini")

    # verify if backend already initialized or not
    if check_backend_initialization_state(config):
        validate_backend()
    # else:
    #     initialize_backend()