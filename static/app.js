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
      $$(".menu a", nav).forEach(a => a.addEventListener("click", () => set(false)));
      document.addEventListener("keydown", e => { if (e.key === "Escape" && nav.classList.contains("open")) { set(false); bg.focus(); } });
    }
    // "Xem thêm ngành" trên trang chủ
    $$("[data-more]").forEach(b => b.addEventListener("click", () => { const g = document.getElementById(b.dataset.more); g.classList.add("all"); b.remove(); }));
    // Nút submit: chống bấm 2 lần + hiện đang xử lý
    $$("form").forEach(f => f.addEventListener("submit", e => { const b = e.submitter; if (b && b.tagName === "BUTTON") { setTimeout(() => { if (!e.defaultPrevented) b.disabled = true; else b.removeAttribute("aria-busy"); }, 0); b.setAttribute("aria-busy", "true"); } }));
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
    // Trang con của bước: widget riêng + lưu (tài khoản → máy chủ; khách → localStorage, đồng bộ khi đăng nhập)
    const sf = $("[data-stepform]");
    if (sf) {
      const KEY = "hn360:step:" + sf.dataset.stepform, st = $("[data-save-status]", sf), SKIP = new Set(["_csrf", "action", "go"]);
      const ser = () => { const o = {}; for (const [k, v] of new FormData(sf)) if (!SKIP.has(k)) (o[k] = o[k] || []).push(v); return o; };
      const wrap = $$("[data-w=list]", sf);
      const renum = w => $$("[data-ord]", w).forEach((e, i) => e.textContent = i + 1);
      const total = r => { const t = $("[data-tot]", r); if (!t) return; const v = $$("select", r).map(s => +s.value).filter(n => n > 0 && n <= 5); t.textContent = v.length ? "Tổng: " + v.reduce((a, b) => a + b, 0) : "Tổng: –"; };
      const addRow = w => { const max = +w.dataset.max || 20, box = $("[data-rows]", w); if (box.children.length >= max) return null;
        box.appendChild($("[data-tpl]", w).content.firstElementChild.cloneNode(true)); renum(w); return box.lastElementChild; };
      const limits = () => $$("[data-max]", sf).forEach(w => { if (w.dataset.w === "list") { $("[data-add]", w).disabled = $("[data-rows]", w).children.length >= +w.dataset.max; return; }
        const bs = $$("input[type=checkbox]", w), n = bs.filter(b => b.checked).length, m = +w.dataset.max;
        bs.forEach(b => { b.disabled = !b.checked && n >= m; }); const c = $("[data-count]", w); if (c) c.textContent = `Đã chọn ${n}/${m}` + (n >= m ? " – đã đủ, bỏ bớt để chọn khác." : "."); });
      const counts = () => { $$("[data-target]", sf).forEach(w => { const n = $$("input:checked", w).length, t = +w.dataset.target, c = $("[data-count]", w);
          c.textContent = `Đã chọn ${n} môn` + (n === t ? " ✓ đúng số môn theo chương trình." : ` – chương trình quy định chọn ${t} môn (tùy nhóm môn trường mở).`); c.classList.toggle("okc", n === t); });
        $$("[data-w=cards]", sf).forEach(w => { const n = $$(".hchk input:checked", w).length; $("[data-count]", w).textContent = n ? `Bạn đã chọn ${n} thói quen/cách làm.` : "Chưa chọn thẻ nào.";
          $$(".hc", w).forEach(h => h.classList.toggle("on", $(".hchk input", h).checked)); });
        $$("[data-row]", sf).forEach(total); limits(); };
      const fill = o => {
        wrap.forEach(w => { const id = w.dataset.id, need = Math.max(0, ...Object.keys(o).filter(k => k.startsWith(id + ".")).map(k => o[k].length)), box = $("[data-rows]", w);
          while (box.children.length < need && addRow(w)); });
        Object.entries(o).forEach(([k, arr]) => $$(`[name="${CSS.escape(k)}"]`, sf).forEach((e, i) => {
          if (e.type === "checkbox" || e.type === "radio") e.checked = arr.includes(e.value); else e.value = arr[i] || ""; }));
        $$(".hc", sf).forEach(h => { if ($(".hchk input", h).checked) $("details", h).open = true; });
      };
      let tm;
      const push = () => fetch("/api/buoc/" + sf.dataset.stepform, { method: "POST", credentials: "same-origin", headers: { "X-CSRF-Token": meta("csrf-token") }, body: new URLSearchParams(new FormData(sf)) })
        .then(r => r.ok ? r.json() : Promise.reject()).then(() => { st.textContent = "✓ Đã lưu vào tài khoản"; }).catch(() => { st.textContent = "Chưa lưu được – kiểm tra kết nối"; });
      const save = () => { clearTimeout(tm); tm = setTimeout(() => { if (LOGGED) push(); else { store.set(KEY, ser()); st.textContent = "✓ Đã lưu tạm trên trình duyệt này"; } }, 600); };
      const local = store.get(KEY, null);
      if (local && (!LOGGED || sf.dataset.has === "0")) { fill(local); if (LOGGED) { push(); localStorage.removeItem(KEY); } }
      sf.addEventListener("input", () => { counts(); save(); }); sf.addEventListener("change", () => { counts(); save(); });
      sf.addEventListener("click", e => { const b = e.target.closest("button[type=button]"); if (!b) return; const w = b.closest("[data-w]"), r = b.closest("[data-row]");
        if (b.hasAttribute("data-add")) { const n = addRow(w); n && $("input,select,textarea", n).focus(); }
        else if (b.hasAttribute("data-del")) { if ($("[data-rows]", w).children.length > 1) r.remove(); else $$("input,select,textarea", r).forEach(x => x.value = ""); }
        else if (b.hasAttribute("data-up") && r.previousElementSibling) r.parentNode.insertBefore(r, r.previousElementSibling);
        else if (b.hasAttribute("data-down") && r.nextElementSibling) r.parentNode.insertBefore(r.nextElementSibling, r);
        renum(w); counts(); save(); });
      sf.addEventListener("submit", () => { if (!LOGGED) store.set(KEY, ser()); });
      counts();
    }
    // Biểu đồ (Chart.js tự lưu trữ)
    if (window.Chart) {
      Chart.defaults.font.family = '"Be Vietnam Pro",system-ui,sans-serif'; Chart.defaults.color = "#5b6478";
      const inc = $("#incdata");
      if (inc) {
        const d = JSON.parse(inc.textContent), fmt = v => v.toLocaleString("vi-VN", { maximumFractionDigits: 1 }) + " triệu";
        new Chart($("#inc"), { type: "bar", data: { labels: d.years, datasets: [
          { label: d.label, data: d.values, backgroundColor: "#2f49d1", borderRadius: 8, maxBarThickness: 48 },
          { label: "Bình quân cả nước", data: d.all, backgroundColor: "#ffb81f", borderRadius: 8, maxBarThickness: 48 }] },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" }, tooltip: { callbacks: { label: c => `${c.dataset.label}: ${fmt(c.raw)}` } } },
            scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: "#eef1f6" }, border: { display: false }, title: { display: true, text: "triệu đồng/tháng" } } } } });
      }
      const rd = $("#rdata");
      if (rd) {
        const d = JSON.parse(rd.textContent);
        new Chart($("#radar"), { type: "radar", data: { labels: d.labels, datasets: [{ label: "Điểm của bạn", data: d.values, borderColor: "#2f49d1", backgroundColor: "rgba(47,73,209,.2)", pointBackgroundColor: "#2f49d1", borderWidth: 2.5 }] },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { r: { min: 0, max: 100, ticks: { stepSize: 25, backdropColor: "transparent" }, pointLabels: { font: { size: 13, weight: "600" } } } } } });
      }
    }
  });
})();
// Khối "Thực hiện hành động": tích việc (localStorage) + accordion cơ sở khoa học
(() => {
  document.querySelectorAll("[data-acts]").forEach(ul => {
    const K = "acts:" + ul.dataset.acts; let st = {};
    try { st = JSON.parse(localStorage.getItem(K) || "{}"); } catch {}
    ul.querySelectorAll("input[data-act]").forEach(cb => {
      cb.checked = !!st[cb.dataset.act];
      cb.addEventListener("change", () => { st[cb.dataset.act] = cb.checked; try { localStorage.setItem(K, JSON.stringify(st)); } catch {} });
    });
  });
  const open = (b, v) => { b.setAttribute("aria-expanded", v); document.getElementById(b.getAttribute("aria-controls")).hidden = !v; };
  document.querySelectorAll(".sci-t").forEach(b => b.addEventListener("click", () => open(b, b.getAttribute("aria-expanded") !== "true")));
  document.querySelectorAll(".actbox a.cite").forEach(a => a.addEventListener("click", () => { const b = a.closest(".actbox").querySelector(".sci-t"); if (b) open(b, true); }));
})();
