import os
import requests
from bs4 import BeautifulSoup


default_url = 'https://www.debian.org/'
url = 'https://www.debian.org/News/'

response = requests.get(url)
response.raise_for_status()  # Raise an exception if the request fails

soup = BeautifulSoup(response.content, 'html.parser')

soup2 = BeautifulSoup(response.content, 'html.parser')

def all_links_modifier(link):
    """
        Modifies all the links in the page as expected
    """
    other_links = ['news', 'press/', 'project/', 'awards']

    if link.startswith("../"):
        return default_url + link[3:]
    elif link.startswith("index") or any(link.startswith(str(year)+'/') for year in range(2023, 1996, -1)) or link in other_links:
        return f' {url + link} '
    elif link == '/':
        return f' {default_url} '
    else:
        return f' {link} '



def extract_languages():
    '''
        Generate the Markdown language content with embedded links
    '''
    language_links = soup2.find('div', {'id': 'langContainer'}).find_all('a')
    
    markdown_content = "***\n\n This page is also available in the following languages:\n"
    default_language_link = soup2.find('a', href='../intro/cn')['href']
    default_language_link = default_url + default_language_link[3:]
    markdown_content += f"\n\nHow to set [the default document language]({default_language_link})"

    for link in language_links:
        language_name = link.get_text()
        language_url = link['href']
        language_url = all_links_modifier(language_url)
        markdown_content += f" \n\n [{language_name}]({language_url})\n"

    return markdown_content


def extract_footer():
    '''
        Extract and format the footermap content
    '''
    footermap = soup2.find('div', id='footermap')
    footer_links = footermap.find_all('a')

    formatted_footer = ''
    for link in footer_links:
        link_text = link.get_text(strip=True)
        href = link['href']
        href = all_links_modifier(href)
        formatted_footer += f' \n\n [{link_text}]({href})\n'

    return formatted_footer


title = soup.find(href="2023/")

with open('debian_news.md', 'w') as f:
    f.write(f'# {title.get_text(strip=True)}\n\n')



def extract_text_with_links(element):
    text = ''

    for item in element:

        if isinstance(item, str):
            text += item.strip()

            if text == 'Latest News':
                text = ''
        elif item.name == 'a':
            link_text = item.get_text(strip=True)
            href = item['href']
            href = all_links_modifier(href)
            text += f'[{link_text}]({href})'
            if text == "[Skip Quicknav]( #content )":
                text = ''


    return text
    




def extract_paragraphs(languages, footers):
    '''
        Find all <p> elements
        Initialize an empty list to store the formatted text
    '''

    paragraphs = soup.find_all('p')


    formatted_text = []
    

    executed = False
    for paragraph in paragraphs:

        text = extract_text_with_links(paragraph)

        if text.startswith("Back to the[Debian Project homepage]") and executed == False:
            text = f"*** \n Back to the[Debian Project homepage]({default_url})."
            text += f'\n {languages} \n *** \n\n {footers}'
            executed = True

        formatted_text.append(text)
        

    formatted_output = '\n\n'.join(formatted_text)

    return formatted_output


languages_content = extract_languages()

footer_content = extract_footer()

formatted_output = extract_paragraphs(languages_content, footer_content)


# Extract and print <tt>, <strong><a>, and href content side by side
tt_elements = soup.find_all('tt')
strong_elements = soup.find_all('strong')

def save_to_markdown_file(paragraph_output):

    parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    file_path = os.path.join(parent_dir_path, 'debian_news.md')

    with open(file_path , 'a') as f:
        for tt, strong in zip(tt_elements, strong_elements):
            tt_content = tt.get_text(strip=True)
            strong_content = strong.a.get_text(strip=True)
            href = strong.a['href']
            href = all_links_modifier(href)
            f.write(f'{tt_content} [{strong_content}]({href})\n<br>\n')
        f.write('***')

        f.write(f'{paragraph_output}')
        print("Content saved to 'debian_news.md'")
        f.close()


if __name__ == "__main__":
    try:
        save_to_markdown_file(formatted_output)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the HTTP request: {e}")
    except Exception as e:
        error_message = str(e)
        print(f"An unexpected error occurred: {error_message}")




