"""Quản lý tài khoản admin (chạy trên server, cùng DATA_DIR/APP_DB với web).
  python admin_cli.py create-admin <tên>      # tạo mới hoặc đặt lại mật khẩu
  python admin_cli.py delete-admin <tên>
  python admin_cli.py list-admins
Mật khẩu: nhập qua prompt ẩn, hoặc biến môi trường ADMIN_PASSWORD (chỉ đọc lúc chạy lệnh). Không bao giờ in ra."""
import os, sys, getpass, sqlite3
import auth, admin
from werkzeug.security import generate_password_hash
def main(a):
    auth.init_db(); admin.init_db(); c = sqlite3.connect(auth.DB)
    if len(a) == 2 and a[0] == "create-admin":
        u = a[1].strip()
        if not auth.USER_RE.match(u): sys.exit("Tên admin 3–30 ký tự: chữ không dấu, số, _ hoặc .")
        pw = os.environ.get("ADMIN_PASSWORD") or getpass.getpass("Mật khẩu admin (≥12 ký tự): ")
        if not os.environ.get("ADMIN_PASSWORD") and getpass.getpass("Nhập lại: ") != pw: sys.exit("Hai lần nhập không khớp.")
        if len(pw) < 12 or auth.is_common(pw, u): sys.exit("Mật khẩu cần ≥12 ký tự và không dễ đoán.")
        h = generate_password_hash(pw); del pw
        if c.execute("SELECT 1 FROM admin_users WHERE username=?", (u,)).fetchone():
            c.execute("UPDATE admin_users SET password_hash=? WHERE username=?", (h, u))
            c.execute("DELETE FROM admin_sessions WHERE admin_id=(SELECT id FROM admin_users WHERE username=?)", (u,)); print("Đã đặt lại mật khẩu cho", u)
        else:
            c.execute("INSERT INTO admin_users(username,password_hash,created_at) VALUES(?,?,?)", (u, h, auth.now())); print("Đã tạo admin", u)
    elif len(a) == 2 and a[0] == "delete-admin":
        n = c.execute("DELETE FROM admin_users WHERE username=?", (a[1],)).rowcount; print("Đã xóa" if n else "Không có admin này")
    elif a == ["list-admins"]:
        for r in c.execute("SELECT username, created_at, last_login_at FROM admin_users"): print(*r)
    else: sys.exit(__doc__)
    c.commit(); c.close()
if __name__ == "__main__": main(sys.argv[1:])
