# Sets up the routes for all the pages

from flask import Flask, render_template, request, make_response
from flask_caching import Cache
from config import TEMPLATES_PATH, TEXT_PATH
from application.helpers import *


app = Flask(__name__, template_folder=TEMPLATES_PATH)
app.jinja_env.filters["is_active"] = is_active
app.jinja_env.filters["get_language_image"] = get_language_image

app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = 3600
cache = Cache(app)


@app.route("/")
def loading():
    """Renders the 'Loading' page of the website."""

    #response = make_response(render_template("loading.html"))
    #response.headers["Cache-Control"] = "public, max-age=3"

    #return response
    return render_template("home.html")


@app.route("/home")
@cache.cached()
def home():
    """Renders the 'Home' page of the website."""

    return render_template("home.html")


@app.route("/about")
@cache.cached()
def about():
    """Renders the 'About Me' page of the website."""

    content = read_description(f"{TEXT_PATH}/about.txt")

    return render_template("about.html", content=content)


@app.route("/skills")
@cache.cached()
def skills():
    """Renders the 'Skills' page of the website."""

    skills = get_skills(f"{TEXT_PATH}/skills.json")

    return render_template("skills.html", skills=skills)


@app.route("/portfolio")
@cache.cached()
def portfolio():
    """Renders the 'Portfolio' page of the website."""

    repos = get_repositories()

    return render_template("portfolio.html", repos=repos)


@app.route("/contact", methods=["GET", "POST"])
@cache.cached()
def contact():
    """Renders the 'Contact' page of the website."""

    # User reached route via POST
    if request.method == "POST":
        return render_template("result.html")

    # User reached route via GET
    return render_template("contact.html")


@app.route("/result")
@cache.cached()
def result():
    """Renders the 'Result' page of the website."""

    return render_template("result.html")

# ==========================================
# 新增的 AI 應用路由
# ==========================================

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """AI 文字助理路由"""
    response_text = None
    if request.method == "POST":
        prompt = request.form.get("prompt")
        if prompt:
            response_text = ask_ai(prompt)
            
    return render_template("chat.html", response=response_text)


@app.route("/image_gen", methods=["GET", "POST"])
def image_gen():
    """AI 圖片生成路由"""
    img_url = None
    prompt = None
    if request.method == "POST":
        prompt = request.form.get("prompt")
        size = request.form.get("size")
        if prompt and size:
            img_url = generateImg(prompt, size)
            
    return render_template("image_generator.html", imgUrl=img_url, prompt=prompt)