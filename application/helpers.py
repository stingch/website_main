# Helper functions

import requests
import json
import os

from config import TEXT_PATH


def is_active(current_path:str, nav_path:str) -> str:
    """Returns a string that shows which page is active in the navigation menu."""

    if current_path == nav_path:
        return "is-active"
    
    return ""


def read_description(file_path:str) -> list:
    """Returns the content of a text file as a list of strings where each string is a paragraph."""

    content = []

    try:
        with open(file_path) as file:
            current_paragraph = ""

            # Loop over each line
            for line in file:
                # Check if the line is blank (i.e. contains only white spaces)
                if line.strip() == "":
                    # If so, add the current paragraph to the list and reset current paragraph
                    content.append(current_paragraph)
                    current_paragraph = ""
                # If line is not blank, add it to the current paragraph
                else:
                    current_paragraph += line

            # Add the final paragraph to the list
            if current_paragraph != "":
                content.append(current_paragraph)
    except FileNotFoundError:
        print(f"ERROR! File could not be found for path: {file_path}.")
    except Exception as error:
        print(f"ERROR! {error}.")

    return content


def get_skills(file_path:str) -> tuple:
    """Returns three lists one for each type of cards in the JSON file."""

    try:
        with open(file_path) as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"ERROR! File could not be found for path: {file_path}.")
    except json.JSONDecodeError as error:
        print(f"ERROR! {error}.")
    except Exception as error:
        print(f"ERROR! {error}.")

    # Storing the information based on the type of card
    languages = [card for card in data["cards"] if card["type"] == "language"]
    frameworks = [card for card in data["cards"] if card["type"] in ["library", "framework"]]
    technologies = [card for card in data["cards"] if card["type"] == "technology"]

    return languages, frameworks, technologies


def get_repositories() -> list:
    """Returns a list of dictionaries which contains information about each public repository on my GitHub profile."""

    github_token = os.getenv("GITHUB_ACCESS")

    url = "https://api.github.com/users/stingch/repos"
    params = {"per_page": 1000}
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = json.loads(response.text)

            repo_list = []

            # Iterate through each repository and add the information needed to the list
            for repo in data:
                # Retrieve information only for non-forked repositories
                if not repo["fork"]:
                    # Check for the README repository so it won't be included
                    if "BogdanOtava" not in repo["name"]:
                        repo_info = {}
                        repo_info["name"] = repo["name"]
                        repo_info["description"] = repo["description"]
                        repo_info["url"] = repo["html_url"]

                        try:
                            # Get all languages used in the repository
                            languages = repo["languages_url"]
                            # Use authentication headers to avoid API rate limit
                            languages_response = requests.get(languages, headers=headers)
                            languages_data = languages_response.json()
                            if isinstance(languages_data, dict) and "message" not in languages_data:
                                sorted_languages = sorted(languages_data.items(), key=lambda x: x[1], reverse=True)
                                # Get top three most used languages in repository
                                top_languages = [lang[0] for lang in sorted_languages[:3]]
                            else:
                                top_languages = []
                        except Exception as e:
                            print(f"Error fetching languages for {repo['name']}: {e}")
                            top_languages = []
                            
                        repo_info["languages"] = top_languages

                        # Add the repository dictionary to the list of repositories
                        repo_list.append(repo_info)

            return repo_list
        else:
            print(f"ERROR! {response.status_code} - {response.reason}.")
            return []
    except Exception as error:
        print(f"ERROR! {error}.")
        return []


def get_language_image(language:str) -> str:
    """Returns the image of a programming language from 'skills.json'."""

    try:
        with open(f"{TEXT_PATH}/skills.json") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        print(f"ERROR! {error}.")
    else:
        for card in data.get("cards", []):
            if card.get("type") == "language" and card.get("title", "").lower() == language.lower():
                return card.get("image")

# ==========================================
# OpenAI 整合功能（文字助理與圖片生成）
# ==========================================
import os
from openai import OpenAI
from dotenv import load_dotenv

# 載入本機 .env 環境變數檔（本機測試用）
load_dotenv()

def get_openai_client():
    """惰性初始化 OpenAI 客戶端以避免啟動時因缺少 Key 而崩潰"""
    return OpenAI()

def ask_ai(prompt):
    """呼叫 OpenAI GPT-4o-mini 進行對話"""
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o-mini",
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI Chat: {e}")
        return f"文字助手發生錯誤：{e}"

def generateImg(prompt, size):
    """呼叫 OpenAI 產生圖片 (配合學校特定/代理 API 伺服器的 gpt-image-1 模型與 base64 格式)"""
    try:
        client = get_openai_client()
        response = client.images.generate(
            model="gpt-image-1", 
            prompt=prompt,
            n=1,
            size=size,
            quality="medium"
        )
        image_base64 = response.data[0].b64_json
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print(f"Error calling OpenAI Image: {e}")
        return None