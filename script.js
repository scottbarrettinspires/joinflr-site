// ---- Site settings: edit these two values, nothing else needs to change ----
// FORM_ENDPOINT: URL that accepts a JSON POST (Jotform, Zapier catch hook, etc.).
// Leave empty to fall back to opening the visitor's email app addressed to CONTACT_EMAIL.
var FORM_ENDPOINT = "";
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

    if (FORM_ENDPOINT) {
      say("Sending...");
      fetch(FORM_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: "joinflr.com",
          name: d.name, email: d.email, phone: d.phone,
          type: d.type, brokerage: d.brokerage, message: d.message
        })
      }).then(function (r) {
        if (!r.ok) { throw new Error("bad status"); }
        form.reset();
        say("Thank you. Scott will be in touch personally.", "ok");
      }).catch(function () {
        say("Something went wrong. Please email " + CONTACT_EMAIL + ".", "err");
      });
      return;
    }

    var body = [
      "Name: " + d.name,
      "Email: " + d.email,
      "Phone: " + (d.phone || ""),
      "I am: " + d.type,
      "Current brokerage: " + (d.brokerage || ""),
      "",
      d.message || ""
    ].join("\n");
    window.location.href = "mailto:" + CONTACT_EMAIL +
      "?subject=" + encodeURIComponent("Interested in joining FLR") +
      "&body=" + encodeURIComponent(body);
    say("Your email app should open with your details ready to send.", "ok");
  });
})();

(function(){try{document.documentElement.classList.add("js");var els=document.querySelectorAll(".reveal");if(!("IntersectionObserver" in window)){els.forEach(function(e){e.classList.add("in")});return;}
var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add("in");io.unobserve(x.target)}})},{threshold:.15});els.forEach(function(e,i){e.style.transitionDelay=(i%3)*90+"ms";io.observe(e)});}catch(e){document.querySelectorAll(".reveal").forEach(function(x){x.classList.add("in")})}})();
