import json, os, functools
from datetime import timedelta
from grades import GRADES, steps as grade_steps
from flask import Flask, render_template, request, abort, session, redirect, url_for, flash, jsonify
import auth, riasec
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
    h.setdefault("Content-Security-Policy", CSP); h["X-Content-Type-Options"] = "nosniff"; h["X-Frame-Options"] = "DENY"
    h["Referrer-Policy"] = "strict-origin-when-cross-origin"; h["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if app.config["SESSION_COOKIE_SECURE"]: h["Strict-Transport-Security"] = "max-age=31536000"
    if session.get("uid") or request.path.startswith(("/ho-so", "/dang-")): h["Cache-Control"] = "no-store"
    return r
auth.init_db()
app.teardown_appcontext(auth.close_db)
app.before_request(auth.check_csrf)
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
@app.context_processor
def ctx():
    return dict(LABEL=LABEL, TAGS=TAGS, GRADES=GRADES, user=current_user(), csrf_token=auth.csrf_token, pstat=profile_status(),
                SEC_LABELS={"account":"Tài khoản", **SEC_LABEL}, RT=riasec.TYPES, SRC=load()["sources"], LAST_CHECKED=load()["last_checked"])
@app.route("/an-nhac-nho", methods=["POST"])
def dismiss():
    session["hide_reminder"] = True
    return redirect(safe_next(request.form.get("next")))
def safe_next(n): return n if n and n.startswith("/") and not n.startswith("//") else url_for("index")
def do_login(uid):
    session.clear(); session.permanent = True; session["uid"] = uid; session["_csrf"] = auth.secrets.token_urlsafe(32)
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
    u = current_user()
    return auth.get_progress(u["id"]) if u else {}
@app.route("/")
def index():
    d = load(); ms = d["majors"]
    g, s, t, sort = (request.args.get(k, "") for k in ("growth","salary","tag","sort"))
    if g: ms = [m for m in ms if m["growth"] == g]
    if s: ms = [m for m in ms if m["salary"] == s]
    if t: ms = [m for m in ms if t in m["tags"]]
    if sort in ("growth","salary"): ms = sorted(ms, key=lambda m: -RANK[m[sort]])
    totals = {n: len(grade_steps(n)) for n in GRADES}
    return render_template("index.html", d=d, majors=ms, fit=fit_set(d["majors"]), f=dict(growth=g,salary=s,tag=t,sort=sort),
                           totals=totals, prog={k: len(v) for k, v in user_progress().items()})
@app.route("/lop-<int:g>")
def grade(g):
    if g not in GRADES: abort(404)
    return render_template("grade.html", g=g, x=GRADES[g], done=user_progress().get(g, []), total=len(grade_steps(g)))
@app.route("/api/tien-do", methods=["POST"])
def save_progress():
    u = current_user()
    if not u: return jsonify(ok=False, error="login"), 401
    data = request.get_json(silent=True) or {}
    g = data.get("grade")
    if g not in GRADES or not isinstance(data.get("done"), list): return jsonify(ok=False, error="invalid"), 400
    valid = set(grade_steps(g)); done = {k for k in data["done"] if isinstance(k, str) and k in valid}
    if data.get("merge"): done |= set(auth.get_progress(u["id"]).get(g, []))
    auth.save_progress(u["id"], g, done)
    return jsonify(ok=True, done=sorted(done), n=len(done), total=len(valid))
@app.route("/nganh/<mid>")
def detail(mid):
    m = major(mid)
    if not m: abort(404)
    return render_template("detail.html", d=load(), m=m)
@app.route("/quiz", methods=["GET","POST"])
def quiz():
    Q = riasec.QUESTIONS
    if request.method == "GET": return render_template("quiz.html", Q=Q, L=riasec.LIKERT)
    ans = riasec.parse_form(request.form)
    if len(ans) < len(Q) // 2:
        return render_template("quiz.html", Q=Q, L=riasec.LIKERT, prev=ans,
                               error=f"Bạn hãy trả lời ít nhất {len(Q)//2} câu để kết quả có ý nghĩa (đã trả lời {len(ans)}/{len(Q)})."), 400
    sc, n = riasec.score(ans); code = riasec.top3(sc); res = riasec.rank(sc, load()["majors"])
    saved = False; u = current_user()
    if u:
        gr = auth.get_profile(u["id"]).get("grade")
        auth.save_riasec(u["id"], gr, {str(k): v for k, v in ans.items()}, sc, code, [dict(id=r["m"]["id"], name=r["m"]["name"], pct=r["pct"]) for r in res]); saved = True
    return render_template("result.html", sc=sc, code=code, res=res, saved=saved, answered=n, total=len(Q),
                           chart=dict(labels=[riasec.TYPES[c]["short"] for c in sc], values=list(sc.values())))
@app.route("/so-sanh")
def compare():
    ids = []
    for i in request.args.getlist("nganh"):
        if major(i) and i not in ids: ids.append(i)
    ms = [major(i) for i in ids[:3]]
    return render_template("compare.html", ms=ms, all=load()["majors"], d=load(), too_many=len(ids) > 3)
@app.route("/con-duong-khac")
def other_paths():
    from paths import PATHS, OFFICIAL
    return render_template("paths.html", P=PATHS, OFFICIAL=OFFICIAL)
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
