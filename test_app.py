"""Kiểm thử: .venv/bin/python test_app.py"""
import os, re, sqlite3, tempfile, json
os.environ["DATA_DIR"] = tempfile.mkdtemp(); os.environ["APP_DB"] = os.path.join(os.environ["DATA_DIR"], "t.db")
import app as A, riasec, auth, step_ui
from werkzeug.datastructures import MultiDict
from grades import steps
A.app.config["PROPAGATE_EXCEPTIONS"] = False
@A.app.route("/_boom")
def _boom(): raise RuntimeError("x")
c = A.app.test_client()
N = [0]
def ok(cond, msg): assert cond, msg; N[0] += 1; print("PASS", msg)
def tok(path, cl=None):
    return re.search(r'(?:name="_csrf" value|name="csrf-token" content)="([^"]+)"', (cl or c).get(path).get_data(as_text=True)).group(1)
PW = "Huongnghiep#2026"
R = lambda **k: {**dict(full_name="Nguyễn Văn An", school="THPT Chu Văn An", username="an.nguyen", password=PW), **k}
DBC = lambda: sqlite3.connect(os.environ["APP_DB"])

# --- RIASEC đơn vị ---
Q = riasec.QUESTIONS
ok(len(Q) == 30 and all(riasec.PER[t] == 5 for t in "RIASEC"), "30 câu, mỗi nhóm 5 câu")
sc, n = riasec.score({i: 5 if Q[i][0] == "I" else 1 for i in range(30)})
ok(sc == {"R": 0, "I": 100, "A": 0, "S": 0, "E": 0, "C": 0} and n == 30, "điểm 0–100 đúng")
sc, n = riasec.score({i: 3 for i in range(30)}); ok(all(v == 50 for v in sc.values()), "toàn 3 → 50")
sc, n = riasec.score({0: 9, 1: "5", -1: 5, 99: 5, 2: 4}); ok(n == 1 and sc["A"] == 75, "bỏ qua câu/giá trị không hợp lệ")
ok(riasec.top3({"R": 10, "I": 10, "A": 90, "S": 80, "E": 0, "C": 0}) == "ASR", "top3 + phá hòa theo thứ tự RIASEC")
ok(riasec.match({"I": 100, "C": 100, "R": 100}, "ICR") == 100 and riasec.match({}, "ICR") == 0, "match 0–100")
majors = A.load()["majors"]
ok(all(len(m["riasec"]) == 3 and set(m["riasec"]) <= set("RIASEC") for m in majors), "18 ngành có mã RIASEC hợp lệ")
top = riasec.rank({"R": 0, "I": 100, "A": 0, "S": 0, "E": 0, "C": 100}, majors)
ok(top[0]["m"]["id"] in ("cntt", "taichinh"), "xếp hạng ngành theo RIASEC: " + top[0]["m"]["id"])
ok(riasec.parse_form({"q0": "5", "q1": "x", "q2": "0", "q3": "6"}) == {0: 5}, "parse_form an toàn")

# --- Dữ liệu ---
d = A.load()
ok(all(m["income"]["years"] == [2024] and len(m["income"]["vals"]) == 1 for m in majors), "mọi ngành có thu nhập Cục Thống kê năm 2024")
ok(all(s["year"] in (2024, 2025) for s in d["sources"].values()), "mọi nguồn là năm 2024–2025")
ok(all(s["url"].startswith("https://") and s.get("year") for s in d["sources"].values()), "mọi nguồn có URL + năm")
ok(all("trend" not in m for m in majors), "đã bỏ chỉ số nhu cầu bịa")
for m in majors:
    if m.get("salary_vnd"): assert m["salary_vnd"]["source"] in d["sources"]


# --- Trang con: mẫu UI riêng + làm sạch dữ liệu ---
ok(set(step_ui.UI) == {k for g in (10, 11, 12) for k in steps(g)}, "25 bước đều có UI riêng")
ok(len({tuple(w["type"] + w["id"] for w in v) for v in step_ui.UI.values()}) == 25, "25 trang con có cấu hình UI khác nhau")
MJ = [m["id"] for m in majors]
d = step_ui.parse("10-0-0", MultiDict([("mon", "ly"), ("mon", "hoa"), ("mon", "bogus"), ("mon", "ly"), ("mon.note", "x" * 5000)]), MJ)
ok(d["mon"] == ["ly", "hoa"] and len(d["mon.note"]) == 1000, "chọn môn: bỏ giá trị lạ/trùng, ghi chú ≤1000")
d = step_ui.parse("10-1-2", MultiDict([("giatri", v) for v in ["thunhap", "ondinh", "sangtao", "tudo"]]), MJ); ok(d["giatri"] == ["thunhap", "ondinh", "sangtao"], "giới hạn 3 giá trị")
d = step_ui.parse("12-1-0", MultiDict([("nv.truong", "A"), ("nv.truong", ""), ("nv.truong", "C"), ("nv.muc", "an-toan"), ("nv.muc", ""), ("nv.muc", "hack")]), MJ)
ok(d["nv"] == [{"truong": "A", "nganh": "", "muc": "an-toan", "dc": ""}, {"truong": "C", "nganh": "", "muc": "", "dc": ""}], "danh sách nguyện vọng giữ thứ tự, bỏ dòng trống + lựa chọn lạ")
d = step_ui.parse("11-0-1", MultiDict([("truong.link", "javascript:alert(1)"), ("truong.truong", "X")]), MJ); ok(d["truong"][0]["link"] == "", "chặn link javascript:")
d = step_ui.parse("12-0-1", MultiDict([("moc.ngay", "2026-13-99x"), ("moc.moc", "Thi")]), MJ); ok(d["moc"][0]["ngay"] == "", "ngày sai định dạng bị bỏ")
d = step_ui.parse("11-1-0", MultiDict([("pt.thpt", "4"), ("pt.hocba", "9")]), MJ); ok(d == {"pt.thpt": "4"}, "thang 1–5 hợp lệ")
d = step_ui.parse("10-1-1", MultiDict([("nhatky.hd", str(i)) for i in range(50)]), MJ); ok(len(d["nhatky"]) == 20, "danh sách tối đa 20 dòng")

# --- Trang công khai ---
for u in ["/", "/quiz", "/lop-10", "/lop-11", "/lop-12", "/nganh/cntt", "/nganh/nongnghiep", "/dang-ky", "/dang-nhap", "/so-sanh",
          "/so-sanh?nganh=cntt&nganh=yduoc", "/con-duong-khac", "/nguon-du-lieu", "/chinh-sach-bao-mat", "/healthz"]:
    r = c.get(u); assert r.status_code == 200, u
ok(True, "15 trang công khai trả 200")
h = c.get("/nganh/cntt").get_data(as_text=True)
ok("Cục Thống kê" in h and "chưa có số liệu 2025" in h and "cập nhật năm 2024" in h and "9,72–14,4" in h, "trang ngành có số liệu thật + nguồn + năm")
h = c.get("/nganh/nongnghiep").get_data(as_text=True); ok("chưa có số liệu – minh họa" in h, "ngành thiếu số liệu ghi rõ minh họa")
ok("cdn" not in c.get("/").get_data(as_text=True).lower() and "googleapis" not in h, "không còn CDN trong HTML")
ok(c.get("/static/vendor/chart.umd.min.js").status_code == 200 and c.get("/static/fonts/bvp-vietnamese-400.woff2").status_code == 200, "Chart.js + font tự lưu trữ")
h = c.get("/so-sanh?nganh=cntt&nganh=yduoc&nganh=luat").get_data(as_text=True)
ok(h.count('<th scope="col"><a href="/nganh/') == 3 and "ICR" in h and "Mã Holland" in h, "so sánh 3 ngành")
ok("ít nhất <b>2 ngành</b>" in c.get("/so-sanh?nganh=cntt&nganh=khongco").get_data(as_text=True), "so sánh bỏ id lạ, cần ≥2")
ok("tối đa 3" in c.get("/so-sanh?" + "&".join("nganh=" + m["id"] for m in majors[:4])).get_data(as_text=True), "so sánh >3 báo lỗi")
ok('href="/so-sanh"' in c.get("/lop-11/buoc/11-0-0").get_data(as_text=True), "Bước 'Thu hẹp ngành' có nút /so-sanh")
ok(c.get("/").get_data(as_text=True).count("/con-duong-khac") >= 2 and "/con-duong-khac" in c.get("/lop-10").get_data(as_text=True), "link con đường khác từ trang chủ + trang lớp")
h = c.get("/con-duong-khac").get_data(as_text=True)
ok(all(x in h for x in ["Cao đẳng", "Trung cấp", "Vừa học vừa làm", "Du học", "Gap year", "Quân đội", "moet.gov.vn"]), "con đường khác đủ 6 nhánh + nguồn chính thức")
h = c.get("/chinh-sach-bao-mat").get_data(as_text=True)
ok("liên hệ quản trị viên" in h and "không bán" in h and "@" not in h.split("<main")[1], "chính sách bảo mật, không email bịa")
ok("/chinh-sach-bao-mat" in c.get("/dang-ky").get_data(as_text=True), "đăng ký có dòng đồng ý chính sách")

# --- Header bảo mật, 404/500, giới hạn ---
r = c.get("/")
ok("script-src 'self'" in r.headers["Content-Security-Policy"] and r.headers["X-Frame-Options"] == "DENY" and r.headers["X-Content-Type-Options"] == "nosniff" and r.headers["Referrer-Policy"], "security headers")
ok("<script>" not in r.get_data(as_text=True) and "onclick" not in r.get_data(as_text=True), "không có script/handler inline (CSP)")
r = c.get("/khong-ton-tai"); ok(r.status_code == 404 and "Không tìm thấy trang" in r.get_data(as_text=True), "404 tiếng Việt")
ok(c.get("/nganh/xyz").status_code == 404 and c.get("/lop-9").status_code == 404, "404 ngành/lớp lạ")
r = c.get("/_boom"); ok(r.status_code == 500 and "Có lỗi xảy ra" in r.get_data(as_text=True), "500 tiếng Việt")
r = c.post("/dang-nhap", data={"x": "a" * 70000}); ok(r.status_code == 413, "giới hạn kích thước request 413")
r = c.post("/quiz", data={"q0": "5", "_csrf": tok("/quiz")}); ok(r.status_code == 400 and "ít nhất 15" in r.get_data(as_text=True), "quiz cần ≥15 câu")

# --- CSRF trên mọi POST ---
for u in ["/dang-ky", "/dang-nhap", "/dang-xuat", "/ho-so", "/ho-so/xoa", "/quiz", "/an-nhac-nho", "/api/tien-do", "/lop-10/buoc/10-0-0"]:
    assert c.post(u, data={}).status_code == 400, u
ok(True, "9 endpoint POST đều chặn khi thiếu CSRF")
r = c.post("/api/tien-do", json={"grade": 10, "done": ["10-0-0"]}, headers={"X-CSRF-Token": tok("/")}); ok(r.status_code == 200 and r.json["n"] == 1, "khách lưu tiến độ vào phiên")

# --- Trang con của từng bước ---
from grades import GRADES as G, GUIDE, href
allk = [k for g in G for k in steps(g)]
for k in allk:
    assert c.get(f"/lop-{k[:2]}/buoc/{k}").status_code == 200, k
ok(len(allk) == 25 and all(GUIDE[k]["how"] for k in allk), "25 trang con bước đều 200 + có hướng dẫn")
ok(c.get("/lop-10/buoc/10-9-9").status_code == 404 and c.get("/lop-11/buoc/10-0-0").status_code == 404 and c.get("/lop-10/buoc/abc").status_code == 404, "khóa bước lạ 404")
h = c.get("/lop-10").get_data(as_text=True)
ok('href="/quiz?buoc=10-0-1"' in h and 'href="/lop-10/buoc/10-0-2"' in h and 'data-href=' in h, "ô checklist trỏ trang con, ô trắc nghiệm trỏ /quiz")
ok('id="s10-0-0" data-step="10-0-0" data-href="/lop-10/buoc/10-0-0" aria-label="Đã xong' in h, "trang lớp hiện bước khách đã tích")
h = c.get("/lop-10/buoc/10-0-0").get_data(as_text=True)
ok('type="checkbox" name="mon" value="ly"' in h and 'name="mon.note"' in h and "Lý do mình chọn" in h and "tùy trường" in h, "trang chọn môn: ô tích môn + ghi chú lý do")
h = c.get("/lop-10/buoc/10-0-2").get_data(as_text=True)
ok(h.count('class="hc"') == 10 and "<details" in h and 'name="thoiquen.ngu.date"' in h, "trang thói quen: thẻ chọn + mở rộng + ngày bắt đầu")
ok('data-w="list"' in c.get("/lop-12/buoc/12-1-0").get_data(as_text=True) and "data-up" in c.get("/lop-12/buoc/12-1-0").get_data(as_text=True), "nguyện vọng: danh sách sắp thứ tự")
ok('data-w="rate"' in c.get("/lop-11/buoc/11-1-0").get_data(as_text=True), "phương thức xét tuyển: thang 1–5")
ok('data-w="majors"' in c.get("/lop-10/buoc/10-1-0").get_data(as_text=True), "tìm hiểu ngành: chọn ngành yêu thích")
r = c.post("/api/buoc/10-0-0", data={"mon": "ly", "_csrf": tok("/")}); ok(r.json.get("local") is True, "khách: API bước báo lưu cục bộ")
ok(c.post("/api/buoc/10-0-0", data={"mon": "ly"}).status_code == 400 and c.post("/api/buoc/9-9-9", data={"_csrf": tok("/")}).status_code == 404, "API bước chặn CSRF + khóa lạ")
h = c.get("/lop-12/buoc/12-0-1").get_data(as_text=True)
ok("Đánh dấu xong" in h and "moet.gov.vn" in h and "web không tự đưa ra" in h, "trang con có nút hoàn thành + nguồn chính thống + không bịa ngày")
t0 = tok("/lop-12/buoc/12-0-0")
r = c.post("/lop-12/buoc/12-0-0", data={"_csrf": t0, "go": "next"}); ok(r.status_code == 302 and r.location.endswith("/lop-12/buoc/12-0-1"), "hoàn thành & sang bước tiếp")
ok("Bỏ tích" in c.get("/lop-12/buoc/12-0-0").get_data(as_text=True) and "1/9" in c.get("/lop-12/buoc/12-0-0").get_data(as_text=True), "bước đã tích hiện trạng thái")
c.post("/lop-12/buoc/12-0-0", data={"_csrf": t0, "action": "undo"}); ok("Đánh dấu xong" in c.get("/lop-12/buoc/12-0-0").get_data(as_text=True), "bỏ tích bước")
ok(c.post("/lop-12/buoc/12-0-0", data={}).status_code == 400, "trang con chặn thiếu CSRF")
qg = {f"q{i}": "4" for i in range(30)}
h = c.get("/quiz?buoc=10-0-1").get_data(as_text=True); ok('name="buoc" value="10-0-1"' in h, "quiz giữ bước nguồn")
r = c.post("/quiz", data={**qg, "buoc": "10-0-1", "_csrf": tok("/quiz")}); h = r.get_data(as_text=True)
ok("Tiếp tục bước tiếp theo" in h and 'href="/lop-10/buoc/10-0-2"' in h, "kết quả quiz có nút sang bước chưa xong kế tiếp")
ok('data-step="10-0-1" data-href="/quiz?buoc=10-0-1" aria-label="Đã xong' in c.get("/lop-10").get_data(as_text=True), "làm xong quiz tự tích ô trắc nghiệm")
c.get("/lop-11"); h = c.post("/quiz", data={**qg, "_csrf": tok("/quiz")}).get_data(as_text=True)
ok('href="/lop-11/buoc/11-0-0"' in h, "quiz không có bước nguồn → dẫn tới lớp đang xem gần nhất")

# --- Đăng ký ---
r = c.post("/dang-ky", data={**R(password="123"), "_csrf": tok("/dang-ky")}); ok("ít nhất 6" in r.get_data(as_text=True), "mật khẩu ngắn")
r = c.post("/dang-ky", data={**R(password="12345678"), "_csrf": tok("/dang-ky")}); ok("dễ đoán" in r.get_data(as_text=True), "mật khẩu phổ biến bị từ chối")
r = c.post("/dang-ky", data={**R(password="an.nguyen"), "_csrf": tok("/dang-ky")}); ok("dễ đoán" in r.get_data(as_text=True), "mật khẩu = tên đăng nhập bị từ chối")
r = c.post("/dang-ky", data={**R(full_name="<script>alert(1)</script>"), "username": "xss_user", "_csrf": tok("/dang-ky")}); ok(r.status_code == 302, "đăng ký tên chứa thẻ HTML")
h = c.get("/ho-so").get_data(as_text=True); ok("<script>alert(1)" not in h and "&lt;script&gt;" in h, "XSS được escape")
c.post("/dang-xuat", data={"_csrf": tok("/")})
r = c.post("/dang-ky", data={**R(full_name="A" * 81), "_csrf": tok("/dang-ky")}); ok("tối đa 80" in r.get_data(as_text=True), "tên quá dài")
r = c.post("/dang-ky", data={**R(full_name="   "), "_csrf": tok("/dang-ky")}); ok("họ và tên" in r.get_data(as_text=True), "tên rỗng")
c.post("/api/tien-do", json={"grade": 12, "done": ["12-2-2"]}, headers={"X-CSRF-Token": tok("/")})
r = c.post("/dang-ky", data={**R(), "_csrf": tok("/dang-ky")}); ok(r.status_code == 302 and "/ho-so" in r.location, "đăng ký OK")
ck = r.headers.get("Set-Cookie", ""); ok("HttpOnly" in ck and "SameSite=Lax" in ck, "cookie HttpOnly + SameSite=Lax")
row = DBC().execute("SELECT password_hash FROM users WHERE username='an.nguyen'").fetchone()[0]
ok(PW not in row and row.startswith(("scrypt:", "pbkdf2:")), "mật khẩu đã băm")
ok("Hoàn thiện hồ sơ" in c.get("/").get_data(as_text=True), "banner nhắc hoàn thiện hồ sơ")
uid = DBC().execute("SELECT id FROM users WHERE username='an.nguyen'").fetchone()[0]
pr = dict(DBC().execute("SELECT grade, done FROM progress WHERE user_id=?", (uid,)).fetchall())
ok("12-2-2" in pr.get(12, ""), "tiến độ khách được gộp vào tài khoản khi đăng ký")
t = tok("/lop-10/buoc/10-0-0")
r = c.post("/lop-10/buoc/10-0-0", data=MultiDict([("_csrf", t), ("mon", "ly"), ("mon", "tin"), ("mon.note", "<b>thích</b> máy tính"), ("go", "next")]))
ok(r.status_code == 302 and ("10-0-1" in r.location or "10-0-2" in r.location), "lưu & hoàn thành → bước tiếp")
h = c.get("/lop-10/buoc/10-0-0").get_data(as_text=True)
ok('value="ly" checked' in h and "&lt;b&gt;thích&lt;/b&gt;" in h and "<b>thích</b>" not in h and "Bỏ tích" in h, "đăng nhập: lựa chọn + ghi chú lưu DB, escape XSS")
r = c.post("/api/buoc/10-0-2", data=MultiDict([("_csrf", t), ("thoiquen", "ngu"), ("thoiquen.ngu.date", "2026-11-01")])); ok(r.json["ok"] and r.json["n"] == 2, "API tự lưu thói quen")
h = c.get("/lop-10/buoc/10-0-2").get_data(as_text=True); ok('value="2026-11-01"' in h and 'value="ngu" checked' in h, "thói quen đã lưu hiện lại")
c.post("/lop-10/buoc/10-0-2", data={"_csrf": t, "action": "save"}); ok("Đánh dấu xong" in c.get("/lop-10/buoc/10-0-2").get_data(as_text=True), "nút Lưu không tự tích hoàn thành")
t = tok("/ho-so")
for sec, dd in [("hoan-canh", dict(grade="11", province="Hà Nội")), ("so-thich", dict(interests=["tech", "logic"])),
                ("the-manh", dict(strong_subjects=["Toán"], combo="A01")), ("du-dinh", dict(after_school="dh", target_majors=["yduoc"]))]:
    assert c.post("/ho-so", data={**dd, "section": sec, "_csrf": t}).status_code == 302
ok("Phù hợp với bạn" in c.get("/").get_data(as_text=True), "badge Phù hợp với bạn")

# --- Quiz RIASEC lưu lịch sử ---
qa = {f"q{i}": ("5" if Q[i][0] in "IC" else "2") for i in range(30)}
r = c.post("/quiz", data={**qa, "_csrf": t}); h = r.get_data(as_text=True)
ok(r.status_code == 200 and "Đã lưu kết quả" in h and "không phải chẩn đoán" in h and 'id="rdata"' in h, "quiz RIASEC + lưu + disclaimer + radar")
qa2 = {f"q{i}": ("5" if Q[i][0] in "SA" else "1") for i in range(30)}; c.post("/quiz", data={**qa2, "_csrf": t})
rows = DBC().execute("SELECT code, grade FROM riasec_results WHERE user_id=? ORDER BY id", (uid,)).fetchall()
ok(len(rows) == 2 and rows[0][0][:2] in ("IC", "CI") and rows[0][1] == 11, "lưu lịch sử điểm + lớp: " + str(rows))
h = c.get("/ho-so").get_data(as_text=True); ok("Kết quả trắc nghiệm Holland" in h and "So với lần đầu" in h and rows[1][0] in h, "bảng lịch sử + xu hướng trên /ho-so")

# --- Tiến độ trang lớp ---
H = {"X-CSRF-Token": tok("/")}
ks = steps(11)
r = c.post("/api/tien-do", json={"grade": 11, "done": ks[:3] + ["bogus", "10-0-0"]}, headers=H)
ok(r.status_code == 200 and r.json["n"] == 3, "lưu tiến độ, lọc khóa không hợp lệ")
r = c.post("/api/tien-do", json={"grade": 11, "done": [ks[5]], "merge": True}, headers=H); ok(r.json["n"] == 4, "gộp tiến độ khách vào tài khoản")
ok(c.post("/api/tien-do", json={"grade": 9, "done": []}, headers=H).status_code == 400, "lớp không hợp lệ 400")
ok(c.post("/api/tien-do", json={"grade": 11, "done": []}, headers={"X-CSRF-Token": "sai"}).status_code == 400, "API tiến độ chặn CSRF sai")
c.post("/api/tien-do", json={"grade": 11, "done": ks[:4]}, headers=H)
ok(f"4/{len(ks)} bước đã làm" in c.get("/").get_data(as_text=True), "thẻ lớp trên trang chủ hiện x/y")
ok('checked' in c.get("/lop-11").get_data(as_text=True), "trang lớp hiện bước đã tick")

# --- Đăng nhập + giới hạn ---
c.post("/dang-xuat", data={"_csrf": tok("/")}); ok(c.get("/ho-so").status_code == 302, "đăng xuất")
ok(c.post("/dang-nhap", data={"username": "an.nguyen", "password": PW, "_csrf": tok("/dang-nhap"), "next": "//evil.com"}).location == "/", "chặn open redirect")
c.post("/dang-xuat", data={"_csrf": tok("/")})
for i in range(5):
    r = c.post("/dang-nhap", data={"username": "an.nguyen", "password": "sai", "_csrf": tok("/dang-nhap")})
ok(r.status_code == 401, "sai mật khẩu 401")
r = c.post("/dang-nhap", data={"username": "an.nguyen", "password": PW, "_csrf": tok("/dang-nhap")})
ok(r.status_code == 429 and "sai nhiều lần" in r.get_data(as_text=True), "khóa tạm sau 5 lần sai (kể cả mật khẩu đúng)")
c2 = A.app.test_client()
r = c2.post("/dang-nhap", data={"username": "an.nguyen", "password": PW, "_csrf": tok("/dang-nhap", c2)}, environ_base={"REMOTE_ADDR": "10.0.0.9"})
ok(r.status_code == 302, "IP khác vẫn đăng nhập được")
with A.app.app_context():
    auth.db().execute("UPDATE login_attempts SET locked_until=0"); auth.db().commit()
r = c.post("/dang-nhap", data={"username": "an.nguyen", "password": PW, "_csrf": tok("/dang-nhap")}); ok(r.status_code == 302, "hết khóa → đăng nhập OK")

# --- Xóa tài khoản ---
t = tok("/ho-so/xoa"); ok(c.post("/ho-so/xoa", data={"confirm": "no", "_csrf": t}).status_code == 400, "xóa cần xác nhận")
c.post("/ho-so/xoa", data={"confirm": "XOA", "_csrf": t}); db = DBC()
ok(all(db.execute(f"SELECT count(*) FROM {tb} WHERE user_id=?", (uid,)).fetchone()[0] == 0 for tb in ("profiles", "riasec_results", "progress", "quiz_results", "step_data")), "xóa tài khoản + toàn bộ dữ liệu (cascade)")

# --- Cơ sở khoa học & hành động ---
r = c.get("/co-so-khoa-hoc"); ok(r.status_code == 200 and "Cơ sở khoa học" in r.get_data(as_text=True) and "không thay thế tư vấn" in r.get_data(as_text=True), "/co-so-khoa-hoc 200 + lưu ý")
allk = [k for g in A.GRADES for k in steps(g)]
ok(set(A.ACTIONS) == set(allk), "mọi bước có dữ liệu hành động")
ok(all(A.ACTIONS[k] and all(a["refs"] and all(r in A.RESEARCH for r in a["refs"]) and a["why"] for a in A.ACTIONS[k]) for k in allk), "không bước/hành động nào thiếu nguồn")
ok(all(re.match(r"^https?://[^\s]+$", x["url"]) and x["authors"] and x["year"] and x["limits"] for x in A.RESEARCH.values()), "mọi trích dẫn có url http(s), tác giả, năm, giới hạn")
ok(all(any(x["id"] in a["refs"] for v in A.ACTIONS.values() for a in v) for x in A.RESEARCH.values()), "mọi nghiên cứu đều được dùng")
for k in allk:
    h = c.get(f"/lop-{k.split('-')[0]}/buoc/{k}").get_data(as_text=True)
    assert "Thực hiện hành động" in h and 'aria-expanded="false"' in h and ("doi.org" in h or "vbpl.vn" in h), k
ok(True, "25 trang con có khối hành động + accordion cơ sở khoa học")
ok("/co-so-khoa-hoc" in c.get("/").get_data(as_text=True), "footer có link cơ sở khoa học")

# --- SEO ---
import html as _html
from grades import steps as _steps
pages = ["/", "/lop-10", "/lop-11", "/lop-12", "/lop-10/buoc/10-0-0", "/lop-12/buoc/12-2-2", "/nganh/cntt", "/quiz", "/so-sanh", "/con-duong-khac", "/nguon-du-lieu", "/co-so-khoa-hoc", "/chinh-sach-bao-mat"]
pages += ["/nganh/" + m["id"] for m in A.load()["majors"]] + [href(k) for g in (10,11,12) for k in _steps(g) if k != "10-0-1"]
pages = list(dict.fromkeys(pages))
titles, descs = {}, {}
c3 = A.app.test_client()
for pth in pages:
    r = c3.get(pth); h = r.get_data(as_text=True); assert r.status_code == 200, pth
    t1 = re.search(r"<title>(.*?)</title>", h, re.S).group(1).strip(); titles.setdefault(t1, []).append(pth)
    d1 = re.search(r'<meta name="description" content="([^"]*)"', h).group(1); descs.setdefault(d1, []).append(pth)
    assert len(re.findall(r"<h1[ >]", h)) == 1, pth
    can = re.search(r'<link rel="canonical" href="([^"]+)"', h).group(1); assert can == "https://huongnghiep.myagentvn.com" + pth.split("?")[0], (pth, can)
    assert 'property="og:image" content="https://' in h and 'twitter:card' in h and "index, follow" in h, pth
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S): json.loads(blob)
    if pth.startswith(("/lop-", "/nganh/")): assert '"BreadcrumbList"' in h and 'class="crumbs"' in h, pth
ok(all(len(v) == 1 for v in titles.values()), f"title riêng cho {len(pages)} trang công khai")
ok(len(descs) >= len(pages) - 1, "meta description khác nhau giữa các trang")
h = c3.get("/").get_data(as_text=True); ok('"WebSite"' in h and '"Organization"' in h, "JSON-LD trang chủ")
ok('"Occupation"' in c3.get("/nganh/cntt").get_data(as_text=True), "JSON-LD Occupation trang ngành")
r = c3.get("/robots.txt"); b = r.get_data(as_text=True)
ok(r.status_code == 200 and "Disallow: /ho-so" in b and "Disallow: /dang-nhap" in b and "Disallow: /api/" in b and "Sitemap: https://huongnghiep.myagentvn.com/sitemap.xml" in b, "robots.txt")
r = c3.get("/sitemap.xml"); b = r.get_data(as_text=True)
import xml.dom.minidom as _md; _md.parseString(b)
locs = re.findall(r"<loc>(.*?)</loc>", b)
ok(r.status_code == 200 and all(l.startswith("https://") for l in locs) and "https://huongnghiep.myagentvn.com/nganh/cntt" in locs and len(locs) >= len(pages) and not any("/ho-so" in l or "/dang-" in l for l in locs), f"sitemap.xml ({len(locs)} URL)")
for pth in ("/dang-nhap", "/dang-ky"):
    ok("noindex" in c3.get(pth).get_data(as_text=True), f"noindex {pth}")
ok(c3.get("/favicon.ico").status_code == 200 and c3.get("/static/img/og.png").status_code == 200, "favicon + og.png")
r = c3.get("/", headers={"Accept-Encoding": "gzip"}); ok(r.headers.get("Content-Encoding") == "gzip", "gzip HTML")

# UX pass
cu = A.app.test_client(); h = cu.get("/").get_data(as_text=True)
ok("không cần đăng ký" in h and 'data-more="mgrid"' in h and "resume card" not in h, "trang chủ khách mới: thông điệp + xem thêm ngành")
cu.get("/lop-11"); h = cu.get("/").get_data(as_text=True); ok("Tiếp tục lớp 11" in h and "Tiếp tục từ chỗ bạn dừng" in h, "trang chủ: tiếp tục từ chỗ dừng")
h = cu.get("/lop-11").get_data(as_text=True); ok('class="nextcta"' in h and "Bắt đầu" in h, "trang lớp: CTA bước tiếp theo")
h = cu.get("/lop-10/buoc/10-0-0").get_data(as_text=True); ok('sact sticky' in h, "trang con: thanh hành động dính")

# UX pass 2
cu = A.app.test_client(); h = cu.get("/lop-10/buoc/10-0-0").get_data(as_text=True)
ok('class="has-sact"' in h and "Chưa hoàn thành" not in h, "trang con: thanh cố định + đầu trang gọn")
h = cu.get("/so-sanh?nganh=xx&nganh=cntt").get_data(as_text=True); ok("không còn tồn tại" in h, "so sánh: báo ngành sai")
ok("không còn tồn tại" not in cu.get("/so-sanh?nganh=cntt&nganh=marketing").get_data(as_text=True), "so sánh: không báo nhầm")
h = cu.get("/quiz").get_data(as_text=True); ok('data-min="15"' in h and 'id="qerr"' in h and "khoảng 4 phút" in h, "quiz: kiểm tra phía trình duyệt")

# Admin tắt khi không đặt ADMIN_PATH
ok(c.get("/_/abcdefghijklmnopqrst/").status_code == 404 and c.get("/admin").status_code == 404 and c.get("/_/abcdefghijklmnopqrst/dang-nhap").status_code == 404, "admin tắt → 404")
import subprocess, sys
_env = {k: v for k, v in os.environ.items() if k not in ("DATA_DIR", "APP_DB", "ADMIN_PATH")}
_r = subprocess.run([sys.executable, "test_admin.py"], capture_output=True, text=True, env=_env, cwd=os.path.dirname(os.path.abspath(__file__)))
print(_r.stdout[-3000:], _r.stderr[-3000:]); _m = re.search(r"ADMIN OK – (\d+)", _r.stdout)
ok(_r.returncode == 0 and _m, "bộ kiểm thử admin"); N[0] += int(_m.group(1)) - 1
print(f"ALL OK – {N[0]} kiểm thử")
