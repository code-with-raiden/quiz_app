import json
import random
import threading
from pathlib import Path

from flask import Flask, abort, render_template_string, request

BASE_DIR = Path(__file__).parent
QUESTIONS_FILE = BASE_DIR / "questions.json"
ISSUED_FILE = BASE_DIR / "issued.json"
QUESTIONS_PER_STUDENT = 10
MAX_ATTEMPTS = 50

app = Flask(__name__)
lock = threading.Lock()


def load_topics():
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        return json.load(f)["topics"]


def load_issued():
    if ISSUED_FILE.exists():
        with open(ISSUED_FILE, encoding="utf-8") as f:
            return json.load(f)
    # students: who got what | served: how often each question was given
    # sets: signatures of every 10-question set already issued, per topic
    return {"students": {}, "served": {}, "sets": {}}


def save_issued(data):
    tmp = ISSUED_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(ISSUED_FILE)


def pick_questions(topic_key, pool, issued):
    """Pick 10 questions, favouring the least-served ones, never repeating a full set."""
    served = issued["served"].setdefault(topic_key, {})
    used_sets = set(issued["sets"].setdefault(topic_key, []))
    ids = [q["id"] for q in pool]

    for _ in range(MAX_ATTEMPTS):
        ranked = sorted(ids, key=lambda qid: (served.get(qid, 0), random.random()))
        chosen = ranked[:QUESTIONS_PER_STUDENT]
        signature = "|".join(sorted(chosen))
        if signature not in used_sets:
            return chosen, signature

    raise RuntimeError(
        f"No unused 10-question set left for '{topic_key}'. Add more questions to questions.json."
    )


BASE_STYLE = """
<style>
  body { font-family: system-ui, sans-serif; margin: 0; padding: 16px;
         background: #f4f6fb; color: #1d2433; }
  .card { background: #fff; border-radius: 12px; padding: 16px;
          box-shadow: 0 2px 8px rgba(0,0,0,.08); max-width: 560px; margin: 0 auto; }
  h1 { font-size: 1.3rem; margin-top: 0; }
  label { font-size: .95rem; }
  input { width: 100%; padding: 12px; font-size: 1rem; margin: 6px 0 12px;
          border: 1px solid #ccd3e0; border-radius: 8px; box-sizing: border-box; }
  button { width: 100%; padding: 12px; font-size: 1rem; border: none;
           border-radius: 8px; background: #3b5bdb; color: #fff; }
  li { margin-bottom: 14px; line-height: 1.5; }
  .err { color: #c92a2a; }
  a { color: #3b5bdb; }
</style>
"""

INDEX_HTML = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Practice Questions</title>""" + BASE_STYLE + """</head><body><div class="card">
<h1>Choose a topic</h1><ul style="list-style:none;padding:0">
{% for key, t in topics.items() %}
  <li><a href="/topic/{{ key }}">{{ t.title }}</a></li>
{% endfor %}
</ul></div></body></html>
"""

FORM_HTML = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>""" + BASE_STYLE + """</head><body><div class="card">
<h1>{{ title }}</h1>
<form method="post">
  <label>Name</label><input name="name" required value="{{ name }}">
  <label>Roll number</label><input name="roll" required value="{{ roll }}">
  <button type="submit">Get my questions</button>
</form>
{% if error %}<p class="err">{{ error }}</p>{% endif %}
</div></body></html>
"""

RESULT_HTML = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>""" + BASE_STYLE + """</head><body><div class="card">
<h1>{{ title }}</h1>
<p>Hi <strong>{{ name }}</strong>, here are your {{ questions|length }} questions.</p>
<ol>
{% for q in questions %}<li>{{ q }}</li>{% endfor %}
</ol>
</div></body></html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML, topics=load_topics())


@app.route("/topic/<topic_key>", methods=["GET", "POST"])
def topic(topic_key):
    topics = load_topics()
    if topic_key not in topics:
        abort(404)
    title = topics[topic_key]["title"]

    if request.method == "GET":
        return render_template_string(FORM_HTML, title=title, name="", roll="", error=None)

    name = request.form.get("name", "").strip()
    roll = request.form.get("roll", "").strip()
    if not name or not roll:
        return render_template_string(
            FORM_HTML, title=title, name=name, roll=roll,
            error="Please enter both name and roll number."
        ), 400

    student_key = f"{topic_key}:{roll.lower()}"
    pool = topics[topic_key]["questions"]

    try:
        with lock:
            issued = load_issued()
            if student_key not in issued["students"]:
                chosen, signature = pick_questions(topic_key, pool, issued)
                issued["students"][student_key] = {"name": name, "questions": chosen}
                issued["sets"].setdefault(topic_key, []).append(signature)
                served = issued["served"].setdefault(topic_key, {})
                for qid in chosen:
                    served[qid] = served.get(qid, 0) + 1
                save_issued(issued)
            chosen = issued["students"][student_key]["questions"]
    except RuntimeError as exc:
        return render_template_string(
            FORM_HTML, title=title, name=name, roll=roll, error=str(exc)
        ), 503

    text_by_id = {q["id"]: q["question"] for q in pool}
    questions = [text_by_id[qid] for qid in chosen]
    return render_template_string(RESULT_HTML, title=title, name=name, questions=questions)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
