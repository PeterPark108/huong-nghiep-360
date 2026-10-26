"""Trang quản trị CHỈ ĐỌC. Bật khi đặt ADMIN_PATH (chuỗi bí mật ≥16 ký tự [A-Za-z0-9_-]).
URL: /_/<ADMIN_PATH>/ . Không đặt / sai định dạng → mọi URL admin trả 404."""
import os, re, json, time, secrets, hashlib, sqlite3
from datetime import datetime, timezone, timedelta
from flask import request, abort, render_template, redirect, g, session
from werkzeug.security import generate_password_hash, check_password_hash
import auth
from auth import db

SCHEMA = """
CREATE TABLE IF NOT EXISTS admin_users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL COLLATE NOCASE,
 password_hash TEXT NOT NULL, created_at TEXT NOT NULL, last_login_at TEXT);
CREATE TABLE IF NOT EXISTS admin_sessions(token_hash TEXT PRIMARY KEY, admin_id INTEGER NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
 csrf TEXT NOT NULL, created_at REAL NOT NULL, expires_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS admin_attempts(k TEXT PRIMARY KEY, fails INTEGER NOT NULL, first_at REAL NOT NULL, locked_until REAL NOT NULL);
CREATE TABLE IF NOT EXISTS user_activity(user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, day TEXT NOT NULL,
 PRIMARY KEY(user_id, day));
CREATE TABLE IF NOT EXISTS app_meta(k TEXT PRIMARY KEY, v TEXT NOT NULL);
"""
TZ = timezone(timedelta(hours=7))  # Asia/Bangkok / Việt Nam
COOKIE, IDLE, MAX_AGE = "hn_adm", 30 * 60, 8 * 3600
U_MAX, IP_MAX, WINDOW = 5, 10, 900
_raw = os.environ.get("ADMIN_PATH", "").strip().strip("/")
ADMIN_PATH = _raw if re.fullmatch(r"[A-Za-z0-9_-]{16,64}", _raw or "") else None
PREFIX = "/_/"  # robots.txt chỉ ghi "Disallow: /_/" → không lộ phần bí mật
BASE = PREFIX + ADMIN_PATH if ADMIN_PATH else None

def init_db():
    c = sqlite3.connect(auth.DB); c.executescript(SCHEMA)
    c.execute("INSERT OR IGNORE INTO app_meta(k,v) VALUES('activity_since',?)", (datetime.now(TZ).date().isoformat(),))
    c.commit(); c.close()

# ---- Ghi nhận hoạt động (mỗi người 1 dòng/ngày, không lưu nội dung) ----
def track():
    uid = session.get("uid")
    if not uid or request.path.startswith("/static/"): return
    day = datetime.now(TZ).date().isoformat()
    if session.get("_act") == day: return
    try:
        db().execute("INSERT OR IGNORE INTO user_activity(user_id,day) SELECT id,? FROM users WHERE id=?", (day, uid)); db().commit()
        session["_act"] = day
    except sqlite3.Error: pass

# ---- Che thông tin ----
def mask(s):
    s = (s or "").strip()
    if not s: return "–"
    if "@" in s:
        a, _, d = s.partition("@"); return mask(a) + "@" + d
    if len(s) <= 2: return s[0] + "*"
    keep = 1 if len(s) < 7 else 2
    return s[:keep] + "*" * max(3, len(s) - 2 * keep) + s[-keep:]
def initials(name): return ".".join(w[0].upper() for w in (name or "").split() if w)[:12] + "." if name and name.split() else "–"
def vn(ts):
    try: return datetime.fromisoformat(ts).astimezone(TZ).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError): return "–"

# ---- Chống dò mật khẩu ----
def _k(ip, u): return [f"u:{ip}:{(u or '').strip().lower()[:60]}", f"ip:{ip}"]
def locked(ip, u):
    t = time.time()
    return any((r := db().execute("SELECT locked_until FROM admin_attempts WHERE k=?", (k,)).fetchone()) and r[0] > t for k in _k(ip, u))
def fail(ip, u):
    t = time.time()
    for k, lim in zip(_k(ip, u), (U_MAX, IP_MAX)):
        r = db().execute("SELECT fails, first_at FROM admin_attempts WHERE k=?", (k,)).fetchone()
        n, first = (r[0] + 1, r[1]) if r and t - r[1] < WINDOW else (1, t)
        lock = t + min(3600, 60 * 2 ** (n - lim)) if n >= lim else 0
        db().execute("INSERT OR REPLACE INTO admin_attempts VALUES(?,?,?,?)", (k, n, first, lock))
    db().commit()

# ---- Phiên admin riêng (cookie riêng, lưu băm token trong DB) ----
H = lambda t: hashlib.sha256(t.encode()).hexdigest()
def current():
    if "adm" in g: return g.adm
    g.adm = None; t = request.cookies.get(COOKIE)
    if t:
        now = time.time()
        r = db().execute("SELECT s.*, a.username FROM admin_sessions s JOIN admin_users a ON a.id=s.admin_id WHERE token_hash=?", (H(t),)).fetchone()
        if r and r["expires_at"] > now and now - r["created_at"] < MAX_AGE:
            db().execute("UPDATE admin_sessions SET expires_at=? WHERE token_hash=?", (now + IDLE, H(t))); db().commit(); g.adm = r
    return g.adm
def _cookie(resp, val, age):
    from flask import current_app
    resp.set_cookie(COOKIE, val, max_age=age, path=BASE, httponly=True, samesite="Strict",
                    secure=current_app.config.get("SESSION_COOKIE_SECURE", False))
    return resp
def _form_ok():
    t = request.form.get("_acsrf", "")
    return bool(current()) and secrets.compare_digest(t, current()["csrf"])

# ---- Số liệu tổng hợp (chỉ đọc) ----
def stats():
    q = lambda s, a=(): db().execute(s, a).fetchall()
    one = lambda s, a=(): db().execute(s, a).fetchone()[0]
    today = datetime.now(TZ).date()
    days = [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    reg = {d: 0 for d in days}
    for (c,) in q("SELECT created_at FROM users"):
        try: d = datetime.fromisoformat(c).astimezone(TZ).date().isoformat()
        except ValueError: continue
        if d in reg: reg[d] += 1
    from grades import step_info
    steps = []
    for k, n in q("SELECT k, COUNT(*) FROM step_data GROUP BY k ORDER BY 2 DESC"):
        i = step_info(k); steps.append((k, i["title"] if i else k, n))
    import riasec
    codes = {t: 0 for t in riasec.TYPES}
    for (c,) in q("SELECT code FROM riasec_results"):
        if c and c[0] in codes: codes[c[0]] += 1
    prog = q("SELECT grade, COUNT(*), SUM(json_array_length(done)) FROM progress GROUP BY grade ORDER BY grade")
    since = (one("SELECT v FROM app_meta WHERE k='activity_since'") if one("SELECT COUNT(*) FROM app_meta WHERE k='activity_since'") else None)
    s = dict(
        users=one("SELECT COUNT(*) FROM users"),
        new7=sum(reg[d] for d in days[-7:]), new30=sum(reg.values()),
        reg=[(d[8:10] + "/" + d[5:7], reg[d]) for d in days], regmax=max(reg.values()) or 1,
        login7=one("SELECT COUNT(*) FROM users WHERE last_login_at >= ?", ((datetime.now(timezone.utc) - timedelta(days=7)).isoformat(timespec="seconds"),)),
        riasec_n=one("SELECT COUNT(*) FROM riasec_results"), riasec_u=one("SELECT COUNT(DISTINCT user_id) FROM riasec_results"),
        quiz_old=one("SELECT COUNT(*) FROM quiz_results"),
        codes=[(t, riasec.TYPES[t], n) for t, n in codes.items()], codemax=max(codes.values()) or 1,
        steps=steps, step_users=one("SELECT COUNT(DISTINCT user_id) FROM step_data"),
        prog=prog,
        grades=q("SELECT grade, COUNT(*) FROM profiles WHERE grade IS NOT NULL GROUP BY grade ORDER BY grade"),
        prof_done=one("SELECT COUNT(*) FROM profiles WHERE situation_updated_at IS NOT NULL OR interests_updated_at IS NOT NULL OR strengths_updated_at IS NOT NULL OR plans_updated_at IS NOT NULL"),
        since=since and datetime.fromisoformat(since).strftime("%d/%m/%Y"),
        active7=one("SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE day >= ?", (days[-7],)),
        returning=one("SELECT COUNT(*) FROM (SELECT user_id FROM user_activity GROUP BY user_id HAVING COUNT(*) >= 2)"),
        act_rows=one("SELECT COUNT(*) FROM user_activity"),
    )
    ev = q("""SELECT * FROM (
      SELECT u.created_at t, 'Đăng ký tài khoản' e, u.username un FROM users u
      UNION ALL SELECT r.created_at, 'Làm trắc nghiệm Holland (' || r.code || ')', u.username FROM riasec_results r JOIN users u ON u.id=r.user_id
      UNION ALL SELECT q.created_at, 'Làm trắc nghiệm sở thích (cũ)', u.username FROM quiz_results q JOIN users u ON u.id=q.user_id
      UNION ALL SELECT d.updated_at, 'Lưu bước ' || d.k, u.username FROM step_data d JOIN users u ON u.id=d.user_id
      UNION ALL SELECT p.updated_at, 'Cập nhật tiến độ lớp ' || p.grade, u.username FROM progress p JOIN users u ON u.id=p.user_id
    ) ORDER BY t DESC LIMIT 20""")
    s["events"] = [(vn(t), e, mask(un)) for t, e, un in ev]
    return s

PER_PAGE = 20
def users_page(page):
    total = db().execute("SELECT COUNT(*) FROM users").fetchone()[0]
    pages = max(1, -(-total // PER_PAGE)); page = min(max(1, page), pages)
    rs = db().execute("""SELECT u.id, u.username, u.full_name, u.school, u.created_at, u.last_login_at, p.grade,
      (SELECT COUNT(*) FROM riasec_results r WHERE r.user_id=u.id) nr,
      (SELECT COUNT(*) FROM step_data d WHERE d.user_id=u.id) ns,
      (SELECT COUNT(*) FROM user_activity a WHERE a.user_id=u.id) na
      FROM users u LEFT JOIN profiles p ON p.user_id=u.id ORDER BY u.id DESC LIMIT ? OFFSET ?""", (PER_PAGE, (page - 1) * PER_PAGE)).fetchall()
    rows = [dict(id=r["id"], user=mask(r["username"]), name=initials(r["full_name"]), school=r["school"], grade=r["grade"],
                 created=vn(r["created_at"]), last=vn(r["last_login_at"]), nr=r["nr"], ns=r["ns"], na=r["na"]) for r in rs]
    return rows, page, pages, total

def register(app):
    init_db()
    app.before_request(track)
    if not BASE: return
    def guard():
        r = current()
        if not r: return redirect(BASE + "/dang-nhap")
    @app.route(BASE + "/", endpoint="adm_home")
    def home():
        if (x := guard()): return x
        return render_template("admin.html", s=stats(), adm=current(), base=BASE)
    @app.route(BASE + "/nguoi-dung", endpoint="adm_users")
    def users():
        if (x := guard()): return x
        rows, page, pages, total = users_page(request.args.get("trang", 1, type=int))
        return render_template("admin_users.html", rows=rows, page=page, pages=pages, total=total, adm=current(), base=BASE)
    @app.route(BASE + "/dang-nhap", methods=["GET", "POST"], endpoint="adm_login")
    def login():
        if current(): return redirect(BASE + "/")
        err = None
        if request.method == "POST":
            u = request.form.get("username", "")[:60]; pw = request.form.get("password", "")[:200]; ip = request.remote_addr or "-"
            if locked(ip, u):
                return render_template("admin_login.html", err="Đăng nhập không thành công. Vui lòng thử lại sau.", base=BASE), 429
            r = db().execute("SELECT id, password_hash FROM admin_users WHERE username=?", (u.strip(),)).fetchone()
            if r and check_password_hash(r["password_hash"], pw):
                db().execute("DELETE FROM admin_attempts WHERE k=?", (_k(ip, u)[0],))
                db().execute("DELETE FROM admin_sessions WHERE expires_at < ?", (time.time(),))
                t = secrets.token_urlsafe(32); now = time.time()
                db().execute("INSERT INTO admin_sessions VALUES(?,?,?,?,?)", (H(t), r["id"], secrets.token_urlsafe(32), now, now + IDLE))
                db().execute("UPDATE admin_users SET last_login_at=? WHERE id=?", (auth.now(), r["id"])); db().commit()
                return _cookie(redirect(BASE + "/"), t, MAX_AGE)
            if not r: check_password_hash(DUMMY, pw)  # cân thời gian phản hồi
            fail(ip, u); err = "Đăng nhập không thành công. Vui lòng thử lại sau."
        return render_template("admin_login.html", err=err, base=BASE), (401 if err else 200)
    @app.route(BASE + "/dang-xuat", methods=["POST"], endpoint="adm_logout")
    def logout():
        if not _form_ok(): abort(400)
        db().execute("DELETE FROM admin_sessions WHERE token_hash=?", (H(request.cookies.get(COOKIE, "")),)); db().commit()
        return _cookie(redirect(BASE + "/dang-nhap"), "", 0)
DUMMY = generate_password_hash(secrets.token_hex(8))
