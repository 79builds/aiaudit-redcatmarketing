<?php
// AI Visibility Audit form handler. POST only. No third-party dependencies.
// SET THE RECIPIENT BELOW BEFORE GOING LIVE (confirm with Caleb / Red Cat).
const RECIPIENT  = '';                                  // e.g. 'audits@redcatmarketing.ca'
const FROM_EMAIL = 'noreply@aiaudit.redcatmarketing.ca'; // must be a mailbox/domain on this hosting for deliverability
const SUBJECT    = 'New AI Visibility Audit request';

function back_with_error(): void { header('Location: /?error=1#get-audit', true, 303); exit; }

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405); header('Allow: POST'); exit('Method not allowed');
}

// Honeypot: bots fill it. Pretend success, send nothing.
if (trim((string)($_POST['website_url_confirm'] ?? '')) !== '') {
    header('Location: /thank-you.html', true, 303); exit;
}

// Strip control chars (kills header injection); single-line fields lose newlines too.
function clean(string $v, int $max, bool $multiline = false): string {
    $v = str_replace("\0", '', $v);
    $v = $multiline ? preg_replace('/[^\P{C}\n]+/u', '', str_replace("\r\n", "\n", $v))
                    : preg_replace('/\p{C}+/u', ' ', $v);
    $v = trim((string)$v);
    return function_exists('mb_substr') ? mb_substr($v, 0, $max) : substr($v, 0, $max);
}

$first = clean((string)($_POST['first_name'] ?? ''), 80);
$last  = clean((string)($_POST['last_name'] ?? ''), 80);
$email = clean((string)($_POST['email'] ?? ''), 254);
$site  = clean((string)($_POST['website'] ?? ''), 300);
$area  = clean((string)($_POST['service_area'] ?? ''), 20);
$geo   = clean((string)($_POST['geo_area'] ?? ''), 300);
$comp  = clean((string)($_POST['competitors'] ?? ''), 1500, true);
$notes = clean((string)($_POST['notes'] ?? ''), 3000, true);

if ($area !== '' && !in_array($area, ['global', 'national', 'regional', 'local'], true)) $area = '';
if ($first === '' || $last === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) back_with_error();
if (!preg_match('~^https?://~i', $site)) $site = 'https://' . $site;
if (!filter_var($site, FILTER_VALIDATE_URL) || !preg_match('~^https?://[^\s/]+\.[^\s/]+~i', $site)) back_with_error();
if (RECIPIENT === '') { error_log('send.php: RECIPIENT not configured'); back_with_error(); }

$body  = "New AI Visibility Audit request\n\n";
$body .= "Name: $first $last\nEmail: $email\nWebsite: $site\n";
$body .= "Geo-area served: " . ($area ?: '(not given)') . "\nMain location(s): " . ($geo ?: '(not given)') . "\n\n";
$body .= "Top 3 competitors:\n" . ($comp ?: '(not given)') . "\n\n";
$body .= "Anything else:\n" . ($notes ?: '(none)') . "\n\n";
$body .= "Submitted: " . gmdate('Y-m-d H:i') . " UTC\n";

$headers = [
    'From: Red Cat AI Audit <' . FROM_EMAIL . '>',
    'Reply-To: ' . $email,                       // validated + control chars stripped above
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: aiaudit-form',
];
$ok = mail(RECIPIENT, '=?UTF-8?B?' . base64_encode(SUBJECT . ' - ' . $first . ' ' . $last) . '?=', $body, implode("\r\n", $headers));
if (!$ok) { error_log('send.php: mail() failed'); back_with_error(); }

header('Location: /thank-you.html', true, 303);
exit;
