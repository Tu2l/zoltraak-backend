import os
import json
import logging
import configparser
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fill_stage_json(stagging_dir):
    """
    Fills the stage.json file based on the HTML files present in the stagging directory.
    """
    stage_json_path = os.path.join(stagging_dir, "stage.json")
    stage_data = []

    for filename in os.listdir(stagging_dir):
        if filename.endswith(".html"):
            file_path = os.path.join(stagging_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    # Extract title from title tag
                    title = soup.find('title').text if soup.find('title') else "No Title"
                    # Extract description from meta description tag
                    description = soup.find('meta', attrs={'name': 'description'})
                    description = description.get('content') if description else "No Description"
                    # Extract post_name from h1 tag
                    h1 = soup.find('h1').text if soup.find('h1') else "No Post Name"
                    # You might need to adjust the thumbnail extraction logic based on your HTML structure
                    # This is just a placeholder
                    thumbnail = ""  # Replace with actual thumbnail path if available
                    stage_data.append({
                        "filename": filename,
                        "thumbnail": thumbnail,
                        "description": description,
                        "category": "posts",  # Default category
                        "title": h1
                    })
            except Exception as e:
                logging.error(f"Error processing {filename}: {e}", exc_info=True)

    # Write the combined data to stage.json
    with open(stage_json_path, "w", encoding="utf-8") as f:
        json.dump(stage_data, f, indent=2)
    logging.info(f"Successfully filled stage.json at {stage_json_path}")

def verify_config_file(config_file_path):
    """
    Verifies that the config file exists and contains the required options.
    Raises an exception if the file is not found or if any required option is missing.
    """
    if not os.path.isfile(config_file_path):
        raise Exception(f"Config file not found: {config_file_path}")

    config = configparser.ConfigParser()
    config.read(config_file_path)

    required_options = [
        ("SERVER", "base_url"),
        ("SERVER", "staging_dir"),
        ("SERVER", "published_dir"),
        ("PAGE", "item_per_page")
    ]

    for section, option in required_options:
        if not config.has_section(section) or not config.has_option(section, option):
            raise Exception(f"Missing configuration: {section}.{option}")

    return config

if __name__ == "__main__":
    try:
        # Load configuration
        config = verify_config_file("config.ini")
        staging_dir = config["SERVER"]["staging_dir"]

        # Fill stage.json
        fill_stage_json(staging_dir)

        logging.info("Successfully filled stage.json.")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
