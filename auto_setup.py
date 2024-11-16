import os
import json
import configparser
import logging
import shutil

logging.basicConfig(level=logging.INFO)


def load_json(json_path):
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file {json_path}: {e}")
        raise


def verify_config_file(config_file_path):
    if not os.path.isfile(config_file_path):
        raise Exception(f"Config file not found: {config_file_path}")

    config = configparser.ConfigParser()
    config.read(config_file_path)

    # required_sections = ["SERVER", "PAGE"]
    required_options = [
        ("SERVER", "base_url"),
        ("SERVER", "stagging_dir"),
        ("SERVER", "published_dir"),
        ("PAGE", "item_per_page")
    ]

    for section, option in required_options:
        if not config.has_section(section) or not config.has_option(section, option):
            raise Exception(f"Missing configuration: {section}.{option}")

    return config


def check_backend_initialization_state(config):
    staging_dir = config["SERVER"]["stagging_dir"]
    published_dir = config["SERVER"]["published_dir"]

    if not os.path.isdir(staging_dir) or not os.path.isdir(published_dir):
        return False
    return True


def initialize_backend(config):
    staging_dir = config["SERVER"]["stagging_dir"]
    published_dir = config["SERVER"]["published_dir"]
    item_per_page = config["PAGE"]["item_per_page"]

    # Create directories if they don't exist
    os.makedirs(staging_dir, exist_ok=True)
    os.makedirs(published_dir, exist_ok=True)

    # Create initial server.json and page.json files
    server_config = {
        "root": config["SERVER"]["base_url"],
        "items_per_page": item_per_page,
        "published_pages": "published/page.json"
    }
    with open(os.path.join(published_dir, "server.json"), "w") as f:
        json.dump(server_config, f, indent=2)

    published_page_json = [
        # {"name": "Posts", "path": "posts", "start_page": ""},
        # Add more categories as needed
    ]
    with open(os.path.join(published_dir, "page.json"), "w") as f:
        json.dump(published_page_json, f, indent=2)

    # Create initial post category and page
    stage_json_path = os.path.join(stagging_dir, "stage.json")
    os.makedirs(os.path.dirname(stage_json_path), exist_ok=True)

    post_page_json = []

    with open(stage_json_path, "w") as f:
        json.dump(post_page_json, f, indent=2)

    # # Create initial post category and page
    # post_category_path = os.path.join(published_dir, "posts")
    # os.makedirs(post_category_path, exist_ok=True)

    # post_page_json = {
    #     "root": "posts",
    #     "start_page": 0,
    #     "end_page": 0,
    #     "total_pages": 0
    # }
    # with open(os.path.join(post_category_path, "page.json"), "w") as f:
    #     json.dump(post_page_json, f, indent=2)


def validate_backend(published_dir, item_per_page):
    server_json_path = os.path.join(published_dir, "server.json")
    server_config = load_json(server_json_path)

    published_dir_page_json_path = os.path.join(published_dir, "page.json")
    published_pages = load_json(published_dir_page_json_path)
    published_pages_updated = False

    for i, category in enumerate(published_pages):
        category_path = os.path.join(published_dir, category["path"])
        category_page_json_path = os.path.join(category_path, "page.json")
        category_page_json = load_json(category_page_json_path)

        if not category["start_page"]:
            published_pages[i]["start_page"] = category_page_json["start_page"]
            published_pages_updated = True

        total_pages = category_page_json["total_pages"]
        for page_number in range(1, total_pages + 1):
            page_path = os.path.join(category_path, str(page_number))
            page_json_path = os.path.join(page_path, "page.json")
            page_json = load_json(page_json_path)

            # Validate the number of posts in the page against item_per_page
            if len(page_json["posts"]) > item_per_page:
                logging.warning(f"Page {page_number} in category {
                                category['name']} exceeds item_per_page limit")
                adjust_page(category_path, item_per_page,
                            page_number, page_json, page_json_path)

    if published_pages_updated == True:
        with open(published_dir_page_json_path, "w") as f:
            json.dump(published_pages, f, indent=2)


def adjust_page(category_path, item_per_page, page_num, page_data, page_json_path):
    if len(page_data["posts"]) > item_per_page:
        new_page_num = page_num + 1
        new_page_path = os.path.join(
            category_path, str(new_page_num), "page.json")

        # Create a new page
        os.makedirs(os.path.dirname(new_page_path), exist_ok=True)
        new_page_data = {
            "root": str(new_page_num),
            "current_page": new_page_num,
            # "page_size": item_per_page,
            "next_page": None,
            "posts": []
        }

        # Move excess posts to the new page
        excess_posts = page_data["posts"][item_per_page:]
        page_data["posts"] = page_data["posts"][:item_per_page]

        for post in excess_posts:
            # TODO move thumbnail if available
            post_dir = os.path.dirname(post["path"])
            shutil.move(
                os.path.join(category_path, str(page_num), post_dir),
                os.path.join(category_path, str(new_page_num), post_dir)
            )

            # Update the post paths in the new page's JSON
            post["path"] = post["path"].replace(
                str(page_num), str(new_page_num))
            new_page_data["posts"].append(post)

        # Update the previous page's next_page
        if new_page_num > 1:
            page_data["next_page"] = new_page_num

        # Update the category's page.json
        category_page_json_path = os.path.join(category_path, "page.json")
        category_page_json = load_json(category_page_json_path)
        category_page_json["total_pages"] = new_page_num
        category_page_json["end_page"] = new_page_num
        with open(category_page_json_path, "w") as f:
            json.dump(category_page_json, f, indent=2)

        # Write the updated page data
        with open(page_json_path, "w") as f:
            json.dump(page_data, f, indent=2)
        with open(new_page_path, "w") as f:
            json.dump(new_page_data, f, indent=2)


# stagging directory logic
def process_stagging_files(stagging_dir, published_dir):
    if os.path.isfile(os.path.join(stagging_dir, "stage.json")) == False:
        return

    stage_json = load_json(os.path.join(stagging_dir, "stage.json"))

    for stage in stage_json:
        if stage["filename"] is None or not os.path.isfile(os.path.join(stagging_dir, stage["filename"])):
            continue

        stagged_category = stage["category"]

        # check if category exists or not
        published_page_json_path = os.path.join(published_dir, "page.json")
        published_page_json = load_json(published_page_json_path)
        category_path = None

        for category in published_page_json:
            if str.lower(category["name"]) == str.lower(stagged_category):
                category_path = category["path"]
                break

        # category not exists
        if category_path is None:
            category_path = os.path.join(published_dir, stagged_category)

            # update published/page.json
            published_page_json.append(
                    {
                        "name": stagged_category,
                        "path": str.lower(stagged_category),
                        "start_page": 1
                    }
                )

        with open(published_page_json_path, "w") as f:
            json.dump(published_page_json, f, indent=2)

        category_json = None
        category_json_path = os.path.join(category_path, "page.json")
        if os.path.isfile(category_json_path) == True:
            category_json = load_json(category_json_path)

        if category_json is None:
            category_json = {
                    "root": str.lower(stagged_category),
                    "start_page": 1,
                    "end_page": 1,
                    "total_pages": 1
                }
            os.makedirs(os.path.dirname(category_json_path), exist_ok=True)

        with open(category_json_path, "w") as f:
                json.dump(category_json, f, indent=2)

        end_page_number = category_json["end_page"]
        page_json_path = os.path.join(
            category_path, str(end_page_number), "page.json")

        page_json = None
        if os.path.isfile(page_json_path) == True:
            page_json = load_json(page_json_path)

        else:
            # create new json for the page
            os.makedirs(os.path.dirname(page_json_path), exist_ok=True)
            page_json = {
                    "root": "1",
                    "current_page": 1,
                    "next_page": None,
                    "posts": []
            }

        # move files from stagging to last page and update page.json, then call adjust_page
        from_path = os.path.join(stagging_dir, stage["filename"])
        to_path = os.path.join(category_path, str(
                end_page_number), stage["filename"])

        # move html file
        shutil.move(from_path, to_path)

            # move thumbnail
        if stage["thumbnail"] and os.path.isfile(os.path.join(stagging_dir, stage["thumbnail"])):
            from_path = os.path.join(stagging_dir, stage["thumbnail"])
            # post_dir = os.path.dirname(from_path)
            to_path = os.path.join(category_path, str(
                    end_page_number), stage["thumbnail"])
            shutil.move(from_path, to_path)

        page_json["posts"].append(
            {
                "path": stage["filename"],
                "topic": stage["topic"],
                "thumbnail": stage["thumbnail"]
            })

        with open(page_json_path, "w") as f:
            json.dump(page_json, f, indent=2)

                # adjust_page


if __name__ == "__main__":
    config = verify_config_file("config.ini")
    published_dir = config["SERVER"]["published_dir"]
    stagging_dir = config["SERVER"]["stagging_dir"]
    item_per_page = int(config["PAGE"]["item_per_page"])

    if not check_backend_initialization_state(config):
        initialize_backend(config)
    else:

        validate_backend(published_dir, item_per_page)

    process_stagging_files(stagging_dir=stagging_dir,
                           published_dir=published_dir)
