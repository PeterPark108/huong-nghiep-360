"""Kiểm thử: .venv/bin/python test_app.py"""
import os, re, sqlite3, tempfile, json
os.environ["DATA_DIR"] = tempfile.mkdtemp(); os.environ["APP_DB"] = os.path.join(os.environ["DATA_DIR"], "t.db")
import app as A, riasec, auth
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
ok(all(m["income"]["vals"] and len(m["income"]["vals"]) == 3 for m in majors), "mọi ngành có chuỗi thu nhập TCTK 3 năm")
ok(all(s["url"].startswith("https://") and s.get("year") for s in d["sources"].values()), "mọi nguồn có URL + năm")
ok(all("trend" not in m for m in majors), "đã bỏ chỉ số nhu cầu bịa")
for m in majors:
    if m.get("salary_vnd"): assert m["salary_vnd"]["source"] in d["sources"]

# --- Trang công khai ---
for u in ["/", "/quiz", "/lop-10", "/lop-11", "/lop-12", "/nganh/cntt", "/nganh/nongnghiep", "/dang-ky", "/dang-nhap", "/so-sanh",
          "/so-sanh?nganh=cntt&nganh=yduoc", "/con-duong-khac", "/nguon-du-lieu", "/chinh-sach-bao-mat", "/healthz"]:
    r = c.get(u); assert r.status_code == 200, u
ok(True, "15 trang công khai trả 200")
h = c.get("/nganh/cntt").get_data(as_text=True)
ok("Tổng cục Thống kê" in h and "cập nhật năm 2024" in h and "9,72–14,4" in h, "trang ngành có số liệu thật + nguồn + năm")
h = c.get("/nganh/nongnghiep").get_data(as_text=True); ok("chưa có số liệu – minh họa" in h, "ngành thiếu số liệu ghi rõ minh họa")
ok("cdn" not in c.get("/").get_data(as_text=True).lower() and "googleapis" not in h, "không còn CDN trong HTML")
ok(c.get("/static/vendor/chart.umd.min.js").status_code == 200 and c.get("/static/fonts/bvp-vietnamese-400.woff2").status_code == 200, "Chart.js + font tự lưu trữ")
h = c.get("/so-sanh?nganh=cntt&nganh=yduoc&nganh=luat").get_data(as_text=True)
ok(h.count('<th scope="col"><a href="/nganh/') == 3 and "ICR" in h and "Mã Holland" in h, "so sánh 3 ngành")
ok("ít nhất <b>2 ngành</b>" in c.get("/so-sanh?nganh=cntt&nganh=khongco").get_data(as_text=True), "so sánh bỏ id lạ, cần ≥2")
ok("tối đa 3" in c.get("/so-sanh?" + "&".join("nganh=" + m["id"] for m in majors[:4])).get_data(as_text=True), "so sánh >3 báo lỗi")
ok('href="/so-sanh"' in c.get("/lop-11").get_data(as_text=True), "Lớp 11 'So sánh ngành' trỏ /so-sanh")
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
for u in ["/dang-ky", "/dang-nhap", "/dang-xuat", "/ho-so", "/ho-so/xoa", "/quiz", "/an-nhac-nho", "/api/tien-do"]:
    assert c.post(u, data={}).status_code == 400, u
ok(True, "8 endpoint POST đều chặn khi thiếu CSRF")
r = c.post("/api/tien-do", json={"grade": 10, "done": []}, headers={"X-CSRF-Token": tok("/")}); ok(r.status_code == 401, "API tiến độ cần đăng nhập")

# --- Đăng ký ---
r = c.post("/dang-ky", data={**R(password="123"), "_csrf": tok("/dang-ky")}); ok("ít nhất 6" in r.get_data(as_text=True), "mật khẩu ngắn")
r = c.post("/dang-ky", data={**R(password="12345678"), "_csrf": tok("/dang-ky")}); ok("dễ đoán" in r.get_data(as_text=True), "mật khẩu phổ biến bị từ chối")
r = c.post("/dang-ky", data={**R(password="an.nguyen"), "_csrf": tok("/dang-ky")}); ok("dễ đoán" in r.get_data(as_text=True), "mật khẩu = tên đăng nhập bị từ chối")
r = c.post("/dang-ky", data={**R(full_name="<script>alert(1)</script>"), "username": "xss_user", "_csrf": tok("/dang-ky")}); ok(r.status_code == 302, "đăng ký tên chứa thẻ HTML")
h = c.get("/ho-so").get_data(as_text=True); ok("<script>alert(1)" not in h and "&lt;script&gt;" in h, "XSS được escape")
c.post("/dang-xuat", data={"_csrf": tok("/")})
r = c.post("/dang-ky", data={**R(full_name="A" * 81), "_csrf": tok("/dang-ky")}); ok("tối đa 80" in r.get_data(as_text=True), "tên quá dài")
r = c.post("/dang-ky", data={**R(full_name="   "), "_csrf": tok("/dang-ky")}); ok("họ và tên" in r.get_data(as_text=True), "tên rỗng")
r = c.post("/dang-ky", data={**R(), "_csrf": tok("/dang-ky")}); ok(r.status_code == 302 and "/ho-so" in r.location, "đăng ký OK")
ck = r.headers.get("Set-Cookie", ""); ok("HttpOnly" in ck and "SameSite=Lax" in ck, "cookie HttpOnly + SameSite=Lax")
row = DBC().execute("SELECT password_hash FROM users WHERE username='an.nguyen'").fetchone()[0]
ok(PW not in row and row.startswith(("scrypt:", "pbkdf2:")), "mật khẩu đã băm")
ok("Hoàn thiện hồ sơ" in c.get("/").get_data(as_text=True), "banner nhắc hoàn thiện hồ sơ")
uid = DBC().execute("SELECT id FROM users WHERE username='an.nguyen'").fetchone()[0]
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
ok(all(db.execute(f"SELECT count(*) FROM {tb} WHERE user_id=?", (uid,)).fetchone()[0] == 0 for tb in ("profiles", "riasec_results", "progress", "quiz_results")), "xóa tài khoản + toàn bộ dữ liệu (cascade)")
print(f"ALL OK – {N[0]} kiểm thử")
