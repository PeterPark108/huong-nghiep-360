"""Trắc nghiệm sở thích nghề nghiệp theo mô hình Holland (RIASEC)."""
TYPES = {
 "R": dict(name="Kỹ thuật (Realistic)", short="Kỹ thuật", icon="🔧", color="#e07a5f",
           desc="Thích làm việc với đồ vật, máy móc, cây cối, động vật; thích làm bằng tay và thấy kết quả cụ thể."),
 "I": dict(name="Nghiên cứu (Investigative)", short="Nghiên cứu", icon="🔬", color="#3d5a80",
           desc="Tò mò, thích tìm hiểu, phân tích, giải quyết vấn đề bằng tư duy và dữ liệu."),
 "A": dict(name="Nghệ thuật (Artistic)", short="Nghệ thuật", icon="🎨", color="#9b5de5",
           desc="Giàu trí tưởng tượng, thích sáng tạo, tự do thể hiện bằng hình ảnh, âm thanh, chữ viết."),
 "S": dict(name="Xã hội (Social)", short="Xã hội", icon="🤝", color="#0f8a7e",
           desc="Thích giúp đỡ, dạy bảo, chăm sóc, lắng nghe và làm việc cùng mọi người."),
 "E": dict(name="Quản lý (Enterprising)", short="Quản lý", icon="🚀", color="#f2a900",
           desc="Năng động, thích thuyết phục, dẫn dắt, kinh doanh và chấp nhận thử thách."),
 "C": dict(name="Nghiệp vụ (Conventional)", short="Nghiệp vụ", icon="🗂️", color="#5b6478",
           desc="Cẩn thận, ngăn nắp, thích làm việc có quy trình rõ ràng, với số liệu và hồ sơ."),
}
QUESTIONS = [
 ("R","Tự sửa xe đạp, quạt điện hoặc đồ dùng bị hỏng"),
 ("I","Tìm hiểu vì sao một hiện tượng tự nhiên xảy ra"),
 ("A","Vẽ, thiết kế poster hoặc trang trí lớp học"),
 ("S","Giảng bài cho bạn khi bạn chưa hiểu"),
 ("E","Đứng ra tổ chức một sự kiện của lớp"),
 ("C","Sắp xếp tài liệu, ghi chép gọn gàng theo thứ tự"),
 ("R","Lắp ráp mô hình, đồ chơi kỹ thuật hoặc robot"),
 ("I","Giải các bài toán khó hoặc câu đố logic"),
 ("A","Viết truyện, thơ, lời bài hát hoặc kịch bản"),
 ("S","Lắng nghe và an ủi khi bạn bè gặp chuyện buồn"),
 ("E","Thuyết phục người khác đồng ý với ý tưởng của mình"),
 ("C","Theo dõi chi tiêu, lập bảng tính số liệu"),
 ("R","Làm việc ngoài trời: trồng cây, chăm vật nuôi"),
 ("I","Làm thí nghiệm ở phòng thực hành Lý, Hóa, Sinh"),
 ("A","Chụp ảnh, quay và dựng video"),
 ("S","Tham gia hoạt động tình nguyện giúp cộng đồng"),
 ("E","Bán hàng online hoặc thử kinh doanh nhỏ"),
 ("C","Kiểm tra lỗi chính tả, số liệu cho cả nhóm"),
 ("R","Dùng dụng cụ như tua vít, máy khoan, máy may"),
 ("I","Đọc sách, xem video về khoa học, công nghệ, vũ trụ"),
 ("A","Chơi nhạc cụ, hát, nhảy hoặc diễn kịch"),
 ("S","Chăm sóc em nhỏ, người già hoặc người bị ốm"),
 ("E","Làm lớp trưởng, trưởng nhóm, dẫn dắt mọi người"),
 ("C","Lập kế hoạch, thời gian biểu chi tiết và làm đúng theo đó"),
 ("R","Xem cách máy móc, động cơ hoạt động bên trong"),
 ("I","Phân tích dữ liệu, tìm quy luật trong các con số"),
 ("A","Nghĩ ra ý tưởng mới lạ, khác với mọi người"),
 ("S","Làm việc nhóm và giúp mọi người hòa thuận"),
 ("E","Tranh luận, thuyết trình trước đám đông"),
 ("C","Làm công việc cần chính xác, tỉ mỉ, theo quy trình"),
]
LIKERT = [(1,"Rất không thích"),(2,"Không thích"),(3,"Bình thường"),(4,"Thích"),(5,"Rất thích")]
PER = {t: sum(1 for q, _ in QUESTIONS if q == t) for t in TYPES}

def score(answers):
    """answers: {index: 1..5}. Trả về điểm 0–100 cho mỗi nhóm (chỉ tính câu đã trả lời), và số câu đã trả lời."""
    tot, cnt = {t: 0 for t in TYPES}, {t: 0 for t in TYPES}
    for i, v in answers.items():
        if isinstance(i, int) and 0 <= i < len(QUESTIONS) and v in (1, 2, 3, 4, 5):
            t = QUESTIONS[i][0]; tot[t] += v; cnt[t] += 1
    return {t: (round((tot[t] - cnt[t]) / (4 * cnt[t]) * 100) if cnt[t] else 0) for t in TYPES}, sum(cnt.values())

def top3(sc):
    return "".join(sorted(TYPES, key=lambda t: (-sc[t], "RIASEC".index(t)))[:3])

W = (3, 2, 1)
def match(sc, code):
    """Độ phù hợp 0–100 giữa điểm RIASEC và mã Holland 3 chữ của ngành (trọng số 3-2-1)."""
    return round(sum(w * sc.get(c, 0) for w, c in zip(W, code)) / sum(W[:len(code)]))

def rank(sc, majors, n=5):
    r = sorted(majors, key=lambda m: -match(sc, m["riasec"]))
    out = []
    for m in r[:n]:
        strong = [TYPES[c]["short"] for c in m["riasec"] if sc.get(c, 0) >= 50]
        out.append(dict(m=m, pct=match(sc, m["riasec"]), why=strong))
    return out

def parse_form(form):
    a = {}
    for i in range(len(QUESTIONS)):
        v = form.get(f"q{i}", "")
        if v.isdigit() and 1 <= int(v) <= 5: a[i] = int(v)
    return a
