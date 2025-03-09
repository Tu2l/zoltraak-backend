# Zoltraak Backend Directory Structure and JSON Files Documentation

This document describes the directory structure and JSON files used in the Zoltraak backend.

## Top-Level Directories

*   `zoltraak-backend/`: The root directory of the backend project.
*   `zoltraak-backend/staging/`:  This directory is used as a temporary area for new or updated content before it is published.
*   `zoltraak-backend/published/`: This directory contains the final, published content served by the backend.

## `published` Directory Structure

The `published` directory contains the following files and subdirectories:

*   `page.json`:  This file contains a list of categories. Each category points to a subdirectory containing the actual content for that category.
*   `server.json`: This file contains server-wide configuration settings, such as the base URL, the number of items per page, and the location of the `page.json` file.
*   `[category_name]/`:  Subdirectories representing content categories (e.g., `posts1`, `posts2`, etc.). The category name is derived from the `name` field in the `page.json` file.

### Category Subdirectories

Each category subdirectory (e.g., `posts1/`) contains:

*   `page.json`: This file contains metadata for the category, such as the category root, the starting page number, the ending page number, and the total number of pages in the category.
*   `[page_number]/`: Subdirectories representing individual pages within the category (e.g., `1/`).

### Page Subdirectories

Each page subdirectory (e.g., `1/`) contains:

*   `page.json`: This file contains metadata for the page, such as the page root, the current page number, the next page number, and a list of posts on the page.
*   `[content_file].html`: HTML files containing the actual content for each post.

## JSON File Formats

### `published/page.json`

This file contains a JSON array of category objects. Each object has the following structure:

```json
[
  {
    "name": "Category Name",
    "path": "category_name",
    "start_page": 1
  }
]
```

*   `name`: The display name of the category.
*   `path`: The path to the category subdirectory within the `published` directory.
*   `start_page`: The starting page number for the category.

### `published/server.json`

This file contains a JSON object with server configuration settings:

```json
{
  "root": "https://example.com",
  "items_per_page": 10,
  "published_pages": "published/page.json"
}
```

*   `root`: The base URL of the website.
*   `items_per_page`: The number of content items to display on each page.
*   `published_pages`: The path to the `page.json` file.

### `published/[category_name]/page.json`

This file contains a JSON object with category metadata:

```json
{
  "root": "category_name",
  "start_page": 1,
  "end_page": 1,
  "total_pages": 1
}
```

*   `root`: The root name or identifier for the category.
*   `start_page`: The starting page number for the category.
*   `end_page`: The ending page number for the category.
*   `total_pages`: The total number of pages in the category.

### `published/[category_name]/[page_number]/page.json`

This file contains a JSON object with page metadata:

```json
{
  "root": "page_number",
  "current_page": 1,
  "next_page": 2,
  "posts": [
    {
      "path": "content_file.html",
      "topic": "Content Title",
      "thumbnail": "thumbnail.jpg"
    }
  ]
}
```

*   `root`: The root name or identifier for the page.
*   `current_page`: The current page number.
*   `next_page`: The page number of the next page, or `null` if it is the last page.
*   `posts`: An array of post objects, each containing:
    *   `path`: The path to the content file (HTML).
    *   `topic`: The title or topic of the content.
    *   `thumbnail`: The path to the thumbnail image for the content.

## `staging` Directory

The `staging` directory contains files that are not yet published.  The structure is less rigid than the `published` directory.  A key file in this directory is:

*   `stage.json`: This file describes the files in the staging directory and how they should be processed.  It's an array of objects with the following structure:

```json
[
  {
    "filename": "filename.html",
    "thumbnail": "thumbnail.jpg",
    "topic": "About the file content",
    "category": "posts"
  }
]
```

*   `filename`: The name of the HTML file.
*   `thumbnail`: The name of the thumbnail image (optional).
*   `topic`: A brief description of the content.
*   `category`: The category to which the content belongs.  This should match a category `name` in the `published/page.json` file.

This documentation provides a comprehensive overview of the directory structure and JSON files used in the Zoltraak backend. Understanding this structure is crucial for managing and updating the content of the website.
