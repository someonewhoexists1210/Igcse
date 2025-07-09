# paper.py (with real-time progress tracking)
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger
import io
import requests
import re

BASE_URL = "https://pastpapers.papacambridge.com/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def get_subject_link(code):
    response = requests.get(BASE_URL + "papers/caie/igcse", headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all("div", class_="kt-widget4__item item-folder-type")
    for div in divs:
        if code in div.get_text():
            link_tag = div.find('a')
            if link_tag and link_tag.has_attr('href'):
                return requests.compat.urljoin(BASE_URL, link_tag['href'])
    return None


def get_subpages(subject_url, years_start):
    response = requests.get(subject_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    elements = []
    for el in soup.find_all(class_='kt-widget4__item item-folder-type'):
        a = el.find('a', href=True)
        if a:
            text = a.get_text()
            match = re.search(r'(20\d{2}|19\d{2})', text)
            if match:
                year = int(match.group(0))
                if year < years_start:
                    continue
            elements.append(el)
    for el in elements:
        a = el.find('a', href=True)
        if a:
            links.append(requests.compat.urljoin(BASE_URL, a['href']))
    links = list(set(links))
    links.sort(reverse=True)
    return links[2:17]


async def fetch_page(session, url):
    async with session.get(url, headers=HEADERS) as response:
        return await response.text()


async def fetch_pdf(session, url):
    async with session.get(url, headers=HEADERS) as response:
        return await response.read()


async def gather_pdf_links(code, papers, variants, years_start, progress_callback):
    progress_callback(5, "Fetching subject page")
    subject_url = get_subject_link(code)
    if not subject_url:
        return []

    progress_callback(10, "Gathering subpages")
    subpages = get_subpages(subject_url, years_start)

    progress_callback(20, "Downloading subpage HTML")
    async with aiohttp.ClientSession() as session:
        subpage_htmls = await asyncio.gather(*(fetch_page(session, link) for link in subpages))

    progress_callback(30, "Scanning for PDF links")
    pdf_links = []
    seen = set()

    for html in subpage_htmls:
        soup = BeautifulSoup(html, 'html.parser')
        for paper in papers:
            count = 0
            for a in soup.find_all("a", href=True):
                href = a['href']
                if href.endswith(".pdf") and "qp" in href.lower() and count < 3 and href[-6] == paper and href[-5] in variants:
                    full_url = requests.compat.urljoin(BASE_URL, href)
                    if full_url not in seen:
                        seen.add(full_url)
                        pdf_links.append(full_url)
                        count += 1

    progress_callback(40, f"Found {len(pdf_links)} PDFs. Starting download...")
    return pdf_links


async def download_pdfs_async(pdf_links, progress_callback):
    merger = PdfMerger()
    async with aiohttp.ClientSession() as session:
        total = len(pdf_links)
        for i, url in enumerate(pdf_links):
            content = await fetch_pdf(session, url)
            merger.append(io.BytesIO(content))
            percent = 40 + int((i + 1) / total * 40)
            progress_callback(percent, f"Downloaded {i + 1}/{total} PDFs")

    progress_callback(85, "Merging PDFs")
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    progress_callback(100, "Completed")
    return output.getvalue()


def get_paper_pdf(code, papers, variants, years_start, progress_callback):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    pdf_links = loop.run_until_complete(gather_pdf_links(code, papers, variants, years_start, progress_callback))
    pdf_data = loop.run_until_complete(download_pdfs_async(pdf_links, progress_callback))
    return pdf_data
