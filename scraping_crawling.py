import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. book dataset load
current_dir = os.path.dirname(__file__)
data_path = os.path.join(current_dir, "../project_dataset/books/books.csv")

books_data = pd.read_csv(data_path)

# 2. scraping / crawling function
def get_genre_for_book(book_title):
    if not book_title:
        return None
    
    base_url = "https://www.goodreads.com/search?q="
    search_url = f"{base_url}{book_title.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    try:
        # 검색 페이지 요청
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")

        # 검색 결과에서 첫 번째 책 링크 찾기
        first_book = soup.find("a", class_="bookTitle")
        if not first_book:
            return None

        # 정확한 책 페이지 URL로 이동
        book_url = "https://www.goodreads.com" + first_book['href']
        book_page = requests.get(book_url, headers=headers)
        if book_page.status_code != 200:
            return None
        book_soup = BeautifulSoup(book_page.text, "html.parser")

        # 장르 정보 추출 (책 페이지에서 장르 가져오기)
        genre_section = book_soup.find_all("span", class_="BookPageMetadataSection__genreButton")
        
        # 장르 목록
        genres = []
        for genre in genre_section:
            genre_link = genre.find("a")
            if genre_link:
                genre_name = genre_link.find("span", class_="Button__labelItem").text.strip()
                genres.append(genre_name)
        
        # 장르 리스트 반환
        return ", ".join(genres) if genres else "No genres found."

    except Exception as e:
        print(f"Error fetching genres for '{book_title}': {e}")
        return None


for index, row in books_data.iterrows():
    book_title = row['original_title']
    
    if pd.isna(book_title):  # 제목이 null인 경우 genre 컬럼에 None 추가
        books_data.at[index, 'genre'] = None  
    else:
        genre = get_genre_for_book(book_title)  # 책 제목에 맞는 장르 크롤링
        
        if genre == "No genres found.":  # 장르를 찾을 수 없는 경우 genre 컬럼에 None 추가
            books_data.at[index, 'genre'] = None  
        else:
            books_data.at[index, 'genre'] = genre  # 해당 행의 genre 컬럼에 장르 추가

    print(f"Book: {book_title}, Genre: {genre}")

# 크롤링 결과를 CSV 파일로 저장
books_data.to_csv("books_with_genres.csv", index=False)

