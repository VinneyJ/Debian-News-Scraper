"""
    Methods that help in scraping the data from debian wiki

"""

import os

import requests
from bs4 import BeautifulSoup


def response_status(response):
    """
    checks the response status of the request url
    """
    # print(response)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        print(f"HTTP error occurred: {http_error}")
    except requests.exceptions.Timeout as timeout_error:
        print(f"Request timed out: {timeout_error}")
    except requests.exceptions.RequestException as request_error:
        print(f"An error occurred during the HTTP request: {request_error}")


def all_links_modifier(link, default_url, url):
    """
    Modifies all the links in the page as expected
    """
    other_links = ["news", "press/", "project/", "awards"]

    if link.startswith("../"):
        return default_url + link[3:]
    if (
        link.startswith("index")
        or any(link.startswith(str(year) + "/") for year in range(2023, 1996, -1))
        or link in other_links
    ):
        return f" {url + link} "
    if link == "/":
        return f" {default_url} "
    return f" {link} "


def extract_languages(soup2, default_url, url):
    """
    Generate the Markdown language content with embedded links
    """
    language_links = soup2.find("div", {"id": "langContainer"}).find_all("a")

    markdown_content = (
        "***\n\n This page is also available in the following languages:\n"
    )
    default_language_link = soup2.find("a", href="../intro/cn")["href"]
    default_language_link = default_url + default_language_link[3:]
    markdown_content += (
        f"\n\nHow to set [the default document language]({default_language_link})"
    )

    for link in language_links:
        language_name = link.get_text()
        language_url = link["href"]
        language_url = all_links_modifier(language_url, default_url, url)
        markdown_content += f" \n\n [{language_name}]({language_url})\n"

    return markdown_content


def extract_footer(soup2, defaul_url, url):
    """
    Extract and format the footermap content
    """
    footermap = soup2.find("div", id="footermap")
    footer_links = footermap.find_all("a")

    formatted_footer = ""
    for link in footer_links:
        link_text = link.get_text(strip=True)
        href = link["href"]
        href = all_links_modifier(href, defaul_url, url)
        formatted_footer += f" \n\n [{link_text}]({href})\n"

    return formatted_footer


def extract_text_with_links(element, default_url, url):
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
            href = all_links_modifier(href, default_url, url)
            text += f"[{link_text}]({href})"
            if text == "[Skip Quicknav]( #content )":
                text = ""

    return text


def extract_paragraphs(languages, footers, soup, default_url, url):
    """
    Find all <p> elements
    Initialize an empty list to store the formatted text
    """

    paragraphs = soup.find_all("p")

    formatted_text = []

    executed = False
    for paragraph in paragraphs:
        text = extract_text_with_links(paragraph, default_url, url)

        if (
            text.startswith("Back to the[Debian Project homepage]")
            and executed is False
        ):
            text = f"*** \n Back to the[Debian Project homepage]({default_url})."
            text += f"\n {languages} \n *** \n\n {footers}"
            executed = True

        formatted_text.append(text)

    formatted_output = "\n\n".join(formatted_text)

    return formatted_output


def save_to_markdown_file(paragraph_output, soup, default_url, url, file_path):
    """
    save the content into a markdown file
    """
    tt_elements = soup.find_all("tt")
    strong_elements = soup.find_all("strong")

    title = soup.find(href="2023/")
    with open(file_path, "w", encoding="UTF-8") as file:
        file.write(f"# {title.get_text(strip=True)}\n\n")
        for tt_item, strong in zip(tt_elements, strong_elements):
            tt_content = tt_item.get_text(strip=True)
            strong_content = strong.a.get_text(strip=True)
            href = strong.a["href"]
            href = all_links_modifier(href, default_url, url)
            file.write(f"{tt_content} [{strong_content}]({href})\n<br>\n")
        file.write("***")

        file.write(f"{paragraph_output}")
        print("Content saved to 'debian_news.md'")
        file.close()


def process_debian_news(url, default_url):
    """
    Processes the whole debian news content page
    """

    response = requests.get(url, timeout=(3, 5))
    # print(response)

    response_status(response)

    soup = BeautifulSoup(response.content, "html.parser")

    soup2 = BeautifulSoup(response.content, "html.parser")

    # title = soup.find(href="2023/")

    # with open("debian_news.md", "w", encoding="UTF-8") as file:
    #     file.write(f"# {title.get_text(strip=True)}\n\n")

    # Extract and print <tt>, <strong><a>, and href content side by side

    parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    file_path = os.path.join(parent_dir_path, "debian_news.md")

    try:
        languages_content = extract_languages(soup2, default_url, url)
        footer_content = extract_footer(soup2, default_url, url)
        formatted_content = extract_paragraphs(
            languages_content, footer_content, soup, default_url, url
        )
        # print(formatted_content)
        save_to_markdown_file(formatted_content, soup, default_url, url, file_path)
    except Exception as error:  # pylint: disable=broad-except
        error_message = str(error)
        print(f"An unexpected error occurred: {error_message}")


if __name__ == "__main__":
    DEFAULT_URL = "https://www.debian.org/"
    URL = "https://www.debian.org/News/"

    process_debian_news(URL, DEFAULT_URL)
