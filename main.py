import redis

from flask import Flask, render_template, request, flash

app = Flask(__name__)

app.secret_key = 'key'

r = redis.Redis()

last_id = 0


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        global last_id
        req = request.form
        name = req["full_name"]
        data = req['data']
        last_id = r.get('last_id')
        if last_id is None:
            last_id = 1
        else:
            last_id = int(last_id) + 1

        r.set("news:name:{0}".format(last_id), name)
        r.set("news:post:{0}".format(last_id), data)
        r.set("last_id", last_id)
        r.lpush("post_id", last_id)
        flash("Successfully created post", category="success")

    return render_template("home.html")


@app.route("/all")
def all_posts():
    post_ids = r.lrange('post_id', 0, -1)
    posts = dict()
    for post_id in post_ids:
        name = r.get("news:name:{0}".format(post_id.decode('utf-8'))).decode('utf-8')
        post_data = r.get("news:post:{0}".format(post_id.decode('utf-8'))).decode('utf-8')
        posts[name] = post_data
    return render_template("all.html", posts=posts)


@app.route('/latest')
def latest_posts():
    post_ids = r.lrange('post_id', 0, 2)
    posts = dict()
    for post_id in post_ids:
        name = r.get("news:name:{0}".format(post_id.decode('utf-8'))).decode('utf-8')
        post_data = r.get("news:post:{0}".format(post_id.decode('utf-8'))).decode('utf-8')
        posts[name] = post_data
    return render_template("latest.html", posts=posts)


app.run()
