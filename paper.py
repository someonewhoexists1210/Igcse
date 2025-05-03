import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger
import io
import time

def get_paper_pdf(code, papers, variants):
    # Base URL
    base_url = "https://pastpapers.papacambridge.com/"

    # Headers to mimic a browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(base_url + "papers/caie/igcse", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    divs = soup.find_all("div", class_="kt-widget4__item item-folder-type")
    for div in divs:
        if code in div.get_text():
            linkh = div.find('a')
            if linkh and linkh.has_attr('href'):
                linkh = linkh['href']

    # Step 1: Fetch the main page
    response = requests.get(requests.compat.urljoin(base_url, linkh), headers=headers)
    subject_soup = BeautifulSoup(response.text, 'html.parser')

    # Step 2: Find all subpage links
    subpage_links = []
    elements = subject_soup.find_all(class_='kt-widget4__item item-folder-type')
    for element in elements:
        a_tag = element.find('a', href=True)
        href = a_tag['href']
        subpage_links.append(requests.compat.urljoin(base_url, href))
        
    subpage_links = list(set(subpage_links))
    subpage_links.sort(reverse=True)
    subpage_links = subpage_links[2:17]
    for link in subpage_links:
        print(f"Subpage link: {link}")


    pdf_links = []

    for paper in papers:
        for link in subpage_links:
            res = requests.get(link, headers=headers)
            sub_soup = BeautifulSoup(res.text, 'html.parser')
            count = 0
            for a in sub_soup.find_all("a", href=True):
                pdf_url = a['href']
                if pdf_url.endswith('.pdf') and "qp" in pdf_url.lower() and count < 3 and pdf_url[-6] == paper and pdf_url[-5] in variants:
                    count += 1
                    print(f"Found PDF link: {pdf_url}")
                    full_pdf_url = requests.compat.urljoin(base_url, pdf_url)
                    if full_pdf_url not in pdf_links:
                        print(f"Adding PDF link: {full_pdf_url}")
                        pdf_links.append(full_pdf_url)
        
        time.sleep(1)  # Be polite to the server

    merger = PdfMerger()

    for url in pdf_links:
        print(f"Downloading: {url}")
        pdf_response = requests.get(url, headers=headers)
        pdf_file = io.BytesIO(pdf_response.content)
        merger.append(pdf_file)
        time.sleep(0.5)  

    output_pdf = io.BytesIO()
    merger.write(output_pdf)
    merger.close()
    output_pdf.seek(0)
    return output_pdf.getvalue()  
