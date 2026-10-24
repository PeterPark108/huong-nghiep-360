"""Tài khoản, hồ sơ, CSRF, SQLite (stdlib)."""
import os, json, re, secrets, sqlite3
from datetime import datetime, timezone
from functools import wraps
from flask import g, session, request, abort, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(__file__)
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE, "data"))
os.makedirs(DATA_DIR, exist_ok=True)
DB = os.environ.get("APP_DB", os.path.join(DATA_DIR, "app.db"))
SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL COLLATE NOCASE,
 password_hash TEXT NOT NULL, full_name TEXT NOT NULL, school TEXT NOT NULL, created_at TEXT NOT NULL, last_login_at TEXT);
CREATE TABLE IF NOT EXISTS profiles(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 grade INTEGER, province TEXT, needs_scholarship TEXT, can_study_far TEXT, situation_updated_at TEXT,
 interests TEXT, interests_note TEXT, interests_updated_at TEXT,
 strong_subjects TEXT, combo TEXT, skills TEXT, strengths_note TEXT, strengths_updated_at TEXT,
 target_majors TEXT, after_school TEXT, dream_school TEXT, plans_updated_at TEXT);
CREATE TABLE IF NOT EXISTS quiz_results(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 created_at TEXT NOT NULL, answers TEXT NOT NULL, tag_scores TEXT NOT NULL, top_majors TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS riasec_results(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 created_at TEXT NOT NULL, grade INTEGER, answers TEXT NOT NULL, scores TEXT NOT NULL, code TEXT NOT NULL, top_majors TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS progress(user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, grade INTEGER NOT NULL,
 done TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(user_id, grade));
CREATE TABLE IF NOT EXISTS login_attempts(k TEXT PRIMARY KEY, fails INTEGER NOT NULL, first_at REAL NOT NULL, locked_until REAL NOT NULL);
"""
def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

def secret_key():
    k = os.environ.get("SECRET_KEY")
    if k: return k
    p = os.path.join(DATA_DIR, ".secret_key")
    if not os.path.exists(p):
        with open(p, "w") as f: f.write(secrets.token_hex(32))
        os.chmod(p, 0o600)
    return open(p).read().strip()

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db
def init_db():
    c = sqlite3.connect(DB); c.executescript(SCHEMA); c.commit(); c.close()
def close_db(e=None):
    d = g.pop("db", None)
    if d: d.close()

def csrf_token():
    if "_csrf" not in session: session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]
def check_csrf():
    if request.method == "POST":
        t = request.form.get("_csrf", "") or request.headers.get("X-CSRF-Token", "")
        if not t or not secrets.compare_digest(t, session.get("_csrf", "")): abort(400, "CSRF")

def current_user():
    uid = session.get("uid")
    if not uid: return None
    if "user" not in g: g.user = db().execute("SELECT id,username,full_name,school FROM users WHERE id=?", (uid,)).fetchone()
    return g.user
def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not current_user(): return redirect(url_for("login", next=request.path))
        return f(*a, **k)
    return w

USER_RE = re.compile(r"^[A-Za-z0-9_.]{3,30}$")
def register(full_name, school, username, password):
    err = {}
    full_name, school, username = full_name.strip(), school.strip(), username.strip()
    if len(full_name) < 2: err["full_name"] = "Bạn nhập họ và tên giúp mình nhé."
    elif len(full_name) > 80: err["full_name"] = "Họ tên hơi dài, tối đa 80 ký tự."
    if len(school) < 2: err["school"] = "Bạn đang học ở trường nào?"
    elif len(school) > 120: err["school"] = "Tên trường tối đa 120 ký tự."
    if not USER_RE.match(username): err["username"] = "Tên đăng nhập 3–30 ký tự, chỉ gồm chữ không dấu, số, dấu _ hoặc dấu chấm."
    if len(password) < 6: err["password"] = "Mật khẩu cần ít nhất 6 ký tự."
    elif is_common(password, username): err["password"] = "Mật khẩu này quá dễ đoán, bạn chọn mật khẩu khác nhé."
    elif len(password) > 200: err["password"] = "Mật khẩu quá dài."
    if not err and db().execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
        err["username"] = "Tên đăng nhập này đã có người dùng, bạn thử tên khác nhé."
    if err: return None, err
    cur = db().execute("INSERT INTO users(username,password_hash,full_name,school,created_at,last_login_at) VALUES(?,?,?,?,?,?)",
                       (username, generate_password_hash(password), full_name, school, now(), now()))
    db().execute("INSERT INTO profiles(user_id) VALUES(?)", (cur.lastrowid,)); db().commit()
    return cur.lastrowid, {}
def authenticate(username, password):
    r = db().execute("SELECT id,password_hash FROM users WHERE username=?", (username.strip(),)).fetchone()
    if r and check_password_hash(r["password_hash"], password):
        db().execute("UPDATE users SET last_login_at=? WHERE id=?", (now(), r["id"])); db().commit(); return r["id"]
    return None

def get_profile(uid):
    r = db().execute("SELECT * FROM profiles WHERE user_id=?", (uid,)).fetchone()
    p = dict(r) if r else {}
    for k in ("interests", "strong_subjects", "skills", "target_majors"):
        p[k] = json.loads(p[k]) if p.get(k) else []
    return p
SECTIONS = {"hoan-canh": "situation", "so-thich": "interests", "the-manh": "strengths", "du-dinh": "plans"}
def section_done(p):
    return {"account": True,
            "situation": bool(p.get("grade") or p.get("province")),
            "interests": bool(p.get("interests") or p.get("interests_note")),
            "strengths": bool(p.get("strong_subjects") or p.get("skills") or p.get("strengths_note")),
            "plans": bool(p.get("target_majors") or p.get("after_school"))}
def save_section(uid, sec, cols):
    cols[f"{sec}_updated_at"] = now()
    sets = ",".join(f"{k}=?" for k in cols)  # keys come from fixed whitelist in app.py
    db().execute(f"UPDATE profiles SET {sets} WHERE user_id=?", (*cols.values(), uid)); db().commit()
def save_quiz(uid, answers, scores, top):
    db().execute("INSERT INTO quiz_results(user_id,created_at,answers,tag_scores,top_majors) VALUES(?,?,?,?,?)",
                 (uid, now(), json.dumps(answers), json.dumps(scores), json.dumps(top, ensure_ascii=False))); db().commit()
def quiz_history(uid):
    rs = db().execute("SELECT created_at,tag_scores,top_majors FROM quiz_results WHERE user_id=? ORDER BY id DESC LIMIT 5", (uid,)).fetchall()
    return [dict(created_at=datetime.fromisoformat(r["created_at"]).astimezone().strftime("%d/%m/%Y %H:%M"), scores=json.loads(r["tag_scores"]), top=json.loads(r["top_majors"])) for r in rs]
def delete_user(uid):
    db().execute("DELETE FROM users WHERE id=?", (uid,)); db().commit()

COMMON = set("""123456 1234567 12345678 123456789 1234567890 111111 000000 666666 888888 999999 123123 112233 121212 654321 abc123
abcdef abc123456 qwerty qwerty123 qwertyuiop asdfgh asdfghjk zxcvbn password password1 password123 matkhau matkhau1 matkhau123
iloveyou iloveu anhyeuem emyeuanh yeuem123 123abc a123456 aa123456 abcd1234 1q2w3e 1q2w3e4r admin admin123 welcome letmein
football monkey dragon sunshine princess hello123 vietnam vietnam1 hanoi123 saigon123 hocsinh hocsinh1 hocsinh123 123qwe 147258
159753 789456 456789 987654321 11223344 555555 777777 222222 aaaaaa abcabc thpt123 truong123""".split())
def is_common(pw, username=""):
    p = pw.lower()
    return p in COMMON or (username and p == username.lower()) or len(set(p)) <= 2

# ---- Giới hạn đăng nhập sai (lưu trong SQLite, dùng được với nhiều worker) ----
import time
MAX_FAILS, IP_MAX, WINDOW = 5, 30, 900
def _keys(ip, username): return [f"u:{ip}:{username.strip().lower()[:40]}", f"ip:{ip}"]
def locked_for(ip, username):
    t = time.time(); left = 0
    for k in _keys(ip, username):
        r = db().execute("SELECT locked_until FROM login_attempts WHERE k=?", (k,)).fetchone()
        if r and r[0] > t: left = max(left, r[0] - t)
    return int(left) + (1 if left else 0)
def record_fail(ip, username):
    t = time.time()
    for k, lim in zip(_keys(ip, username), (MAX_FAILS, IP_MAX)):
        r = db().execute("SELECT fails, first_at FROM login_attempts WHERE k=?", (k,)).fetchone()
        fails, first = (r[0] + 1, r[1]) if r and t - r[1] < WINDOW else (1, t)
        lock = t + min(900, 30 * 2 ** (fails - lim)) if fails >= lim else 0
        db().execute("INSERT OR REPLACE INTO login_attempts(k,fails,first_at,locked_until) VALUES(?,?,?,?)", (k, fails, first, lock))
    db().execute("DELETE FROM login_attempts WHERE first_at < ? AND locked_until < ?", (t - WINDOW, t)); db().commit()
def clear_fails(ip, username):
    db().execute("DELETE FROM login_attempts WHERE k=?", (_keys(ip, username)[0],)); db().commit()

# ---- RIASEC ----
def save_riasec(uid, grade, answers, scores, code, top):
    db().execute("INSERT INTO riasec_results(user_id,created_at,grade,answers,scores,code,top_majors) VALUES(?,?,?,?,?,?,?)",
                 (uid, now(), grade, json.dumps(answers), json.dumps(scores), code, json.dumps(top, ensure_ascii=False))); db().commit()
def riasec_history(uid, n=10):
    rs = db().execute("SELECT * FROM riasec_results WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid, n)).fetchall()
    return [dict(created_at=datetime.fromisoformat(r["created_at"]).astimezone().strftime("%d/%m/%Y"), grade=r["grade"], code=r["code"],
                 scores=json.loads(r["scores"]), top=json.loads(r["top_majors"])) for r in rs]
def latest_riasec(uid):
    h = riasec_history(uid, 1); return h[0] if h else None

# ---- Tiến độ trang lớp ----
def get_progress(uid):
    return {r["grade"]: json.loads(r["done"]) for r in db().execute("SELECT grade, done FROM progress WHERE user_id=?", (uid,))}
def save_progress(uid, grade, done):
    db().execute("INSERT OR REPLACE INTO progress(user_id,grade,done,updated_at) VALUES(?,?,?,?)", (uid, grade, json.dumps(sorted(done)), now())); db().commit()
