import requests
from bs4 import BeautifulSoup

url = 'https://www.debian.org/News/'

response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')


title = soup.find(href="2023/")

with open('debian_news.md', 'w') as f:
    f.write(f'# {title.get_text(strip=True)}\n\n')


def extract_text_with_links(element):
    text = ''
    for item in element.contents:
        if isinstance(item, str):
            text += item.strip()
        elif item.name == 'a':
            link_text = item.get_text(strip=True)
            href = item['href']
           
            text += f'[{link_text}]({href})'
    return text


def extract_languages():
    '''
        Generate the Markdown language content with embedded links
    '''
    language_links = soup.find('div', {'id': 'langContainer'}).find_all('a')

    
    markdown_content = "***\n\n This page is also available in the following languages:\n"
    default_language_link = soup.find('a', href='../intro/cn')['href']
    markdown_content += f"\n\nHow to set [the default document language]({default_language_link})"


    for link in language_links:
        language_name = link.get_text()
        language_url = link['href']
        markdown_content += f" \n\n [{language_name}]({language_url})\n"

    return markdown_content


def extract_footer():
    '''
        Extract and format the footermap content
    '''
    footermap = soup.find('div', id='footermap')
    footer_links = footermap.find_all('a')

    formatted_footer = ''
    for link in footer_links:
        link_text = link.get_text(strip=True)
        href = link['href']
        formatted_footer += f'\n\n [{link_text}]({href})'
        
    return formatted_footer


def extract_paragraphs():
    '''
        Find all <p> elements
        Initialize an empty list to store the formatted text
    '''
    
    paragraphs = soup.find_all('p')

    formatted_text = []

    executed = False
    for paragraph in paragraphs:
        text = extract_text_with_links(paragraph)
        if text == "[Skip Quicknav](#content)" or text == "Latest News":
            text = ''
        if text == "Back to the[Debian Project homepage](../)." and executed == False:
            text = "***\n\n Back to the[Debian Project homepage](../)."
            text += f'\n\n {extract_languages()} \n\n *** \n\n {extract_footer()}'
            executed = True

        formatted_text.append(text)

    formatted_output = '\n\n'.join(formatted_text)

    return formatted_output


# Extract and print <tt>, <strong><a>, and href content side by side
tt_elements = soup.find_all('tt')
strong_elements = soup.find_all('strong')

def save_to_markdown_file():
    with open('debian_news.md', 'a') as f:
        for tt, strong in zip(tt_elements, strong_elements):
            tt_content = tt.get_text(strip=True)
            strong_content = strong.a.get_text(strip=True)
            href = strong.a['href']
            f.write(f'{tt_content} [{strong_content}]({url+href})\n\n')
        f.write('***\n\n')

        f.write(f'{extract_paragraphs()}')
        print("Content saved to 'debian_news.md'")
        f.close()

save_to_markdown_file()