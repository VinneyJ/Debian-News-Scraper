"""
    Methods that help in testing debian wiki scrapper
"""

import os

from bs4 import BeautifulSoup

from src.scrape_debian import (all_links_modifier, extract_footer,
                               extract_languages, extract_paragraphs,
                               extract_text_with_links, save_to_markdown_file)
from tests.content_file import (extract_footer_link, final_data,
                                format_paragraph_output, languages_output)


def test_all_links_modifier():
    """
    Test all links modifier
    """
    assert all_links_modifier("../some_link") == "https://www.debian.org/some_link"
    assert (
        all_links_modifier("index2023.html/")
        == " https://www.debian.org/News/index2023.html/ "
    )
    assert all_links_modifier("/") == " https://www.debian.org/ "
    assert all_links_modifier("2022/") == " https://www.debian.org/News/2022/ "
    assert all_links_modifier("other_link") == " other_link "


def test_extract_languages():
    """
    test languages extract
    """
    assert extract_languages() == languages_output


def test_extract_footer():
    """
    test footer extraction
    """
    assert extract_footer() == extract_footer_link


def test_extract_text_with_links():
    """
    test text with links extraction
    """
    html = '<p><a href="https://bits.debian.org">Bits from Debian</a></p>'
    soup = BeautifulSoup(html, "html.parser")
    paragraph1 = soup.find("p")

    result = extract_text_with_links(paragraph1)
    expected_result = "[Bits from Debian]( https://bits.debian.org )"
    assert result == expected_result


def test_extract_paragraphs():
    """
    test paragraph extraction
    """
    result = extract_paragraphs(languages_output, extract_footer_link)

    assert result == format_paragraph_output


def test_save_to_markdown_file():
    """
    test save to markdown file
    """
    save_to_markdown_file(format_paragraph_output)

    parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    file_path = os.path.join(parent_dir_path, "debian_news.md")
    with open(file_path, "r", encoding="UTF-8") as f:
        markdown_contents = f.read()

    assert markdown_contents == final_data
