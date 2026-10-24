# Hướng Nghiệp 360

Web hướng nghiệp cho học sinh lớp 10–12 (Flask + SQLite, tiếng Việt).

## Chạy thử trên máy
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py              # http://127.0.0.1:5000 (debug tắt)
.venv/bin/python test_app.py         # kiểm thử
```

## Tính năng
- Trang ngành (`/nganh/<id>`): thu nhập bình quân **ngành kinh tế liên quan** (TCTK 2022–2024), lương khởi điểm/thị trường khi có nguồn, dữ kiện nhu cầu có nguồn. Thiếu số liệu → ghi "chưa có số liệu – minh họa", không vẽ biểu đồ bịa.
- `/nguon-du-lieu`: toàn bộ nguồn, năm, cách quy đổi, độ phủ dữ liệu.
- `/quiz`: trắc nghiệm Holland/RIASEC 30 câu Likert 1–5 → điểm 0–100 mỗi nhóm, mã 3 chữ, radar, ngành phù hợp (mỗi ngành có mã `riasec`, độ khớp trọng số 3-2-1). Chỉ để tham khảo, không phải chẩn đoán.
- `/so-sanh?nganh=a&nganh=b[&nganh=c]`: so sánh 2–3 ngành; chọn bằng checkbox trên thẻ, thanh so sánh dính đáy (localStorage `hn360:compare`).
- `/lop-10|11|12`: checklist; khách lưu localStorage (`hn360:progress:<lớp>`), đã đăng nhập đồng bộ `POST /api/tien-do` (JSON, header `X-CSRF-Token`). Trang chủ hiện "x/y bước đã làm".
- `/con-duong-khac`: cao đẳng, trung cấp, vừa học vừa làm, du học, gap year, quân đội/công an + link chính thức.
- `/chinh-sach-bao-mat`: chính sách cho người dùng dưới 18 tuổi.

## Mô hình dữ liệu (SQLite, `DATA_DIR/app.db`)
| Bảng | Cột chính |
|---|---|
| users | id, username (unique, lower), password_hash (scrypt), full_name, school, created_at |
| profiles | user_id PK, grade, province, interests/strong_subjects/target_majors (JSON), combo, after_school, … |
| riasec_results | id, user_id, created_at, grade (lớp lúc làm), scores (JSON R..C 0–100), code (3 chữ), answered |
| progress | (user_id, grade) PK, done (JSON danh sách khóa bước `lớp-giai đoạn-mục`), updated_at |
| login_attempts | key (ip / ip+user), fails, first_at, locked_until — chống dò mật khẩu |
| quiz_results | bảng cũ (v3), giữ để tương thích |
Mọi bảng con `ON DELETE CASCADE` — xóa tài khoản xóa sạch dữ liệu.

`data/careers.json`: `sources{id:{name,url,year,note}}`, `gso_sectors{mã VSIC:{name,v:[2022,2023,2024] nghìn đồng}}`, `gso_all`, mỗi ngành: `gso_sector`, `riasec`, `salary_vnd{min,max,unit,note,source}` (tùy chọn), `facts[{text,source}]`.

## Bảo mật
CSRF cho mọi POST; CSP `script-src 'self'` (không có JS inline), font + Chart.js tự lưu trữ; cookie HttpOnly/SameSite=Lax/Secure; khóa đăng nhập sau 5 lần sai (theo IP+tài khoản) hoặc 30 lần (theo IP), thời gian tăng dần tới 15 phút; giới hạn request 64 KB; chặn mật khẩu phổ biến; chặn open-redirect.

## Triển khai
Biến môi trường:
| Biến | Ý nghĩa | Mặc định |
|---|---|---|
| `SECRET_KEY` | khóa ký phiên — **bắt buộc đặt trong production** | tự sinh, lưu `DATA_DIR/.secret_key` |
| `DATA_DIR` | thư mục chứa SQLite (cần ổ đĩa bền) | `data/` |
| `PORT` | cổng gunicorn | 5000 |
| `SESSION_COOKIE_SECURE` | đặt `1` khi chạy HTTPS (bật luôn HSTS) | `0` |
| `TRUST_PROXY` | `1` khi đứng sau reverse proxy (Render, Nginx) để lấy IP thật | `0` |
| `WEB_CONCURRENCY` | số worker | 2 |

Chạy production (không dùng server debug):
```bash
SECRET_KEY=$(python3 -c 'import secrets;print(secrets.token_hex(32))') \
  .venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
```
- **Docker:** `docker build -t hn360 . && docker run -p 5000:5000 -e SECRET_KEY=... -v hn360data:/data hn360`
- **Render:** đẩy repo lên GitHub → New → Blueprint → chọn repo (`render.yaml` có sẵn, kèm disk 1 GB ở `/var/data`, health check `/healthz`).
- **Heroku/Railway:** dùng `Procfile`; lưu ý ổ đĩa tạm thời sẽ mất SQLite khi khởi động lại — cần volume.
Trên HTTPS nhớ đặt `SESSION_COOKIE_SECURE=1` (render.yaml đã đặt sẵn).
