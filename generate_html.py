import os
import configparser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_sample_html(staging_dir, num_files=7):
    """
    Generates sample HTML files in the specified staging directory.
    """
    for i in range(1, num_files + 1):
        filename = f"sample{i}.html"
        filepath = os.path.join(staging_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"<html><head><title>Sample {i} Title</title></head><body><h1>Sample {i} Post Name</h1><h1>Sample {i} Content</h1></body></html>")
            logging.info(f"Generated {filepath}")
        except Exception as e:
            logging.error(f"Error generating {filepath}: {e}", exc_info=True)
            break

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
        ("SERVER", "staging_dir"),
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

        # Generate sample HTML files
        generate_sample_html(staging_dir)

        logging.info("Completed")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)