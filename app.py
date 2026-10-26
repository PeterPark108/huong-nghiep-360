import icons
import json, os, functools
from datetime import timedelta
from grades import GRADES, steps as grade_steps, step_info, href as step_href, next_step, QUIZ_STEP
from flask import Flask, render_template, request, abort, session, redirect, url_for, flash, jsonify
import auth, riasec, step_ui
from auth import db, current_user, login_required
app = Flask(__name__)
ENVB = lambda k, d="0": os.environ.get(k, d).lower() in ("1", "true", "yes")
app.config.update(SECRET_KEY=auth.secret_key(), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=ENVB("SESSION_COOKIE_SECURE"), PERMANENT_SESSION_LIFETIME=timedelta(days=14),
    MAX_CONTENT_LENGTH=64 * 1024, MAX_FORM_MEMORY_SIZE=64 * 1024, MAX_FORM_PARTS=200,
    SEND_FILE_MAX_AGE_DEFAULT=86400)
if ENVB("TRUST_PROXY"):
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; "
       "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'")
@app.after_request
def headers(r):
    h = r.headers
    if r.mimetype == "text/html" and not r.direct_passthrough:  # giao diện: emoji → icon SVG
        r.set_data(icons.svgify(r.get_data(as_text=True)))
    h.setdefault("Content-Security-Policy", CSP); h["X-Content-Type-Options"] = "nosniff"; h["X-Frame-Options"] = "DENY"
    h["Referrer-Policy"] = "strict-origin-when-cross-origin"; h["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if app.config["SESSION_COOKIE_SECURE"]: h["Strict-Transport-Security"] = "max-age=31536000"
    if request.path.startswith(PRIVATE): h["X-Robots-Tag"] = "noindex, nofollow"
    import gzip as _gz
    if (not r.direct_passthrough and r.status_code == 200 and "gzip" in request.headers.get("Accept-Encoding", "")
            and r.mimetype in ("text/html", "text/plain", "application/xml", "application/json") and "Content-Encoding" not in h):
        data = r.get_data()
        if len(data) > 1024:
            r.set_data(_gz.compress(data, 6)); h["Content-Encoding"] = "gzip"; h["Vary"] = "Accept-Encoding"
    if session.get("uid") or request.path.startswith(("/ho-so", "/dang-", "/lop-", "/quiz", "/api/", "/_/")): h["Cache-Control"] = "no-store"
    if request.path.startswith("/static/") and r.status_code == 200: h["Cache-Control"] = "public, max-age=604800"
    return r
auth.init_db()
app.teardown_appcontext(auth.close_db)
app.before_request(auth.check_csrf)
import admin
admin.register(app)
DATA = os.path.join(os.path.dirname(__file__), "data", "careers.json")
@functools.lru_cache(maxsize=1)
def _load(mtime):
    with open(DATA, encoding="utf-8") as f: d = json.load(f)
    for m in d["majors"]:
        sec = d["gso_sectors"][m["gso_sector"]]
        m["income"] = dict(sector=sec["name"], years=d["gso_years"], vals=[round(v / 1000, 1) for v in sec["v"]],
                           srcs=[f"gso{y}" for y in d["gso_years"]], all=[round(v / 1000, 1) for v in d["gso_all"]])
    return d
def load(): return _load(os.path.getmtime(DATA))
def major(mid): return next((m for m in load()["majors"] if m["id"] == mid), None)
RANK = {"Cao": 3, "Kha": 2, "TB": 1, "Thap": 0}
LABEL = {"Cao": "Cao", "Kha": "Khá", "TB": "Trung bình", "Thap": "Thấp"}
TAGS = {"tech":"Công nghệ","logic":"Logic/Toán","hands":"Thực hành","business":"Kinh doanh","people":"Con người","creative":"Sáng tạo","care":"Chăm sóc","science":"Khoa học","organize":"Tổ chức"}
PROVINCES = ["Hà Nội","TP. Hồ Chí Minh","Đà Nẵng","Hải Phòng","Cần Thơ","Huế","Miền Bắc (tỉnh khác)","Miền Trung – Tây Nguyên (tỉnh khác)","Miền Nam (tỉnh khác)"]
SCHOLAR = {"can":"Cần học bổng / hỗ trợ học phí","maybe":"Có thể cần","no":"Chưa cần","skip":"Không muốn chia sẻ"}
FAR = {"yes":"Có thể học xa nhà","near":"Muốn học gần nhà","unsure":"Chưa chắc"}
SUBJECTS = ["Toán","Văn","Tiếng Anh","Lý","Hóa","Sinh","Sử","Địa","Tin học","GDKT&PL","Công nghệ","Nghệ thuật"]
COMBOS = ["A00","A01","B00","C00","D01","D07","Chưa rõ"]
SKILLS = ["Giao tiếp","Làm việc nhóm","Tư duy logic","Sáng tạo","Tự học","Kiên nhẫn","Thuyết trình","Tổ chức, lập kế hoạch","Làm tay, sửa chữa","Ngoại ngữ"]
AFTER = {"dh":"Đại học","cd":"Cao đẳng / học nghề","duhoc":"Du học","dilam":"Đi làm","chuaro":"Chưa rõ"}
SEC_LABEL = {"situation":"Hoàn cảnh","interests":"Sở thích","strengths":"Thế mạnh","plans":"Dự định"}
def profile_status():
    u = current_user()
    if not u: return None
    p = auth.get_profile(u["id"]); d = auth.section_done(p)
    return dict(p=p, done=d, n=sum(d.values()), total=len(d))
SITE_URL = os.environ.get("SITE_URL", "https://huongnghiep.myagentvn.com").rstrip("/")
PRIVATE = ("/ho-so", "/dang-nhap", "/dang-ky", "/dang-xuat", "/api/", "/an-nhac-nho", "/_/")
def abs_url(path): return SITE_URL + path
def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(p)} for i, (n, p) in enumerate(items)]}
def home_ld():
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": SITE_URL + "/#website", "name": "Hướng Nghiệp 360", "url": SITE_URL + "/", "inLanguage": "vi",
         "description": "Công cụ hướng nghiệp miễn phí cho học sinh THPT lớp 10, 11, 12.", "publisher": {"@id": SITE_URL + "/#org"}},
        {"@type": "Organization", "@id": SITE_URL + "/#org", "name": "Hướng Nghiệp 360", "url": SITE_URL + "/",
         "logo": abs_url("/static/img/apple-touch-icon.png")}]}
def occ_ld(m):
    return {"@context": "https://schema.org", "@type": "Occupation", "name": m["name"], "description": m["desc"],
            "skills": ", ".join(m["skills"]), "url": abs_url("/nganh/" + m["id"]),
            "mainEntityOfPage": {"@type": "WebPage", "@id": abs_url("/nganh/" + m["id"]), "inLanguage": "vi"}}
def public_urls():
    from grades import steps as _st
    u = ["/", "/lop-10", "/lop-11", "/lop-12", "/quiz", "/so-sanh", "/con-duong-khac", "/nguon-du-lieu", "/co-so-khoa-hoc", "/chinh-sach-bao-mat"]
    u += [step_href(k) for g in GRADES for k in _st(g) if k != QUIZ_STEP]
    u += ["/nganh/" + m["id"] for m in load()["majors"]]
    return u
@app.route("/robots.txt")
def robots():
    body = "User-agent: *\nAllow: /\n" + "".join(f"Disallow: {p}\n" for p in PRIVATE) + f"\nSitemap: {SITE_URL}/sitemap.xml\n"
    return app.response_class(body, mimetype="text/plain")
@app.route("/sitemap.xml")
def sitemap():
    from xml.sax.saxutils import escape
    lm = load().get("last_checked", "")
    lm = "-".join(reversed(lm.split("/"))) if lm.count("/") == 2 else None
    rows = "".join(f"<url><loc>{escape(abs_url(p))}</loc>" + (f"<lastmod>{lm}</lastmod>" if lm else "") + "</url>" for p in public_urls())
    return app.response_class('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + rows + "</urlset>", mimetype="application/xml")
@app.route("/favicon.ico")
def favicon():
    from flask import send_from_directory
    return send_from_directory(os.path.join(app.root_path, "static", "img"), "favicon.ico", max_age=604800)
@app.context_processor
def ctx():
    return dict(SITE_URL=SITE_URL, CANON=abs_url(request.path), NOINDEX=request.path.startswith(PRIVATE), CRUMBS_LD=crumbs_ld,
                HOME_LD=home_ld, OCC=occ_ld, LABEL=LABEL, TAGS=TAGS, GRADES=GRADES, user=current_user(), csrf_token=auth.csrf_token, pstat=profile_status(),
                SEC_LABELS={"account":"Tài khoản", **SEC_LABEL}, RT=riasec.TYPES, SRC=load()["sources"], LAST_CHECKED=load()["last_checked"])
@app.route("/an-nhac-nho", methods=["POST"])
def dismiss():
    session["hide_reminder"] = True
    return redirect(safe_next(request.form.get("next")))
def safe_next(n): return n if n and n.startswith("/") and not n.startswith("//") else url_for("index")
def do_login(uid):
    guest = session.get("prog") or {}
    session.clear(); session.permanent = True; session["uid"] = uid; session["_csrf"] = auth.secrets.token_urlsafe(32)
    have = auth.get_progress(uid)  # gộp tiến độ đã làm khi chưa đăng nhập
    for g, ks in guest.items():
        if int(g) in GRADES: auth.save_progress(uid, int(g), set(ks) | set(have.get(int(g), [])))
@app.route("/dang-ky", methods=["GET","POST"])
def register():
    if current_user(): return redirect(url_for("index"))
    form, err = {}, {}
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in ("full_name","school","username")}
        uid, err = auth.register(form["full_name"], form["school"], form["username"], request.form.get("password",""))
        if uid:
            do_login(uid); flash("Chào mừng bạn! Tài khoản đã được tạo.")
            return redirect(url_for("profile"))
    return render_template("register.html", form=form, err=err, schools=SCHOOLS), (400 if err else 200)
SCHOOLS = ["THPT Chuyên Hà Nội – Amsterdam","THPT Chu Văn An","THPT Lê Hồng Phong","THPT Nguyễn Thị Minh Khai","THPT Chuyên Lê Quý Đôn","THPT Phan Châu Trinh"]
@app.route("/dang-nhap", methods=["GET","POST"])
def login():
    if current_user(): return redirect(url_for("index"))
    error, username = None, ""
    if request.method == "POST":
        username = request.form.get("username","")[:60]; ip = request.remote_addr or "-"
        wait = auth.locked_for(ip, username)
        if wait:
            error = f"Bạn đã nhập sai nhiều lần. Vui lòng thử lại sau khoảng {max(1, round(wait/60))} phút."
            return render_template("login.html", error=error, username=username, next=request.form.get("next","")), 429
        uid = auth.authenticate(username, request.form.get("password","")[:200])
        if uid:
            auth.clear_fails(ip, username); do_login(uid); return redirect(safe_next(request.form.get("next")))
        auth.record_fail(ip, username)
        error = "Tên đăng nhập hoặc mật khẩu chưa đúng. Bạn thử lại nhé."
    return render_template("login.html", error=error, username=username, next=request.args.get("next") or request.form.get("next","")), (401 if error else 200)
@app.route("/dang-xuat", methods=["POST"])
def logout():
    session.clear(); flash("Bạn đã đăng xuất."); return redirect(url_for("index"))
def picks(name, allowed): return [v for v in request.form.getlist(name) if v in allowed][:20]
def txt(name, n=300): return request.form.get(name, "").strip()[:n] or None
@app.route("/ho-so", methods=["GET","POST"])
@login_required
def profile():
    u = current_user()
    if request.method == "POST":
        sec = auth.SECTIONS.get(request.form.get("section"))
        if not sec: abort(400)
        if sec == "situation":
            gr = request.form.get("grade"); pv = request.form.get("province")
            cols = dict(grade=int(gr) if gr in ("10","11","12") else None, province=pv if pv in PROVINCES else None,
                        needs_scholarship=request.form.get("needs_scholarship") if request.form.get("needs_scholarship") in SCHOLAR else None,
                        can_study_far=request.form.get("can_study_far") if request.form.get("can_study_far") in FAR else None)
        elif sec == "interests":
            cols = dict(interests=json.dumps(picks("interests", TAGS)), interests_note=txt("interests_note"))
        elif sec == "strengths":
            cb = request.form.get("combo")
            cols = dict(strong_subjects=json.dumps(picks("strong_subjects", SUBJECTS), ensure_ascii=False), combo=cb if cb in COMBOS else None,
                        skills=json.dumps(picks("skills", SKILLS), ensure_ascii=False), strengths_note=txt("strengths_note"))
        else:
            ids = {m["id"] for m in load()["majors"]}; af = request.form.get("after_school")
            cols = dict(target_majors=json.dumps(picks("target_majors", ids)[:5]), after_school=af if af in AFTER else None, dream_school=txt("dream_school", 150))
        auth.save_section(u["id"], sec, cols)
        flash(f"Đã lưu phần {SEC_LABEL[sec]} ✓")
        return redirect(url_for("profile") + "#" + request.form.get("section"))
    return render_template("profile.html", majors=load()["majors"], history=auth.riasec_history(u["id"]), PROVINCES=PROVINCES, SCHOLAR=SCHOLAR,
        FAR=FAR, SUBJECTS=SUBJECTS, COMBOS={c: c for c in COMBOS}, SKILLS=SKILLS, AFTER=AFTER, SEC_LABEL=SEC_LABEL)
@app.route("/ho-so/xoa", methods=["GET","POST"])
@login_required
def delete_account():
    if request.method == "POST":
        if request.form.get("confirm") != "XOA":
            return render_template("delete.html", error="Hãy gõ đúng chữ XOA để xác nhận."), 400
        auth.delete_user(current_user()["id"]); session.clear(); flash("Tài khoản và toàn bộ dữ liệu của bạn đã được xóa.")
        return redirect(url_for("index"))
    return render_template("delete.html")
def fit_set(majors):
    ps = profile_status()
    if not ps: return set()
    it, tm = set(ps["p"]["interests"]), set(ps["p"]["target_majors"])
    last = auth.latest_riasec(current_user()["id"])
    out = set()
    for m in majors:
        if m["id"] in tm or (it and len(it & set(m["tags"])) >= min(2, len(m["tags"]))): out.add(m["id"])
        elif last and riasec.match(last["scores"], m["riasec"]) >= 60 and m["riasec"][0] in last["code"][:2]: out.add(m["id"])
    return out
def user_progress():
    """Tiến độ checklist: tài khoản → DB; khách → session (cookie đã ký)."""
    u = current_user()
    if u: return auth.get_progress(u["id"])
    return {int(g): v for g, v in (session.get("prog") or {}).items()}
def set_progress(g, done):
    valid = set(grade_steps(g)); done = {k for k in done if k in valid}
    u = current_user()
    if u: auth.save_progress(u["id"], g, done)
    else: session["prog"] = {**(session.get("prog") or {}), str(g): sorted(done)}
    return done
def mark(key, on=True):
    g = int(key.split("-")[0]); d = set(user_progress().get(g, []))
    return set_progress(g, d | {key} if on else d - {key})
@app.route("/")
def index():
    d = load(); ms = d["majors"]
    g, s, t, sort = (request.args.get(k, "") for k in ("growth","salary","tag","sort"))
    if g: ms = [m for m in ms if m["growth"] == g]
    if s: ms = [m for m in ms if m["salary"] == s]
    if t: ms = [m for m in ms if t in m["tags"]]
    if sort in ("growth","salary"): ms = sorted(ms, key=lambda m: -RANK[m[sort]])
    totals = {n: len(grade_steps(n)) for n in GRADES}
    up = user_progress(); resume = None
    lg = session.get("last_grade") or next((n for n in GRADES if up.get(n)), None)
    if lg in GRADES:
        nk = next_step(lg, set(up.get(lg, [])))
        if nk: resume = dict(g=lg, key=nk, title=step_info(nk)["title"], href=step_href(nk), done=len(up.get(lg, [])), total=totals[lg])
    return render_template("index.html", resume=resume, d=d, majors=ms, fit=fit_set(d["majors"]), f=dict(growth=g,salary=s,tag=t,sort=sort),
                           totals=totals, prog={k: len(v) for k, v in user_progress().items()})
@app.route("/lop-<int:g>")
def grade(g):
    if g not in GRADES: abort(404)
    session["last_grade"] = g
    dn = user_progress().get(g, []); nk = next_step(g, set(dn))
    return render_template("grade.html", g=g, x=GRADES[g], done=dn, nk=nk, nkt=step_info(nk)["title"] if nk else None, total=len(grade_steps(g)), href=step_href)
@app.route("/lop-<int:g>/buoc/<key>", methods=["GET","POST"])
def step(g, key):
    info = step_info(key)
    if not info or info["g"] != g: abort(404)
    session["last_grade"] = g
    u = current_user(); mids = [m["id"] for m in load()["majors"]]
    if request.method == "POST":
        act = request.form.get("action", "done")
        if u and act != "undo": auth.save_step_data(u["id"], key, step_ui.parse(key, request.form, mids))
        if act == "save":
            flash("💾 Đã lưu." if u else "💾 Đã lưu tạm trên trình duyệt này – đăng nhập để giữ lâu dài."); return redirect(url_for("step", g=g, key=key))
        on = act != "undo"; done = mark(key, on)
        if on:
            nk = next_step(g, done, key)
            flash("✓ Đã hoàn thành: " + info["title"] + ("" if nk else f" – bạn đã xong cả lộ trình lớp {g}! 🎉"))
            return redirect(step_href(nk) if nk and request.form.get("go") == "next" else url_for("step", g=g, key=key))
        flash("Đã bỏ tích bước này."); return redirect(url_for("step", g=g, key=key))
    done = set(user_progress().get(g, [])); ks = grade_steps(g); i = ks.index(key)
    nk = next_step(g, done, key)
    data = auth.get_step_data(u["id"], key) if u else {}
    last = auth.latest_riasec(u["id"]) if u and key == QUIZ_STEP else None
    return render_template("step.html", s=info, g=g, x=GRADES[g], is_done=key in done, n=i + 1, total=len(ks), ndone=len(done),
                           prev=ks[i - 1] if i else None, nxt=ks[i + 1] if i + 1 < len(ks) else None, todo=nk, href=step_href,
                           W=step_ui.widgets(key), D=data, kind=step_ui.kind(key), majors=load()["majors"], last=last,
                           ACT=ACTIONS.get(key, []), RS=RESEARCH)
@app.route("/api/buoc/<key>", methods=["POST"])
def save_step_api(key):
    if not step_info(key): abort(404)
    u = current_user()
    if not u: return jsonify(ok=True, local=True)
    d = step_ui.parse(key, request.form, [m["id"] for m in load()["majors"]]); auth.save_step_data(u["id"], key, d)
    return jsonify(ok=True, n=len(d))
@app.route("/api/tien-do", methods=["POST"])
def save_progress():
    data = request.get_json(silent=True) or {}
    g = data.get("grade")
    if g not in GRADES or not isinstance(data.get("done"), list): return jsonify(ok=False, error="invalid"), 400
    valid = set(grade_steps(g)); done = {k for k in data["done"] if isinstance(k, str) and k in valid}
    if data.get("merge"): done |= set(user_progress().get(g, []))
    done = set_progress(g, done)
    return jsonify(ok=True, done=sorted(done), n=len(done), total=len(valid))
@app.route("/nganh/<mid>")
def detail(mid):
    m = major(mid)
    if not m: abort(404)
    return render_template("detail.html", d=load(), m=m)
@app.route("/quiz", methods=["GET","POST"])
def quiz():
    Q = riasec.QUESTIONS
    buoc = request.values.get("buoc", "")
    buoc = buoc if step_info(buoc) else ""
    if request.method == "GET": return render_template("quiz.html", Q=Q, L=riasec.LIKERT, buoc=buoc)
    ans = riasec.parse_form(request.form)
    if len(ans) < len(Q) // 2:
        return render_template("quiz.html", Q=Q, L=riasec.LIKERT, prev=ans, buoc=buoc,
                               error=f"Bạn hãy trả lời ít nhất {len(Q)//2} câu để kết quả có ý nghĩa (đã trả lời {len(ans)}/{len(Q)})."), 400
    sc, n = riasec.score(ans); code = riasec.top3(sc); res = riasec.rank(sc, load()["majors"])
    saved = False; u = current_user()
    if u:
        gr = auth.get_profile(u["id"]).get("grade")
        auth.save_riasec(u["id"], gr, {str(k): v for k, v in ans.items()}, sc, code, [dict(id=r["m"]["id"], name=r["m"]["name"], pct=r["pct"]) for r in res]); saved = True
    mark(QUIZ_STEP)  # làm xong trắc nghiệm → tự tích ô "Làm trắc nghiệm sở thích"
    g = int(buoc.split("-")[0]) if buoc else session.get("last_grade") or (u and auth.get_profile(u["id"]).get("grade")) or 10
    nk = next_step(g, set(user_progress().get(g, [])), buoc or (QUIZ_STEP if g == 10 else None))
    nxt = dict(url=step_href(nk), title=step_info(nk)["title"], g=g) if nk else dict(url=f"/lop-{g}", title=f"Xem lộ trình lớp {g}", g=g)
    return render_template("result.html", sc=sc, code=code, res=res, saved=saved, answered=n, total=len(Q), nxt=nxt,
                           chart=dict(labels=[riasec.TYPES[c]["short"] for c in sc], values=list(sc.values())))
@app.route("/so-sanh")
def compare():
    ids = []
    for i in request.args.getlist("nganh"):
        if major(i) and i not in ids: ids.append(i)
    ms = [major(i) for i in ids[:3]]
    return render_template("compare.html", ms=ms, all=load()["majors"], d=load(), too_many=len(ids) > 3, bad=any(i and not major(i) for i in request.args.getlist("nganh")))
@app.route("/con-duong-khac")
def other_paths():
    from paths import PATHS, OFFICIAL
    return render_template("paths.html", P=PATHS, OFFICIAL=OFFICIAL)
import json as _json
_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RESEARCH = {r["id"]: r for r in _json.load(open(os.path.join(_D, "research.json"), encoding="utf-8"))}
ACTIONS = _json.load(open(os.path.join(_D, "actions.json"), encoding="utf-8"))
@app.route("/co-so-khoa-hoc")
def science():
    used = {}
    for k, acts in ACTIONS.items():
        for a in acts:
            for r in a["refs"]: used.setdefault(r, []).append(k) if k not in used.get(r, []) else None
    return render_template("science.html", R=list(RESEARCH.values()), used=used, info=step_info, href=step_href)
@app.route("/nguon-du-lieu")
def sources():
    d = load()
    cover = dict(salary=[m for m in d["majors"] if m.get("salary_vnd")], facts=[m for m in d["majors"] if m["facts"]])
    return render_template("sources.html", d=d, cover=cover)
@app.route("/chinh-sach-bao-mat")
def privacy(): return render_template("privacy.html")
@app.route("/healthz")
def healthz():
    db().execute("SELECT 1"); return jsonify(status="ok")
ERRORS={400:("Yêu cầu không hợp lệ","Phiên làm việc có thể đã hết hạn. Hãy tải lại trang và thử lại."),
 404:("Không tìm thấy trang","Trang bạn tìm không tồn tại hoặc đã được chuyển đi."),
 500:("Có lỗi xảy ra","Hệ thống gặp sự cố. Bạn hãy thử lại sau ít phút.")}
def _err(e):
    code=getattr(e,"code",500) or 500; t,m=ERRORS.get(code,ERRORS[500])
    return render_template("error.html",code=code,title=t,msg=m),code
ERRORS[413]=("Dữ liệu gửi lên quá lớn","Nội dung bạn gửi vượt giới hạn cho phép.")
ERRORS[429]=("Thao tác quá nhanh","Bạn hãy chờ một chút rồi thử lại.")
ERRORS[405]=("Thao tác không hợp lệ","Trang này không hỗ trợ thao tác bạn vừa thực hiện.")
for _c in ERRORS: app.register_error_handler(_c,_err)

if __name__ == "__main__":  # chỉ dùng khi phát triển; production chạy gunicorn (xem README)
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
