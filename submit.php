<?php
// Receives the joinflr.com request forms and emails them to the broker.
// Stored nowhere on the web server; the email is the record.
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

$TO = 'broker@myflroffice.com';
$FROM = 'noreply@joinflr.com';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false}'; exit; }
// Honeypot: bots fill the hidden field. Pretend success, send nothing.
if (!empty($_POST['website'])) { echo '{"ok":true}'; exit; }

function clean($v, $max = 2000) {
    $v = isset($_POST[$v]) ? (string)$_POST[$v] : '';
    $v = trim(str_replace(["\r", "\0"], '', $v));
    return mb_substr($v, 0, $max);
}
function oneline($s) { return trim(preg_replace('/\s+/', ' ', $s)); }

$name  = oneline(clean('name', 120));
$email = oneline(clean('email', 160));
if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(422); echo '{"ok":false,"error":"invalid"}'; exit;
}

$f = [];
foreach (['phone','type','brokerage','stage','school','sponsor','sponsor_slug','first_touch_name','first_touch','first_touch_at','last_touch_name','last_touch','source','page_url','submitted_at'] as $k) {
    $f[$k] = oneline(clean($k, 300));
}
$message = clean('message', 2000);

$sponsor = $f['sponsor'];
$subject = $sponsor !== '' ? "FLR request via $sponsor: $name" : "FLR request: $name";
$subject = oneline($subject);

$lines = [
    "New request from joinflr.com",
    "",
    "Name: $name",
    "Email: $email",
    "Phone: " . $f['phone'],
    "I am: " . $f['type'],
];
if ($f['brokerage'] !== '') $lines[] = "Current brokerage: " . $f['brokerage'];
if ($f['stage'] !== '')     $lines[] = "Licensing status: " . $f['stage'];
if ($f['school'] !== '')    $lines[] = "Licensing school: " . $f['school'];
$lines[] = "";
$lines[] = "SPONSOR TRACKING";
$lines[] = "This page's FLR agent: " . ($sponsor !== '' ? $sponsor . " (" . $f['sponsor_slug'] . ")" : "none (main or audience page)");
$lines[] = "First FLR agent page visited: " . ($f['first_touch_name'] !== '' ? $f['first_touch_name'] . " on " . $f['first_touch_at'] : "none");
$lines[] = "Most recent FLR agent page: " . ($f['last_touch_name'] !== '' ? $f['last_touch_name'] : "none");
$lines[] = "";
$lines[] = "Page: " . $f['page_url'];
$lines[] = "Submitted: " . $f['submitted_at'];
if ($message !== '') { $lines[] = ""; $lines[] = "Message:"; $lines[] = $message; }

$headers = "From: Florida Luxury Realty <$FROM>\r\n"
         . "Reply-To: " . str_replace(["\r","\n"], '', $email) . "\r\n"
         . "Content-Type: text/plain; charset=UTF-8\r\n";

$sent = @mail($TO, '=?UTF-8?B?' . base64_encode($subject) . '?=', implode("\n", $lines), $headers);
if (!$sent) { http_response_code(500); echo '{"ok":false,"error":"mail"}'; exit; }
echo '{"ok":true}';
