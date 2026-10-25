"""Giao diện riêng cho từng trang con của bước + làm sạch dữ liệu người dùng nhập.
Mẫu UI (widget): pick (danh sách tích), chips (thẻ chọn nhanh), cards (thẻ chọn + mở rộng), rate (thang 1–5),
fields (biểu mẫu nhiều ô), list (danh sách tự thêm; có thể sắp thứ tự/chấm điểm), majors (chọn ngành), quiz."""
import re, json
TXT, NOTE, MAXROWS, MAXJSON = 200, 1000, 20, 24000
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$"); MONTH = re.compile(r"^\d{4}-\d{2}$")
LV = [("mo-uoc", "Mơ ước"), ("phu-hop", "Phù hợp"), ("an-toan", "An toàn")]
S15 = [(str(i), str(i)) for i in range(1, 6)]
def W(t, i, title, **k): return dict(type=t, id=i, title=title, **k)
def C(i, title, how, tip=""): return dict(id=i, title=title, how=how, tip=tip)

UI = {
 "10-0-0": [
  W("info", "batbuoc", "📚 Môn bắt buộc (mọi học sinh đều học)", items=["Ngữ văn", "Toán", "Ngoại ngữ 1", "Lịch sử", "Giáo dục thể chất", "Giáo dục quốc phòng và an ninh", "Hoạt động trải nghiệm, hướng nghiệp", "Nội dung giáo dục của địa phương"],
    hint="Theo chương trình GDPT 2018 (đã sửa đổi bởi Thông tư 13/2022/TT-BGDĐT)."),
  W("pick", "mon", "✅ Môn học lựa chọn mình muốn học", style="subj", target=4, note="Lý do mình chọn",
    hint="Chương trình quy định chọn 4 môn trong nhóm dưới đây. Môn nào được mở và ghép thành nhóm/tổ hợp thế nào là tùy trường – xem thông báo của trường.",
    options=[("dia", "Địa lí", "Xã hội"), ("ktpl", "Giáo dục kinh tế và pháp luật", "Xã hội"), ("ly", "Vật lí", "Tự nhiên"), ("hoa", "Hóa học", "Tự nhiên"), ("sinh", "Sinh học", "Tự nhiên"),
             ("cn", "Công nghệ", "Công nghệ & Nghệ thuật"), ("tin", "Tin học", "Công nghệ & Nghệ thuật"), ("nhac", "Âm nhạc", "Công nghệ & Nghệ thuật"), ("mt", "Mĩ thuật", "Công nghệ & Nghệ thuật")]),
  W("fields", "truong", "🏫 Thông tin từ trường mình", fields=["Các nhóm môn/tổ hợp trường mình mở (ghi theo thông báo của trường)"])],
 "10-0-1": [W("quiz", "quiz", "🧭 Trắc nghiệm sở thích Holland")],
 "10-0-2": [W("cards", "thoiquen", "🌟 Chọn thói quen mình sẽ xây", date="Bắt đầu từ ngày", hint="Bấm vào thẻ để xem cách làm. Tích những thói quen bạn cam kết thử – bắt đầu 2–3 cái là đủ.", cards=[
   C("tgb", "🗓️ Lập thời gian biểu tuần", "Kẻ bảng 7 ngày: giờ học trên lớp, giờ tự học từng môn, giờ nghỉ và giờ ngủ. Dán ở góc học tập.", "Để trống vài ô dự phòng – lịch quá kín rất dễ bỏ."),
   C("on", "🔁 Ôn bài ngay trong ngày", "Tối cùng ngày, đọc lại vở ghi 10–15 phút và tự tóm tắt bài bằng vài dòng.", "Viết 1 câu hỏi về chỗ chưa hiểu để hỏi thầy cô hôm sau."),
   C("deu", "📈 Học đều, không dồn", "Chia ôn tập thành nhiều buổi ngắn trong tuần thay vì thức khuya trước hôm kiểm tra.", "Đánh dấu ngày kiểm tra lên lịch, lùi lại 1 tuần để bắt đầu ôn."),
   C("nhom", "👥 Học nhóm", "Nhóm 3–4 bạn, mỗi buổi có mục tiêu rõ (giải đề, giảng lại bài cho nhau).", "Giảng lại cho bạn là cách kiểm tra mình hiểu thật chưa."),
   C("ngu", "😴 Ngủ đủ giấc", "Đi ngủ và thức dậy cùng giờ mỗi ngày, kể cả cuối tuần.", "Cất điện thoại xa giường 30 phút trước khi ngủ."),
   C("dt", "📵 Hạn chế điện thoại khi học", "Bật chế độ không làm phiền hoặc để điện thoại ở phòng khác trong giờ tự học.", "Chỉ xem tin nhắn trong giờ nghỉ giữa các phiên."),
   C("phien", "⏱️ Chia phiên học có nghỉ", "Học tập trung khoảng 25–45 phút rồi nghỉ ngắn 5–10 phút, đứng dậy vận động.", "Ghi việc cụ thể cho mỗi phiên, ví dụ “làm 5 bài hình”."),
   C("tukt", "❓ Tự kiểm tra", "Gấp sách lại, tự trả lời câu hỏi hoặc làm bài tập thay vì chỉ đọc đi đọc lại.", "Làm flashcard cho công thức, từ vựng."),
   C("truoc", "📖 Đọc trước bài mới", "Lướt bài hôm sau 5–10 phút, gạch chỗ chưa hiểu để nghe giảng kỹ hơn.", ""),
   C("tongket", "📝 Tổng kết cuối tuần", "Dành 5 phút cuối tuần: tuần này làm được gì, chưa được gì, tuần sau chỉnh gì.", "")])],
 "10-1-0": [W("majors", "nganh", "💡 Chọn ngành mình thấy thú vị", hint="Bấm “Xem” để đọc kỹ, tích ngành muốn lưu vào danh sách yêu thích (tối đa 8).", max=8),
  W("fields", "ghi", "✍️ Ghi chép", fields=["Điều bất ngờ mình mới biết về các ngành"])],
 "10-1-1": [W("chips", "loai", "🎨 Loại hoạt động mình muốn thử", hint="Chọn 1–2 loại khác nhau (ví dụ 1 học thuật + 1 nghệ thuật/xã hội).", options=[
   ("hocthuat", "🔬 CLB học thuật"), ("thethao", "⚽ Thể thao"), ("nghethuat", "🎭 Nghệ thuật"), ("tinhnguyen", "🤝 Tình nguyện"), ("cuocthi", "🏆 Cuộc thi"), ("truyenthong", "📣 Truyền thông – sự kiện"), ("khoahoc", "🤖 Khoa học – kỹ thuật"), ("ngoaingu", "🌏 Ngoại ngữ")]),
  W("list", "nhatky", "📔 Nhật ký hoạt động", add="Thêm buổi hoạt động", cols=[("ngay", "Ngày", "date"), ("hd", "Hoạt động", "text"), ("hoc", "Mình thích / học được gì", "note")])],
 "10-1-2": [W("chips", "manh", "💪 Điểm mạnh của mình", hint="Chọn những điều thầy cô, bạn bè từng khen bạn.", options=[
   ("tinh", "Tính toán"), ("viet", "Viết, diễn đạt"), ("noi", "Thuyết trình"), ("ve", "Vẽ, thiết kế"), ("tay", "Làm bằng tay, sửa đồ"), ("maytinh", "Máy tính, công nghệ"), ("ngoaingu", "Ngoại ngữ"), ("lang", "Lắng nghe, giúp đỡ"), ("tochuc", "Tổ chức, sắp xếp"), ("lanh", "Dẫn dắt nhóm"), ("tim", "Tìm tòi, đặt câu hỏi"), ("thethao", "Thể thao, vận động")]),
  W("chips", "giatri", "🧭 3 giá trị quan trọng nhất với mình", max=3, options=[
   ("thunhap", "💰 Thu nhập"), ("ondinh", "🏠 Ổn định"), ("sangtao", "🎨 Sáng tạo"), ("giupnguoi", "❤️ Giúp người"), ("tudo", "🕊️ Tự do"), ("thanhtich", "🏅 Thành tích"), ("hoc", "📚 Học hỏi"), ("giadinh", "👨‍👩‍👧 Gần gia đình")]),
  W("fields", "them", "✍️ Viết thêm", fields=["3 việc mình làm mà quên cả thời gian"])],
 "10-2-0": [W("fields", "cauhoi", "❔ 3 câu hỏi mình chuẩn bị trước khi đi", fields=["Câu hỏi 1", "Câu hỏi 2", "Câu hỏi 3"], short=True),
  W("list", "trainghiem", "🧳 Nhật ký trải nghiệm", add="Thêm nơi/sự kiện", cols=[("ngay", "Ngày", "date"), ("noi", "Nơi / sự kiện", "text"), ("rut", "Điều mình rút ra", "note")])],
 "10-2-1": [W("list", "nhom", "🎯 4–5 nhóm ngành mình quan tâm", add="Thêm nhóm ngành", max=5, cols=[("nganh", "Nhóm ngành", "major"), ("lydo", "Lý do", "text")],
   hint="Mỗi dòng một nhóm ngành kèm 1 lý do ngắn.")],
 "11-0-0": [W("list", "cham", "⚖️ Bảng chấm điểm ngành", add="Thêm ngành", max=6, score=True, cols=[("nganh", "Ngành", "major"), ("thich", "Mình thích (1–5)", "s15"), ("lam", "Mình làm được (1–5)", "s15"), ("tv", "Triển vọng (1–5)", "s15")],
   hint="Chấm 1 (thấp) → 5 (cao). Tổng điểm tự cộng; giữ lại 2–3 ngành cao nhất. Xem triển vọng có nguồn ở trang từng ngành."),
  W("fields", "giu", "✅ Kết luận", fields=["2–3 ngành mình giữ lại"], short=True)],
 "11-0-1": [W("list", "truong", "🏫 Danh sách trường mình tìm hiểu", add="Thêm trường", cols=[("truong", "Trường", "text"), ("nganh", "Ngành / chương trình", "text"), ("link", "Link trang tuyển sinh (.edu.vn)", "url"), ("hocphi", "Học phí (ghi năm & nguồn)", "text"), ("ghi", "Ghi chú", "note")],
   hint="Chỉ ghi học phí, thời gian đào tạo theo trang chính thức của trường – không lấy từ trang quảng cáo.")],
 "11-0-2": [W("pick", "tohop", "🧩 Tổ hợp xét tuyển mình nhắm", style="combo", note="Vì sao chọn tổ hợp này",
   hint="Một vài tổ hợp phổ biến. Ngành nào xét tổ hợp nào là tùy trường – xem đề án tuyển sinh của trường.",
   options=[("A00", "A00", "Toán – Vật lí – Hóa học"), ("A01", "A01", "Toán – Vật lí – Tiếng Anh"), ("B00", "B00", "Toán – Hóa học – Sinh học"), ("C00", "C00", "Ngữ văn – Lịch sử – Địa lí"), ("D01", "D01", "Ngữ văn – Toán – Tiếng Anh"), ("khac", "Khác", "Tổ hợp khác (ghi ở ô bên dưới)")]),
  W("fields", "bu", "🛠️ Môn cần bù", fields=["Môn mình cần cải thiện và cách làm"])],
 "11-1-0": [W("rate", "pt", "🗂️ Phương thức xét tuyển hợp với mình đến đâu?", hint="Bấm vào từng phương thức để xem giải thích, rồi chấm mức phù hợp 1–5. Mỗi trường áp dụng khác nhau và có thể thay đổi hằng năm.", lo="Không hợp", hi="Rất hợp", items=[
   C("thpt", "📝 Điểm thi tốt nghiệp THPT", "Dùng điểm các môn trong tổ hợp của kỳ thi tốt nghiệp THPT."),
   C("hocba", "📒 Xét học bạ", "Dùng điểm học bạ THPT theo cách tính trường công bố."),
   C("dgnl", "🧠 Thi đánh giá năng lực / tư duy", "Kỳ thi riêng do một số đại học tổ chức; kết quả được nhiều trường sử dụng."),
   C("cc", "🌐 Chứng chỉ ngoại ngữ / quốc tế (SAT…)", "Một số trường xét hoặc quy đổi điểm từ chứng chỉ – xem điều kiện trong đề án."),
   C("thang", "🏅 Xét tuyển thẳng / ưu tiên", "Theo quy chế tuyển sinh của Bộ và đề án của trường (ví dụ thành tích thi học sinh giỏi).")]),
  W("fields", "chot", "✍️ Ghi chú", fields=["Phương thức phù hợp với mình và điều kiện cần (theo đề án chính thức)"])],
 "11-1-1": [W("list", "muctieu", "🎯 Mục tiêu từng môn trong tổ hợp", add="Thêm môn", max=6, cols=[("mon", "Môn", "text"), ("nay", "Điểm hiện tại", "num"), ("dich", "Mục tiêu", "num"), ("tuan", "Việc làm mỗi tuần", "text")],
   hint="Điểm thang 10. Ví dụ việc mỗi tuần: “1 đề tổng hợp + chữa lỗi sai”.")],
 "11-1-2": [W("list", "thithu", "📊 Kết quả thi thử", add="Thêm lần thi", cols=[("ngay", "Ngày", "date"), ("ky", "Kỳ thi / đề", "text"), ("diem", "Điểm", "text"), ("rut", "Rút kinh nghiệm", "note")]),
  W("fields", "cc", "🌐 Kế hoạch chứng chỉ (nếu có)", fields=["Chứng chỉ, trường nào dùng, điều kiện quy đổi (theo đề án chính thức)"])],
 "11-2-0": [W("cards", "tn", "🧪 Chọn cách trải nghiệm nghề", date="Dự kiến bắt đầu", hint="Bấm vào thẻ để xem gợi ý. Tích cách bạn sẽ thử trong hè.", cards=[
   C("khoahe", "☀️ Khóa học hè", "Tìm khóa hè ngắn do trường đại học, trung tâm uy tín tổ chức.", "Hỏi kỹ đơn vị tổ chức, tránh nơi thu phí bất thường."),
   C("duan", "🛠️ Dự án cá nhân", "Tự làm một sản phẩm nhỏ liên quan ngành: website, video, mô hình, bài nghiên cứu.", "Lưu lại sản phẩm để làm hồ sơ."),
   C("clb", "👥 CLB / đội nhóm", "Tham gia CLB chuyên ngành, đội thi hoặc nhóm dự án ở trường.", ""),
   C("lamthem", "💼 Làm thêm phù hợp tuổi", "Việc nhẹ, hợp pháp, an toàn và có sự đồng ý của gia đình.", ""),
   C("tinhnguyen", "🤝 Tình nguyện", "Hoạt động xã hội gần với ngành (ví dụ y tế cộng đồng, dạy học).", ""),
   C("theo", "👀 Đi theo người làm nghề", "Xin theo người thân/người quen 1 ngày làm việc để quan sát.", "")]),
  W("rate", "con", "❤️ Sau trải nghiệm", lo="Hết thích", hi="Thích hơn", items=[C("thich", "Mình còn thích ngành này không?", "")]),
  W("fields", "ghi", "✍️ Ghi chép", fields=["Mình đã làm gì và học được gì"])],
 "11-2-1": [W("fields", "pv", "🎙️ Phiếu phỏng vấn người làm nghề", fields=["Người mình hỏi (nghề, nơi làm – không cần ghi tên thật)", "Một ngày làm việc của họ ra sao?", "Điều khó nhất trong nghề là gì?", "Cần kỹ năng gì?", "Thu nhập thực tế khi mới đi làm (theo lời họ)", "Câu trả lời đáng nhớ nhất"])],
 "12-0-0": [W("majors", "chinh", "🎯 Ngành chính (chọn 1–2)", max=2, hint="Tích tối đa 2 ngành chính."),
  W("list", "ds", "🏫 Danh sách trường (4–6 trường)", add="Thêm trường", max=8, cols=[("truong", "Trường", "text"), ("link", "Link tuyển sinh", "url"), ("hop", "Vì sao phù hợp (năng lực, học phí, khoảng cách)", "text")]),
  W("pick", "gd", "👨‍👩‍👧 Thống nhất", style="check", options=[("gd", "Đã trao đổi và thống nhất với gia đình", "")])],
 "12-0-1": [W("list", "moc", "📅 Lịch các mốc của mình", add="Thêm mốc", cols=[("moc", "Mốc", "text"), ("ngay", "Ngày (theo thông báo chính thức)", "date"), ("nguon", "Link thông báo", "url")],
   hint="Chúng tôi không tự đưa ra ngày. Bạn tự điền ngay khi Bộ GD&ĐT hoặc đơn vị tổ chức công bố, kèm link nguồn.")],
 "12-0-2": [W("list", "kh", "🗓️ Kế hoạch ôn thi theo tháng", add="Thêm tháng", cols=[("thang", "Tháng", "month"), ("mon", "Môn", "text"), ("mt", "Mục tiêu cụ thể", "text"), ("xong", "Đạt chưa?", "sel:chua=Chưa,dang=Đang làm,roi=Đạt rồi")])],
 "12-1-0": [W("list", "nv", "🏆 Danh sách nguyện vọng (kéo thứ tự bằng nút ↑ ↓)", add="Thêm nguyện vọng", ordered=True, max=15, cols=[("truong", "Trường", "text"), ("nganh", "Ngành", "text"), ("muc", "Mức", "sel:" + ",".join(f"{a}={b}" for a, b in LV)), ("dc", "Điểm chuẩn tham khảo (ghi năm)", "text")],
   hint="Nguyện vọng 1 là ưu tiên cao nhất. Xếp: mơ ước → phù hợp → an toàn.")],
 "12-1-1": [W("pick", "hs", "📁 Hồ sơ cần chuẩn bị", style="check", note="Còn thiếu gì / cần hỏi ai", hint="Tích từng mục khi đã có. Danh mục cụ thể theo quy chế năm bạn thi và hướng dẫn của trường.", options=[
   ("hocba", "Học bạ THPT (bản chính và bản sao)", "Cơ bản"), ("cccd", "Căn cước", "Cơ bản"), ("anh", "Ảnh thẻ", "Cơ bản"), ("email", "Email và số điện thoại liên lạc đang dùng", "Cơ bản"),
   ("uutien", "Giấy tờ chứng nhận ưu tiên khu vực/đối tượng (nếu có)", "Nếu có"), ("cc", "Chứng chỉ ngoại ngữ / quốc tế (nếu dùng)", "Nếu có"), ("giai", "Giấy chứng nhận giải thưởng (nếu có)", "Nếu có"),
   ("rieng", "Hồ sơ cho phương thức riêng của trường (theo hướng dẫn của trường)", "Theo trường")])],
 "12-1-2": [W("list", "hb", "🎓 Học bổng mình theo dõi", add="Thêm học bổng", cols=[("ten", "Tên học bổng / đơn vị", "text"), ("dk", "Điều kiện", "text"), ("han", "Hạn nộp (theo thông báo)", "date"), ("link", "Link", "url"), ("tt", "Trạng thái", "sel:xem=Đang xem,lam=Đang làm hồ sơ,nop=Đã nộp")],
   hint="⚠️ Không trả phí để “xin” học bổng. Hạn nộp: tự điền theo thông báo chính thức.")],
 "12-2-0": [W("pick", "on", "🏁 Thói quen ôn thi tuần này", style="check", options=[("de", "Luyện đề theo cấu trúc đề minh họa Bộ công bố", ""), ("chua", "Chữa kỹ lỗi sai sau mỗi đề", ""), ("ngu", "Ngủ đủ 7–8 tiếng", ""), ("an", "Ăn uống điều độ, vận động nhẹ", ""), ("khongdon", "Tuần cuối không học dồn", "")]),
  W("list", "loi", "🐞 Sổ lỗi sai hay gặp", add="Thêm lỗi sai", cols=[("mon", "Môn", "text"), ("loi", "Lỗi sai", "text"), ("sua", "Cách sửa", "text")])],
 "12-2-1": [W("pick", "kt", "🔎 Kiểm tra trước khi bấm xác nhận", style="check", hint="Tích từng mục trên cổng thí sinh. Ngày cụ thể: xem thông báo chính thức của Bộ GD&ĐT.", options=[
   ("tk", "Đăng nhập đúng tài khoản thí sinh của mình", ""), ("ma", "Mã trường đúng", ""), ("nganh", "Mã ngành / mã xét tuyển đúng", ""), ("tohop", "Tổ hợp / phương thức đúng", ""), ("thutu", "Thứ tự nguyện vọng đúng ý mình", ""), ("han", "Làm trong thời hạn theo thông báo chính thức", ""), ("luu", "Chụp màn hình / lưu lại kết quả đăng ký", "")])],
 "12-2-2": [W("chips", "loai", "🛤️ Con đường dự phòng mình cân nhắc", options=[("gan", "Ngành gần"), ("khac", "Trường khác"), ("cd", "Cao đẳng"), ("nghe", "Học nghề"), ("vhvl", "Vừa học vừa làm"), ("duhoc", "Du học"), ("gap", "Gap year")]),
  W("fields", "pa", "📋 Phương án của mình", fields=["Phương án A (chính)", "Phương án B (dự phòng 1)", "Phương án C (dự phòng 2)", "Điều kiện cần tìm hiểu thêm"], short=True)],
}
# Mẫu UI chính của mỗi trang (dùng cho báo cáo + class CSS)
def kind(key): return "+".join(dict.fromkeys(w["type"] for w in UI[key] if w["type"] != "info"))

def _cols(w):
    out = []
    for c, label, t in w["cols"]:
        if t.startswith("sel:"): out.append((c, label, "sel", [tuple(x.split("=", 1)) for x in t[4:].split(",")]))
        elif t == "s15": out.append((c, label, "sel", S15))
        else: out.append((c, label, t, None))
    return out
def _clean(v, t, opts=None, majors=()):
    v = (v or "").strip()
    if t == "note": return v[:NOTE]
    if t == "date": return v if DATE.match(v) else ""
    if t == "month": return v if MONTH.match(v) else ""
    if t == "url": return v[:300] if re.match(r"^https?://[^\s<>\"']+$", v) else ""
    if t == "num":
        try: f = float(v.replace(",", ".")); return v[:5] if 0 <= f <= 10 else ""
        except ValueError: return ""
    if t == "sel": return v if v in {a for a, _ in opts} else ""
    if t == "major": return v if v in majors else ""
    return v[:TXT]
def parse(key, form, majors=()):
    """form: đối tượng có .get/.getlist (request.form hoặc MultiDict). Trả dict sạch."""
    d = {}
    for w in UI.get(key, []):
        t, i = w["type"], w["id"]
        if t in ("pick", "chips"):
            ok = [o[0] for o in w["options"]]; v = [x for x in form.getlist(i) if x in ok]
            d[i] = list(dict.fromkeys(v))[:w.get("max", 50)]
            if w.get("note"): d[i + ".note"] = _clean(form.get(i + ".note"), "note")
        elif t == "majors":
            d[i] = [x for x in dict.fromkeys(form.getlist(i)) if x in majors][:w.get("max", 8)]
        elif t == "cards":
            ok = [c["id"] for c in w["cards"]]; d[i] = [x for x in dict.fromkeys(form.getlist(i)) if x in ok]
            for c in w["cards"]:
                d[f"{i}.{c['id']}.date"] = _clean(form.get(f"{i}.{c['id']}.date"), "date")
                d[f"{i}.{c['id']}.note"] = _clean(form.get(f"{i}.{c['id']}.note"), "note")
        elif t == "rate":
            for c in w["items"]: d[f"{i}.{c['id']}"] = _clean(form.get(f"{i}.{c['id']}"), "sel", S15)
        elif t == "fields":
            for n in range(len(w["fields"])): d[f"{i}.{n}"] = _clean(form.get(f"{i}.{n}"), "note")
        elif t == "list":
            cols = _cols(w); vals = {c: form.getlist(f"{i}.{c}") for c, *_ in cols}
            rows = []
            for r in range(min(max((len(v) for v in vals.values()), default=0), w.get("max", MAXROWS))):
                row = {c: _clean(vals[c][r] if r < len(vals[c]) else "", t2, o, majors) for c, _, t2, o in cols}
                if any(row.values()): rows.append(row)
            d[i] = rows
    d = {k: v for k, v in d.items() if v}
    while len(json.dumps(d, ensure_ascii=False)) > MAXJSON and d: d.pop(next(reversed(d)))
    return d
def widgets(key):
    out = []
    for w in UI.get(key, []):
        w = dict(w)
        if w["type"] == "list": w["cols"] = _cols(w)
        out.append(w)
    return out
