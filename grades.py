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

MOET = ("Bộ GD&ĐT – moet.gov.vn", "https://moet.gov.vn")
PORTAL = ("Cổng thí sinh của Bộ GD&ĐT – thisinh.thitotnghiepthpt.edu.vn", "https://thisinh.thitotnghiepthpt.edu.vn")
GDNN = ("Cục Giáo dục nghề nghiệp – gdnn.gov.vn", "https://gdnn.gov.vn")
NSO = ("Cục Thống kê – nso.gov.vn (số liệu lao động, việc làm)", "https://www.nso.gov.vn")
# Mỗi bước: how = các việc cần làm; form = ô ghi chép (lưu trên thiết bị); links = nguồn chính thức; tool = công cụ trong web
GUIDE = {
 "10-0-0": dict(how=["Xem danh sách môn học lựa chọn và các tổ hợp môn trường bạn thực sự mở (hỏi GVCN/phòng giáo vụ).", "Ghi ra 2–3 nhóm ngành bạn đang tò mò và xem chúng thường xét tổ hợp nào.", "Chọn môn vừa thích, vừa học được, vừa giữ được nhiều hướng ngành.", "Trao đổi với gia đình trước khi nộp phiếu chọn môn."],
   form=["Các tổ hợp môn trường mình mở", "Tổ hợp mình định chọn và lý do"], links=[MOET], tool=("/#nganh", "Xem các ngành và tổ hợp")),
 "10-0-1": dict(how=["Dành khoảng 4 phút ở nơi yên tĩnh.", "Trả lời thật lòng theo mức bạn THÍCH hoạt động, không phải mức giỏi.", "Xem mã Holland 3 chữ và các ngành gợi ý.", "Bấm “Tiếp tục bước tiếp theo” ở trang kết quả – ô này sẽ tự được tích."],
   form=[], links=[], tool=("/quiz", "Làm trắc nghiệm")),
 "10-0-2": dict(how=["Lập thời gian biểu tuần: giờ học trên lớp, tự học, nghỉ ngơi, ngủ.", "Ưu tiên học đều mỗi ngày thay vì dồn trước kiểm tra.", "Cuối tuần tự đánh giá 5 phút: tuần này làm được gì, cần chỉnh gì."],
   form=["Thời gian biểu tự học trong tuần", "Môn cần cải thiện nhất"], links=[]),
 "10-1-0": dict(how=["Mở 3–5 ngành bất kỳ trên trang Ngành nghề, đọc phần công việc và kỹ năng.", "Xem thu nhập ngành kinh tế liên quan (có nguồn, năm 2024).", "Đánh dấu ngành muốn so sánh rồi dùng trang So sánh."],
   form=["Ngành mình thấy thú vị", "Điều bất ngờ mình mới biết"], links=[NSO], tool=("/#nganh", "Xem các ngành")),
 "10-1-1": dict(how=["Hỏi thầy cô/đoàn trường danh sách CLB, cuộc thi, hoạt động tình nguyện.", "Chọn 1–2 hoạt động khác nhau (ví dụ 1 học thuật + 1 nghệ thuật/xã hội).", "Sau 1–2 tháng ghi lại: mình thích phần nào, giỏi phần nào."],
   form=["Hoạt động mình tham gia", "Mình học được gì từ đó"], links=[]),
 "10-1-2": dict(how=["Liệt kê 3 việc bạn làm tốt (thầy cô, bạn bè từng khen).", "Liệt kê 3 việc bạn làm mà quên thời gian.", "Chọn 3 giá trị quan trọng nhất: thu nhập, ổn định, sáng tạo, giúp người, tự do…"],
   form=["3 điểm mạnh", "3 việc mình thích làm", "3 giá trị quan trọng nhất"], links=[], tool=("/ho-so#the-manh", "Lưu vào hồ sơ")),
 "10-2-0": dict(how=["Theo dõi ngày hội tư vấn tuyển sinh/hướng nghiệp do trường hoặc địa phương tổ chức.", "Xin phép đi tham quan nơi làm việc của người thân 1 buổi.", "Chuẩn bị 3 câu hỏi trước khi đi và ghi lại câu trả lời."],
   form=["Nơi/sự kiện mình đã đi", "Điều mình rút ra"], links=[MOET]),
 "10-2-1": dict(how=["Xem lại kết quả trắc nghiệm, điểm mạnh và các ngành đã đọc.", "Chọn 4–5 nhóm ngành, mỗi ngành viết 1 dòng lý do.", "Lưu vào hồ sơ để lớp 11 thu hẹp tiếp."],
   form=["4–5 nhóm ngành quan tâm và lý do"], links=[], tool=("/ho-so#du-dinh", "Lưu ngành mục tiêu")),
 "11-0-0": dict(how=["Mở trang So sánh, chọn 3 ngành trong danh sách lớp 10.", "Chấm mỗi ngành theo: mình thích (1–5), mình làm được (1–5), triển vọng (có nguồn).", "Giữ lại 2–3 ngành có tổng điểm cao nhất."],
   form=["2–3 ngành giữ lại"], links=[], tool=("/so-sanh", "So sánh ngành")),
 "11-0-1": dict(how=["Vào trang tuyển sinh chính thức của trường (đuôi .edu.vn) – không dựa vào trang quảng cáo.", "Ghi: chương trình học, thời gian đào tạo, học phí năm gần nhất do trường công bố.", "Tìm số liệu việc làm sau tốt nghiệp nếu trường có công bố (ghi rõ năm)."],
   form=["Trường – ngành – học phí (ghi năm, nguồn)"], links=[MOET]),
 "11-0-2": dict(how=["Xem đề án tuyển sinh năm gần nhất của các trường bạn nhắm.", "Ghi tổ hợp/phương thức mỗi ngành dùng.", "Chọn tổ hợp chung nhiều nhất để tập trung học."],
   form=["Tổ hợp mục tiêu", "Môn cần bù"], links=[MOET], tool=("/ho-so#the-manh", "Lưu tổ hợp vào hồ sơ")),
 "11-1-0": dict(how=["Đọc quy chế tuyển sinh hiện hành trên moet.gov.vn.", "Với từng trường, ghi phương thức xét tuyển và điều kiện.", "Lưu ý: quy chế có thể thay đổi hằng năm – chưa có số liệu, xem thông báo chính thức của năm bạn thi."],
   form=["Phương thức phù hợp với mình"], links=[MOET]),
 "11-1-1": dict(how=["Xác định 3 môn trong tổ hợp mục tiêu.", "Mỗi tuần làm ít nhất 1 đề/bài tổng hợp mỗi môn.", "Theo dõi điểm học bạ từng kỳ."],
   form=["Mục tiêu điểm từng môn"], links=[]),
 "11-1-2": dict(how=["Tham gia thi thử do trường/sở tổ chức để làm quen dạng đề.", "Nếu trường nhắm dùng chứng chỉ ngoại ngữ, xem điều kiện quy đổi trong đề án của trường.", "Chỉ đăng ký thi chứng chỉ ở đơn vị được cấp phép; lệ phí và lịch thi: xem thông báo chính thức."],
   form=["Kết quả thi thử", "Kế hoạch chứng chỉ (nếu có)"], links=[MOET]),
 "11-2-0": dict(how=["Tìm khóa hè, dự án, CLB hoặc việc làm thêm phù hợp tuổi liên quan ngành.", "Tham gia ít nhất 1 hoạt động 2–4 tuần.", "Ghi lại sản phẩm/kinh nghiệm để làm hồ sơ sau này."],
   form=["Hoạt động trải nghiệm", "Mình có còn thích ngành này?"], links=[GDNN]),
 "11-2-1": dict(how=["Tìm 1–2 người đang làm nghề bạn quan tâm (người thân, cựu học sinh).", "Hỏi: một ngày làm việc ra sao, khó nhất là gì, cần kỹ năng gì, thu nhập thực tế khi mới đi làm.", "Cảm ơn và ghi chép lại."],
   form=["Người mình đã hỏi", "Câu trả lời đáng nhớ"], links=[]),
 "12-0-0": dict(how=["Chọn 1–2 ngành chính từ danh sách lớp 11.", "Lập danh sách 4–6 trường: phù hợp năng lực, học phí, khoảng cách.", "Thống nhất với gia đình."],
   form=["Ngành chính", "Danh sách trường"], links=[MOET], tool=("/#nganh", "Xem lại các ngành")),
 "12-0-1": dict(how=["Theo dõi kế hoạch thi tốt nghiệp THPT và tuyển sinh năm của bạn trên moet.gov.vn.", "Ghi các mốc quan trọng vào lịch ngay khi Bộ công bố – mốc thời gian: chưa có số liệu, xem thông báo chính thức.", "Theo dõi lịch các kỳ thi riêng (đánh giá năng lực/tư duy) trên trang của đơn vị tổ chức."],
   form=["Các mốc mình cần nhớ (ghi theo thông báo chính thức)"], links=[MOET, PORTAL]),
 "12-0-2": dict(how=["Chia thời gian đến kỳ thi thành từng tháng.", "Mỗi tháng đặt mục tiêu cụ thể cho từng môn.", "Mỗi tuần làm 1 đề thi thử và chữa lỗi sai."],
   form=["Mục tiêu tháng này"], links=[]),
 "12-1-0": dict(how=["Xếp nguyện vọng theo thứ tự ưu tiên thật sự: mơ ước → phù hợp → an toàn.", "Tham khảo điểm chuẩn các năm gần nhất do trường công bố (ghi rõ năm).", "Nguyện vọng 1 là nguyện vọng cao nhất – chỉ đỗ 1 nguyện vọng cao nhất có thể."],
   form=["Danh sách nguyện vọng dự kiến"], links=[MOET, PORTAL]),
 "12-1-1": dict(how=["Chuẩn bị học bạ, căn cước, ảnh, chứng chỉ (nếu có).", "Kiểm tra giấy tờ ưu tiên khu vực/đối tượng (nếu có) theo quy chế.", "Với phương thức riêng của trường, làm theo hướng dẫn trên trang tuyển sinh của trường."],
   form=["Giấy tờ đã có / còn thiếu"], links=[MOET]),
 "12-1-2": dict(how=["Xem trang học bổng của trường bạn nhắm.", "Tìm học bổng doanh nghiệp/quỹ uy tín – không trả phí để “xin” học bổng.", "Ghi điều kiện và hạn nộp theo thông báo chính thức."],
   form=["Học bổng – điều kiện – hạn nộp (theo thông báo)"], links=[]),
 "12-2-0": dict(how=["Luyện đề theo cấu trúc đề minh họa Bộ công bố.", "Ngủ đủ 7–8 tiếng, ăn uống điều độ.", "Tuần cuối: ôn lại lỗi sai, không học dồn."],
   form=["Lỗi sai hay gặp"], links=[MOET]),
 "12-2-1": dict(how=["Đăng ký/điều chỉnh nguyện vọng trên cổng thí sinh của Bộ.", "Kiểm tra kỹ mã trường, mã ngành, thứ tự nguyện vọng trước khi xác nhận.", "Làm đúng hạn theo thông báo chính thức – ngày cụ thể: chưa có số liệu, xem thông báo chính thức."],
   form=[], links=[PORTAL, MOET]),
 "12-2-2": dict(how=["Chọn 1–2 phương án dự phòng: ngành gần, trường khác, cao đẳng, học nghề.", "Tìm hiểu trước điều kiện của phương án dự phòng.", "Nhớ: con đường nào cũng có thể dẫn tới nghề tốt."],
   form=["Phương án dự phòng của mình"], links=[GDNN], tool=("/con-duong-khac", "Xem con đường khác")),
}
QUIZ_STEP = "10-0-1"
def step_info(key):
    try: g, i, j = (int(x) for x in key.split("-"))
    except ValueError: return None
    if g not in GRADES or i >= len(GRADES[g]["phases"]) or j >= len(GRADES[g]["phases"][i][1]): return None
    ph, items = GRADES[g]["phases"][i]; t, dsc, link = items[j]
    return dict(key=key, g=g, phase=ph, title=t, desc=dsc, link=link, **GUIDE[key])
def href(key): return "/quiz?buoc=" + key if key == QUIZ_STEP else f"/lop-{key.split('-')[0]}/buoc/{key}"
def next_step(g, done, after=None):
    ks = steps(g)
    order = ks[ks.index(after) + 1:] + ks[:ks.index(after)] if after in ks else ks
    return next((k for k in order if k not in done), None)
