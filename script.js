// ---- Site settings: edit these two values, nothing else needs to change ----
// FORM_ENDPOINT: URL that accepts a JSON POST (Jotform, Zapier catch hook, etc.).
// Leave empty to fall back to opening the visitor's email app addressed to CONTACT_EMAIL.
var FORM_ENDPOINT = "/submit.php";
var CONTACT_EMAIL = "broker@myflroffice.com";
// ----------------------------------------------------------------------------

(function () {
  document.getElementById("year").textContent = new Date().getFullYear();

  var btn = document.querySelector(".menu-btn");
  var menu = document.getElementById("menu");
  btn.addEventListener("click", function () {
    var open = menu.classList.toggle("open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
  menu.addEventListener("click", function (e) {
    if (e.target.tagName === "A") {
      menu.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
    }
  });

  // Remember which FLR agent's page a visitor came from (first and most recent), for sponsor tracking.
  function attribution() {
    var out = { first: null, last: null };
    try {
      var ref = window.FLR_REF, now = new Date().toISOString(), DAYS = 90 * 864e5;
      var first = JSON.parse(localStorage.getItem("flr_ref_first") || "null");
      var last = JSON.parse(localStorage.getItem("flr_ref_last") || "null");
      if (first && Date.now() - Date.parse(first.ts) > DAYS) { first = null; }
      if (ref && ref.slug) {
        if (!first) { first = { slug: ref.slug, name: ref.name, ts: now }; localStorage.setItem("flr_ref_first", JSON.stringify(first)); }
        last = { slug: ref.slug, name: ref.name, ts: now }; localStorage.setItem("flr_ref_last", JSON.stringify(last));
      }
      out.first = first; out.last = last;
    } catch (err) {}
    return out;
  }
  attribution();

  var form = document.getElementById("lead-form");
  var status = document.getElementById("form-status");

  function say(msg, cls) {
    status.textContent = msg;
    status.className = "status " + (cls || "");
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var d = {};
    new FormData(form).forEach(function (v, k) { d[k] = String(v).trim(); });

    if (d.website) { return; } // honeypot
    if (!d.name || !/^\S+@\S+\.\S+$/.test(d.email || "")) {
      say("Please add your name and a valid email.", "err");
      return;
    }

    var meta = attribution();
    var payload = {
      source: form.getAttribute("data-source") || "joinflr.com",
      submitted_at: new Date().toISOString(), page_url: location.href,
      name: d.name, email: d.email, phone: d.phone,
      type: d.type || "", brokerage: d.brokerage || "", stage: d.stage || "", school: d.school || "", message: d.message || "",
      sponsor: d.sponsor || "", sponsor_slug: d.sponsor_slug || "",
      first_touch: meta.first ? meta.first.slug : "", first_touch_name: meta.first ? meta.first.name : "", first_touch_at: meta.first ? meta.first.ts : "",
      last_touch: meta.last ? meta.last.slug : "", last_touch_name: meta.last ? meta.last.name : ""
    };

    function mailtoFallback() {
      var body = [
        "Name: " + d.name,
        "Email: " + d.email,
        "Phone: " + (d.phone || ""),
        "I am: " + d.type,
        "Current brokerage: " + (d.brokerage || ""),
        d.stage ? "Licensing status: " + d.stage : "",
        d.school ? "Licensing school: " + d.school : "",
        payload.sponsor ? "Introduced by (FLR agent): " + payload.sponsor : (payload.first_touch_name ? "Earlier introduced by: " + payload.first_touch_name : ""),
        "",
        d.message || ""
      ].join("\n");
      window.location.href = "mailto:" + CONTACT_EMAIL +
        "?subject=" + encodeURIComponent(form.getAttribute("data-subject") || "Interested in joining FLR") +
        "&body=" + encodeURIComponent(body);
      say("Your email app should open with your details ready to send.", "ok");
    }

    function done() {
      var box = document.createElement("div");
      box.className = "form-done"; box.setAttribute("role", "status");
      box.innerHTML = '<span class="form-done-ic" aria-hidden="true">&#10003;</span><h3>Your request has been submitted</h3><p>Scott will reach out to you soon and looks forward to speaking with you.</p>';
      form.replaceWith(box);
      box.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    if (FORM_ENDPOINT) {
      say("Sending...");
      var sbtn = form.querySelector("button[type=submit]"); if (sbtn) { sbtn.disabled = true; }
      fetch(FORM_ENDPOINT, { method: "POST", body: new URLSearchParams(payload) })
        .then(function (r) { return r.json().catch(function () { return {}; }); })
        .then(function (j) { if (!j.ok) { throw new Error("not ok"); } done(); })
        .catch(function () {
          // Server unavailable: fall back to the visitor's email app so the request is never lost.
          if (sbtn) { sbtn.disabled = false; }
          say("", "");
          mailtoFallback();
        });
      return;
    }

    mailtoFallback();
  });
})();

(function(){try{document.documentElement.classList.add("js");var els=document.querySelectorAll(".reveal");if(!("IntersectionObserver" in window)){els.forEach(function(e){e.classList.add("in")});return;}
var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add("in");io.unobserve(x.target)}})},{threshold:.15});els.forEach(function(e,i){e.style.transitionDelay=(i%3)*90+"ms";io.observe(e)});}catch(e){document.querySelectorAll(".reveal").forEach(function(x){x.classList.add("in")})}})();

(function(){var b=document.querySelector(".brand");if(!b)return;b.addEventListener("click",function(e){e.preventDefault();window.scrollTo({top:0,behavior:"smooth"});try{history.replaceState(null,"",location.pathname)}catch(x){}})})();
