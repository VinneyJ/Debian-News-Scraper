
# Scrape Debian Wiki News

Scrape Debian Wiki News is a Python script that retrieves content from the Debian Wiki's News page and converts it into Markdown format.

## Installation

1. Clone the repository using Git:

```
    git clone git@github.com:VinneyJ/Debian-News-Scraper.git
```

2. Navigate to the project folder.



3. Create a virtual environment using [virtualenv](https://pypi.org/project/virtualenv/).


4. Activate the virtual environment:
- On macOS and Linux:
  ```
    source venv/bin/activate
  ```
- On Windows:
  ```
    venv\Scripts\activate
  ```

5. Install the required dependencies using pip:

```
    pip install -r requirements.txt
```

6. Install the current directory as an editable package.

```
  pip install -e .
```

## Usage

After setting up the project and installing the dependencies, you can run the script as follows:



```
    python3 src/scrape_debian.py
```

This will execute the script, scrape the Debian Wiki News page, and save the content in Markdown format.
## Testing

You can run the provided tests to ensure the script's functionality:

```
    pytest tests -vv
```


## Questions

If you have any questions or need assistance, please don't hesitate to reach out. Thank you for using Scrape Debian Wiki News!