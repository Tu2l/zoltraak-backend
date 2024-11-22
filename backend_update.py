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
        return {}


def verify_config_file(config_file_path):
    if not os.path.isfile(config_file_path):
        raise Exception(f"Config file not found: {config_file_path}")

    config = configparser.ConfigParser()
    config.read(config_file_path)

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

    return os.path.isdir(staging_dir) and os.path.isdir(published_dir)


def initialize_backend(config):
    staging_dir = config["SERVER"]["stagging_dir"]
    published_dir = config["SERVER"]["published_dir"]
    item_per_page = int(config["PAGE"]["item_per_page"])

    # Create directories
    os.makedirs(staging_dir, exist_ok=True)
    os.makedirs(published_dir, exist_ok=True)

    # Create initial stage.json, server.json and page.json
    with open(os.path.join(stagging_dir, "template.stage.json"), "w") as f:
        json.dump([{
            "filename": "filename path",
            "thumbnail": "thumbnail path",
            "topic": "about the file content",
            "category": "posts"
        }], f, indent=2)

    server_config = {
        "root": config["SERVER"]["base_url"],
        "items_per_page": item_per_page,
        "published_pages": "published/page.json"
    }
    with open(os.path.join(published_dir, "server.json"), "w") as f:
        json.dump(server_config, f, indent=2)

    with open(os.path.join(published_dir, "page.json"), "w") as f:
        json.dump([], f, indent=2)


def validate_backend(published_dir, item_per_page):
    published_page_json_path = os.path.join(published_dir, "page.json")
    published_pages = load_json(published_page_json_path)
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

            if len(page_json["posts"]) > item_per_page:
                logging.warning(f"Page {page_number} in category {
                                category['name']} exceeds item_per_page limit")
                adjust_page(category_path, item_per_page,
                            page_number, page_json, page_json_path)

    if published_pages_updated:
        with open(published_page_json_path, "w") as f:
            json.dump(published_pages, f, indent=2)


def adjust_page(category_path, item_per_page, page_num, page_data, page_json_path):
    if len(page_data["posts"]) > item_per_page:
        new_page_num = page_num + 1
        new_page_dir = os.path.join(category_path, str(new_page_num))
        new_page_json_path = os.path.join(new_page_dir, "page.json")

        # Ensure the new page directory exists
        os.makedirs(new_page_dir, exist_ok=True)

        new_page_data = {
            "root": str(new_page_num),
            "current_page": new_page_num,
            "next_page": None,
            "posts": []
        }

        excess_posts = page_data["posts"][item_per_page:]
        page_data["posts"] = page_data["posts"][:item_per_page]

        for post in excess_posts:
            post_dir = os.path.dirname(post["path"]) 
            source_path = os.path.join(category_path, str(page_num), post_dir if post_dir else post["path"])
            dest_path = os.path.join(
                category_path, str(new_page_num), post_dir)

            # Move excess posts
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.move(source_path, dest_path)

            post["path"] = post["path"].replace(
                str(page_num), str(new_page_num))
            new_page_data["posts"].append(post)

        if new_page_num > 1:
            page_data["next_page"] = new_page_num

        # Update category's page.json
        category_page_json_path = os.path.join(category_path, "page.json")
        category_page_json = load_json(category_page_json_path)
        category_page_json["total_pages"] = new_page_num
        category_page_json["end_page"] = new_page_num
        with open(category_page_json_path, "w") as f:
            json.dump(category_page_json, f, indent=2)

        # Write the updated page data
        with open(page_json_path, "w") as f:
            json.dump(page_data, f, indent=2)
        with open(new_page_json_path, "w") as f:
            json.dump(new_page_data, f, indent=2)


def initialize_category(category_path, stagged_category):
    category_json_path = os.path.join(category_path, "page.json")
    if not os.path.exists(category_json_path):
        category_json = {
            "root": stagged_category.lower(),
            "start_page": 1,
            "end_page": 1,
            "total_pages": 1
        }
        os.makedirs(os.path.dirname(category_json_path), exist_ok=True)
        with open(category_json_path, "w") as f:
            json.dump(category_json, f, indent=2)
        return category_json
    return load_json(category_json_path)


def process_stagging_files(stagging_dir, published_dir):
    stage_json_path = os.path.join(stagging_dir, "stage.json")
    if not os.path.isfile(stage_json_path):
        return

    stage_json = load_json(stage_json_path)

    for stage in stage_json:
        if not stage.get("filename") or not os.path.isfile(os.path.join(stagging_dir, stage["filename"])):
            continue

        stagged_category = stage["category"]
        published_page_json_path = os.path.join(published_dir, "page.json")
        published_page_json = load_json(published_page_json_path)

        category_path = None
        for category in published_page_json:
            if category["name"].lower() == stagged_category.lower():
                category_path = os.path.join(published_dir, category["path"])
                break

        if not category_path:
            category_path = os.path.join(
                published_dir, stagged_category.lower())
            os.makedirs(category_path, exist_ok=True)
            published_page_json.append({
                "name": stagged_category,
                "path": stagged_category.lower(),
                "start_page": 1
            })
            with open(published_page_json_path, "w") as f:
                json.dump(published_page_json, f, indent=2)

        category_json = initialize_category(category_path, stagged_category)
        end_page_number = int(category_json["end_page"])
        page_dir = os.path.join(category_path, str(end_page_number))
        page_json_path = os.path.join(page_dir, "page.json")

        if not os.path.exists(page_json_path):
            os.makedirs(page_dir, exist_ok=True)
            page_json = {"root": str(
                end_page_number), "current_page": end_page_number, "next_page": None, "posts": []}
        else:
            page_json = load_json(page_json_path)

        post_dir = os.path.dirname(stage["filename"])
        to_path = os.path.join(page_dir,  post_dir if post_dir else stage["filename"])
        shutil.move(os.path.join(stagging_dir,  post_dir if post_dir else stage["filename"]), to_path)

        if stage.get("thumbnail"):
            thumbnail_src = os.path.join(stagging_dir, stage["thumbnail"])
            if os.path.isfile(thumbnail_src):
                shutil.move(thumbnail_src, os.path.join(
                    page_dir, stage["thumbnail"]))

        page_json["posts"].append({
            "path": stage["filename"],
            "topic": stage["topic"],
            "thumbnail": stage.get("thumbnail", "")
        })

        with open(page_json_path, "w") as f:
            json.dump(page_json, f, indent=2)

        # adjust_page(category_path, int(
        #     config["PAGE"]["item_per_page"]), end_page_number, page_json, page_json_path)


if __name__ == "__main__":
    config = verify_config_file("config.ini")
    published_dir = config["SERVER"]["published_dir"]
    stagging_dir = config["SERVER"]["stagging_dir"]
    item_per_page = int(config["PAGE"]["item_per_page"])

    if not check_backend_initialization_state(config):
        initialize_backend(config)
    else:
        validate_backend(published_dir, item_per_page)

    process_stagging_files(stagging_dir, published_dir)
