"""
    Methods that help in testing debian wiki scrapper
"""
import os


import requests
from bs4 import BeautifulSoup
import pytest

from src.scrape_debian import (
    all_links_modifier,
    extract_footer,
    extract_languages,
    extract_paragraphs,
    extract_text_with_links,
    process_debian_news,
    response_status,
    save_to_markdown_file,
)
from tests.content_file import (
    extract_footer_link,
    format_paragraph_output,
    languages_output,
)


@pytest.mark.parametrize(
    "status_code, expected_exception",
    [(200, None), (404, requests.exceptions.HTTPError)],
)
def test_response_status(status_code, expected_exception):
    """
    Test url Connection
    """
    url = "https://www.debian.org/News/"
    response = requests.get(url, timeout=(3, 5))

    response.status_code = status_code

    response_status(response)
    if status_code == 200 and not expected_exception:
        assert response.status_code == 200
    else:
        assert response.status_code == 404


def test_all_links_modifier():
    """
    Test all links modifier
    """
    default_url = "https://www.debian.org/"
    url = "https://www.debian.org/News/"

    # Test relative link
    link1 = "../some_link"
    assert (
        all_links_modifier(link1, default_url, url)
        == f"https://www.debian.org/{link1[3:]}"
    )

    # Test absolute link
    link2 = "https://example.com/absolute_link"
    assert (
        all_links_modifier(link2, default_url, url)
        == " https://example.com/absolute_link "
    )

    # Test links that should not be modified
    link3 = "index2023.html/"
    assert (
        all_links_modifier(link3, default_url, url)
        == " https://www.debian.org/News/index2023.html/ "
    )

    link4 = "/"
    assert all_links_modifier(link4, default_url, url) == " https://www.debian.org/ "

    link5 = "other_link"
    assert all_links_modifier(link5, default_url, url) == " other_link "


def test_extract_languages():
    """
    test languages extract
    """

    default_url = "https://www.debian.org/"
    url = "https://www.debian.org/News/"

    response = requests.get(url, timeout=(3, 5))
    soup2 = BeautifulSoup(response.content, "html.parser")

    result = extract_languages(soup2, default_url, url)

    assert result == languages_output


def test_extract_footer():
    """
    test footer extraction
    """
    default_url = "https://www.debian.org/"
    url = "https://www.debian.org/News/"

    response = requests.get(url, timeout=(3, 5))
    soup2 = BeautifulSoup(response.content, "html.parser")

    result = extract_footer(soup2, default_url, url)

    assert result == extract_footer_link


def test_extract_text_with_links():
    """
    test text with links extraction
    """

    default_url = "https://www.debian.org/"
    url = "https://www.debian.org/News/"

    html = '<p><a href="https://bits.debian.org">Bits from Debian</a></p>'
    soup = BeautifulSoup(html, "html.parser")

    paragraph1 = soup.find("p")

    result = extract_text_with_links(paragraph1, default_url, url)
    expected_result = "[Bits from Debian]( https://bits.debian.org )"

    assert result == expected_result


def test_extract_paragraphs():
    """
    test paragraph extraction
    """

    default_url = "https://www.debian.org/"
    url = "https://www.debian.org/News/"

    response = requests.get(url, timeout=(3, 5))
    soup = BeautifulSoup(response.content, "html.parser")

    result = extract_paragraphs(
        languages_output, extract_footer_link, soup, default_url, url
    )

    assert result == format_paragraph_output


def test_save_to_markdown_file():
    """
    test save to markdown file
    """

    parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    file_path_test = os.path.join(parent_dir_path, "test_file.md")

    default_url = "https://www.debian.org/"
    url = "https://www.debian.org/News/"

    response = requests.get(url, timeout=(3, 5))
    soup = BeautifulSoup(response.content, "html.parser")

    # Call the function
    save_to_markdown_file(
        format_paragraph_output, soup, default_url, url, file_path_test
    )

    # Define file path for testing
    parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    file_path = os.path.join(parent_dir_path, "debian_news.md")

    # Read the content of the file
    with open(file_path_test, "r", encoding="UTF-8") as file:
        saved_content_test = file.read()

    with open(file_path, "r", encoding="UTF-8") as file:
        original_saved_content = file.read()

    # print(saved_content)
    assert saved_content_test == original_saved_content

    # Clean up the temporary directory
    os.remove(file_path_test)


if __name__ == "__main__":
    DEFAULT_URL = "https://www.debian.org/"
    URL = "https://www.debian.org/News/"
    process_debian_news(URL, DEFAULT_URL)
