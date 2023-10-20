"""
    Methods that help in scraping the data from debian wiki

"""

import os

import requests
from bs4 import BeautifulSoup

DEFAULT_URL = "https://www.debian.org/"
URL = "https://www.debian.org/News/"

response = requests.get(URL, timeout=(3, 5))

try:
    response.raise_for_status()
except requests.exceptions.HTTPError as http_error:
    print(f"HTTP error occurred: {http_error}")
except requests.exceptions.Timeout as timeout_error:
    print(f"Request timed out: {timeout_error}")
except requests.exceptions.RequestException as request_error:
    print(f"An error occurred during the HTTP request: {request_error}")

soup = BeautifulSoup(response.content, "html.parser")

soup2 = BeautifulSoup(response.content, "html.parser")

title = soup.find(href="2023/")

# Extract and print <tt>, <strong><a>, and href content side by side
tt_elements = soup.find_all("tt")
strong_elements = soup.find_all("strong")


def all_links_modifier(link):
    """
    Modifies all the links in the page as expected
    """
    other_links = ["news", "press/", "project/", "awards"]

    if link.startswith("../"):
        return DEFAULT_URL + link[3:]
    if (
        link.startswith("index")
        or any(link.startswith(str(year) + "/") for year in range(2023, 1996, -1))
        or link in other_links
    ):
        return f" {URL + link} "
    if link == "/":
        return f" {DEFAULT_URL} "
    return f" {link} "


def extract_languages():
    """
    Generate the Markdown language content with embedded links
    """
    language_links = soup2.find("div", {"id": "langContainer"}).find_all("a")

    markdown_content = (
        "***\n\n This page is also available in the following languages:\n"
    )
    default_language_link = soup2.find("a", href="../intro/cn")["href"]
    default_language_link = DEFAULT_URL + default_language_link[3:]
    markdown_content += (
        f"\n\nHow to set [the default document language]({default_language_link})"
    )

    for link in language_links:
        language_name = link.get_text()
        language_url = link["href"]
        language_url = all_links_modifier(language_url)
        markdown_content += f" \n\n [{language_name}]({language_url})\n"

    return markdown_content


def extract_footer():
    """
    Extract and format the footermap content
    """
    footermap = soup2.find("div", id="footermap")
    footer_links = footermap.find_all("a")

    formatted_footer = ""
    for link in footer_links:
        link_text = link.get_text(strip=True)
        href = link["href"]
        href = all_links_modifier(href)
        formatted_footer += f" \n\n [{link_text}]({href})\n"

    return formatted_footer


with open("debian_news.md", "w", encoding="UTF-8") as f:
    f.write(f"# {title.get_text(strip=True)}\n\n")


def extract_text_with_links(element):
    """
    extracts texts that have links
    """
    text = ""

    for item in element:
        if isinstance(item, str):
            text += item.strip()

            if text == "Latest News":
                text = ""
        elif item.name == "a":
            link_text = item.get_text(strip=True)
            href = item["href"]
            href = all_links_modifier(href)
            text += f"[{link_text}]({href})"
            if text == "[Skip Quicknav]( #content )":
                text = ""

    return text


def extract_paragraphs(languages, footers):
    """
    Find all <p> elements
    Initialize an empty list to store the formatted text
    """

    paragraphs = soup.find_all("p")

    formatted_text = []

    executed = False
    for paragraph in paragraphs:
        text = extract_text_with_links(paragraph)

        if (
            text.startswith("Back to the[Debian Project homepage]")
            and executed is False
        ):
            text = f"*** \n Back to the[Debian Project homepage]({DEFAULT_URL})."
            text += f"\n {languages} \n *** \n\n {footers}"
            executed = True

        formatted_text.append(text)

    formatted_output = "\n\n".join(formatted_text)

    return formatted_output


def save_to_markdown_file(paragraph_output):
    """
    save the content into a markdown file
    """
    parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    file_path = os.path.join(parent_dir_path, "debian_news.md")

    with open(file_path, "a", encoding="UTF-8") as file:
        for tt_item, strong in zip(tt_elements, strong_elements):
            tt_content = tt_item.get_text(strip=True)
            strong_content = strong.a.get_text(strip=True)
            href = strong.a["href"]
            href = all_links_modifier(href)
            file.write(f"{tt_content} [{strong_content}]({href})\n<br>\n")
        file.write("***")

        file.write(f"{paragraph_output}")
        print("Content saved to 'debian_news.md'")
        file.close()


if __name__ == "__main__":
    try:
        languages_content = extract_languages()
        footer_content = extract_footer()
        FORMATTED_OUTPUT_CONTENT = extract_paragraphs(languages_content, footer_content)
        save_to_markdown_file(FORMATTED_OUTPUT_CONTENT)
    except Exception as e:  # pylint: disable=broad-except
        ERROR_MESSAGE = str(e)
        print(f"An unexpected error occurred: {ERROR_MESSAGE}")
