GRADES = {
 10: dict(icon="🌱", tag="Khám phá bản thân", color="pri",
  intro="Lớp 10 là năm để hiểu mình: thích gì, giỏi gì, coi trọng điều gì. Chưa cần chốt ngành, hãy thử nhiều thứ!",
  phases=[
   ("Đầu năm", [
    ("Chọn môn học lựa chọn hợp với mình", "Theo chương trình GDPT 2018, từ lớp 10 bạn chọn các môn học lựa chọn. Hãy cân nhắc môn mình thích và nhóm ngành có thể theo sau này.", None),
    ("Làm trắc nghiệm sở thích", "Mất khoảng 2 phút, gợi ý các nhóm ngành hợp với tính cách của bạn.", ("/quiz", "Làm trắc nghiệm")),
    ("Xây thói quen học tốt", "Lập thời gian biểu, học đều các môn, giữ học bạ ổn định ngay từ đầu.", None)]),
   ("Giữa năm", [
    ("Tìm hiểu các nhóm ngành", "Đọc về công việc, kỹ năng cần có và xu hướng của từng ngành.", ("/#nganh", "Xem các ngành")),
    ("Tham gia câu lạc bộ, ngoại khóa", "CLB, cuộc thi, tình nguyện giúp bạn phát hiện năng lực và sở thích thật.", None),
    ("Ghi lại điểm mạnh và giá trị của mình", "Viết ra: mình giỏi gì, thích làm gì, điều gì quan trọng với mình (thu nhập, giúp người, sáng tạo...).", None)]),
   ("Cuối năm / hè", [
    ("Trải nghiệm thực tế", "Tham quan nơi làm việc, ngày hội hướng nghiệp, hỏi người thân về nghề của họ.", None),
    ("Chọn ra 4–5 nhóm ngành quan tâm", "Danh sách sơ bộ để lớp 11 tìm hiểu sâu hơn.", None)])]),
 11: dict(icon="🔍", tag="Thu hẹp lựa chọn", color="sun",
  intro="Lớp 11 là lúc thu hẹp còn 2–3 ngành, tìm hiểu kỹ trường và cách xét tuyển để chuẩn bị đúng hướng.",
  phases=[
   ("Học kỳ 1", [
    ("Thu hẹp còn 2–3 ngành/nhóm ngành", "So sánh các ngành đã chọn ở lớp 10 dựa trên sở thích, năng lực và xu hướng nghề.", ("/so-sanh", "So sánh ngành")),
    ("Tìm hiểu trường và chương trình đào tạo", "Xem môn học, thời gian đào tạo, cơ hội việc làm, học phí trên trang tuyển sinh chính thức của trường.", None),
    ("Xác định tổ hợp xét tuyển", "Mỗi ngành xét theo các tổ hợp môn (ví dụ A00, B00, D01). Biết tổ hợp để tập trung học.", None)]),
   ("Học kỳ 2", [
    ("Tìm hiểu các phương thức xét tuyển", "Ví dụ: điểm thi tốt nghiệp THPT, xét học bạ, thi đánh giá năng lực/đánh giá tư duy, chứng chỉ ngoại ngữ, SAT... Mỗi trường áp dụng khác nhau và có thể thay đổi hằng năm.", None),
    ("Tập trung các môn trong tổ hợp", "Củng cố kiến thức nền, giữ điểm học bạ tốt.", None),
    ("Thi thử, chứng chỉ ngoại ngữ", "Làm quen dạng đề, cân nhắc chuẩn bị chứng chỉ ngoại ngữ nếu trường bạn nhắm có dùng.", None)]),
   ("Hè lên lớp 12", [
    ("Trải nghiệm nghề", "Tham gia khóa hè, dự án, thực tập ngắn hoặc làm thêm liên quan ngành.", None),
    ("Trò chuyện với người đang làm nghề", "Hỏi về công việc hằng ngày, khó khăn, thu nhập thực tế.", None)])]),
 12: dict(icon="🎯", tag="Quyết định & hành động", color="coral",
  intro="Lớp 12 là năm chốt ngành, chốt trường và hành động theo kế hoạch. Bình tĩnh, làm từng bước!",
  phases=[
   ("Đầu năm", [
    ("Chốt ngành và trường", "Chọn 1–2 ngành chính, danh sách trường phù hợp năng lực và điều kiện gia đình.", ("/#nganh", "Xem lại các ngành")),
    ("Nắm lịch thi và xét tuyển", "Theo dõi lịch thi tốt nghiệp THPT và đăng ký xét tuyển theo thông báo của Bộ GD&ĐT hằng năm, cùng lịch các kỳ thi riêng.", None),
    ("Lập kế hoạch ôn thi", "Chia nhỏ mục tiêu theo tháng cho từng môn trong tổ hợp.", None)]),
   ("Giữa năm", [
    ("Lập danh sách nguyện vọng", "Sắp xếp theo thứ tự: nguyện vọng mơ ước → phù hợp → an toàn.", None),
    ("Chuẩn bị hồ sơ", "Học bạ, chứng chỉ, giấy tờ ưu tiên (nếu có), hồ sơ cho các phương thức xét tuyển riêng.", None),
    ("Tìm hiểu học bổng", "Xem học bổng của trường, doanh nghiệp, quỹ; chú ý điều kiện và hạn nộp.", None)]),
   ("Cuối năm", [
    ("Ôn thi tốt nghiệp THPT", "Luyện đề, giữ sức khỏe, ngủ đủ giấc.", None),
    ("Đăng ký và điều chỉnh nguyện vọng đúng hạn", "Làm theo hướng dẫn chính thức trên hệ thống của Bộ GD&ĐT.", None),
    ("Có kế hoạch dự phòng", "Ngành/trường thay thế, học nghề, cao đẳng, du học... đều là con đường tốt.", ("/con-duong-khac", "Xem con đường khác"))])]),
}

def steps(g):
    """Danh sách khóa ổn định cho từng bước: '<lớp>-<giai đoạn>-<bước>'."""
    return [f"{g}-{i}-{j}" for i, (_, items) in enumerate(GRADES[g]["phases"]) for j in range(len(items))]
