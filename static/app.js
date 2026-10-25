/* Hướng Nghiệp 360 – JS dùng chung (không inline, tương thích CSP script-src 'self'). */
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const meta = n => (document.querySelector(`meta[name="${n}"]`) || {}).content || "";
  const LOGGED = meta("logged-in") === "1";
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} }
  };
  document.addEventListener("DOMContentLoaded", () => {
    // Menu 3 gạch
    const bg = $("[data-burger]");
    if (bg) {
      const nav = bg.closest(".nav");
      const set = o => { nav.classList.toggle("open", o); bg.setAttribute("aria-expanded", o); bg.setAttribute("aria-label", o ? "Đóng menu" : "Mở menu"); };
      bg.addEventListener("click", () => set(!nav.classList.contains("open")));
      document.addEventListener("keydown", e => { if (e.key === "Escape" && nav.classList.contains("open")) { set(false); bg.focus(); } });
    }
    // Hiện/ẩn mật khẩu
    $$("[data-eye]").forEach(b => b.addEventListener("click", () => {
      const p = document.getElementById(b.dataset.eye), show = p.type === "password";
      p.type = show ? "text" : "password"; b.textContent = show ? "Ẩn" : "Hiện";
      b.setAttribute("aria-pressed", show); b.setAttribute("aria-label", show ? "Ẩn mật khẩu" : "Hiện mật khẩu");
    }));
    // Tiến độ trắc nghiệm
    const qf = $("#qf");
    if (qf) {
      const n = +qf.dataset.total, upd = () => {
        const a = new Set($$("input:checked", qf).map(e => e.name)).size, p = Math.round(a / n * 100);
        $("#pb").style.width = p + "%"; $("#pp").textContent = p + "%"; $("#pt").textContent = `Đã trả lời ${a}/${n}`;
        $(".progress [role=progressbar]").setAttribute("aria-valuenow", a);
      };
      qf.addEventListener("change", upd); upd();
    }
    // Checklist trang lớp: ô chưa tích → mở trang con của bước; ô đã tích → bấm để bỏ tích.
    // Lưu trên máy chủ (tài khoản hoặc phiên khách); tiến độ localStorage cũ được gộp lên một lần.
    const cl = $("[data-checklist]");
    if (cl) {
      const g = +cl.dataset.checklist, key = "hn360:lop" + g, boxes = $$("[data-step]"), total = boxes.length;
      const render = () => {
        const d = boxes.filter(b => b.checked).length;
        $("#gcount").textContent = `${d}/${total}`; $("#gbar").style.width = Math.round(d / total * 100) + "%";
        $("[role=progressbar]", cl).setAttribute("aria-valuenow", d);
        boxes.forEach(b => b.closest("li").classList.toggle("done", b.checked));
      };
      const cur = () => boxes.filter(b => b.checked).map(b => b.dataset.step);
      const sync = (merge) => fetch("/api/tien-do", { method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": meta("csrf-token") },
        body: JSON.stringify({ grade: g, done: cur(), merge: !!merge }) })
        .then(r => r.ok ? r.json() : Promise.reject(r.status))
        .then(j => { $("#gsave").textContent = LOGGED ? "✓ Đã lưu vào tài khoản" : "✓ Đã lưu tạm trên trình duyệt này"; boxes.forEach(b => b.checked = j.done.includes(b.dataset.step)); render(); })
        .catch(() => { $("#gsave").textContent = "Chưa lưu được – kiểm tra kết nối"; });
      const local = store.get(key, []);
      if (local.length) { boxes.forEach(b => { if (local.includes(b.dataset.step)) b.checked = true; }); store.set(key, []); sync(true); }
      boxes.forEach(b => b.addEventListener("click", e => {
        if (b.checked) { e.preventDefault(); location.href = b.dataset.href; return; }  // chưa tích → sang trang thực hiện
        render(); sync(false);
      }));
    }
    // So sánh ngành: thanh dính dưới trang chủ
    const bar = $("#cbar");
    if (bar) {
      const KEY = "hn360:compare", boxes = $$("[data-compare]");
      let sel = store.get(KEY, []).filter(x => x && x.id).slice(0, 3);
      const render = () => {
        boxes.forEach(b => { b.checked = sel.some(s => s.id === b.dataset.compare); b.disabled = !b.checked && sel.length >= 3; b.closest(".cmp").classList.toggle("off", b.disabled); });
        bar.hidden = sel.length === 0; document.body.classList.toggle("has-cbar", sel.length > 0);
        $("#cnames").textContent = sel.length ? `Đã chọn ${sel.length}/3: ${sel.map(s => s.name).join(", ")}` : "";
        const go = $("#cgo"); go.href = "/so-sanh?" + sel.map(s => "nganh=" + encodeURIComponent(s.id)).join("&");
        go.classList.toggle("dis", sel.length < 2); go.setAttribute("aria-disabled", sel.length < 2);
        go.textContent = sel.length < 2 ? "Chọn thêm 1 ngành" : "So sánh →";
      };
      boxes.forEach(b => b.addEventListener("change", () => {
        sel = sel.filter(s => s.id !== b.dataset.compare);
        if (b.checked && sel.length < 3) sel.push({ id: b.dataset.compare, name: b.dataset.name });
        store.set(KEY, sel); render();
      }));
      $("#cgo").addEventListener("click", e => { if (sel.length < 2) e.preventDefault(); });
      $("#cclear").addEventListener("click", () => { sel = []; store.set(KEY, sel); render(); });
      render();
    }
    // Ghi chép trên trang con của bước (chỉ lưu localStorage)
    $$("[data-notes]").forEach(box => {
      const k = box.dataset.notes, areas = $$("textarea", box), st = $("[data-notes-status]", box), v = store.get(k, []);
      areas.forEach((t, i) => { t.value = v[i] || ""; t.addEventListener("input", () => { store.set(k, areas.map(a => a.value)); st.textContent = "✓ Đã lưu trên thiết bị này"; }); });
    });
    // Biểu đồ (Chart.js tự lưu trữ)
    if (window.Chart) {
      Chart.defaults.font.family = '"Be Vietnam Pro",system-ui,sans-serif'; Chart.defaults.color = "#5b6478";
      const inc = $("#incdata");
      if (inc) {
        const d = JSON.parse(inc.textContent), fmt = v => v.toLocaleString("vi-VN", { maximumFractionDigits: 1 }) + " triệu";
        new Chart($("#inc"), { type: "bar", data: { labels: d.years, datasets: [
          { label: d.label, data: d.values, backgroundColor: "#0f8a7e", borderRadius: 8, maxBarThickness: 48 },
          { label: "Bình quân cả nước", data: d.all, backgroundColor: "#ffc93c", borderRadius: 8, maxBarThickness: 48 }] },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" }, tooltip: { callbacks: { label: c => `${c.dataset.label}: ${fmt(c.raw)}` } } },
            scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: "#eef1f6" }, border: { display: false }, title: { display: true, text: "triệu đồng/tháng" } } } } });
      }
      const rd = $("#rdata");
      if (rd) {
        const d = JSON.parse(rd.textContent);
        new Chart($("#radar"), { type: "radar", data: { labels: d.labels, datasets: [{ label: "Điểm của bạn", data: d.values, borderColor: "#0f8a7e", backgroundColor: "rgba(15,138,126,.2)", pointBackgroundColor: "#0f8a7e", borderWidth: 2.5 }] },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { r: { min: 0, max: 100, ticks: { stepSize: 25, backdropColor: "transparent" }, pointLabels: { font: { size: 13, weight: "600" } } } } } });
      }
    }
  });
})();
