<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false}'; exit; }

$raw = file_get_contents('php://input');
$in = json_decode($raw ?: '{}', true);
if (!is_array($in)) $in = [];

$allowed = ['page_view','recipe_open','youtube_play','youtube_outbound_click','youtube_subscribe_click','category_filter'];
$event = isset($in['event']) ? (string)$in['event'] : '';
if (!in_array($event, $allowed, true)) { http_response_code(400); echo '{"ok":false}'; exit; }

function clean($v, $max=180) {
    $s = trim((string)($v ?? ''));
    $s = preg_replace('/[\x00-\x1F\x7F]/u', '', $s);
    return mb_substr($s, 0, $max);
}
$day = gmdate('Y-m-d');
$page = clean($in['page'] ?? '', 180);
$title = clean($in['title'] ?? '', 180);
$video = clean($in['video_id'] ?? '', 32);
$source = clean($in['source'] ?? '', 120);
$utm = clean($in['utm_source'] ?? '', 80);

$dir = __DIR__ . '/../_analytics';
if (!is_dir($dir)) @mkdir($dir, 0755, true);
$ht = $dir . '/.htaccess';
if (!file_exists($ht)) @file_put_contents($ht, "<IfModule mod_authz_core.c>\nRequire all denied\n</IfModule>\n<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n");
$file = $dir . '/counts.json';
$fp = fopen($file, 'c+');
if (!$fp) { http_response_code(500); echo '{"ok":false}'; exit; }
flock($fp, LOCK_EX);
$txt = stream_get_contents($fp);
$d = json_decode($txt ?: '{}', true);
if (!is_array($d)) $d = [];
$d += ['totals'=>[], 'days'=>[], 'recipes'=>[], 'sources'=>[]];
$d['totals'][$event] = (int)($d['totals'][$event] ?? 0) + 1;
if (!isset($d['days'][$day])) $d['days'][$day] = [];
$d['days'][$day][$event] = (int)($d['days'][$day][$event] ?? 0) + 1;
if ($video && in_array($event, ['recipe_open','youtube_play','youtube_outbound_click'], true)) {
    if (!isset($d['recipes'][$video])) $d['recipes'][$video] = ['title'=>$title,'opens'=>0,'plays'=>0,'youtube_clicks'=>0];
    if ($title) $d['recipes'][$video]['title'] = $title;
    if ($event === 'recipe_open') $d['recipes'][$video]['opens']++;
    if ($event === 'youtube_play') $d['recipes'][$video]['plays']++;
    if ($event === 'youtube_outbound_click') $d['recipes'][$video]['youtube_clicks']++;
}
$key = $utm ?: $source;
if ($key && $event === 'page_view') $d['sources'][$key] = (int)($d['sources'][$key] ?? 0) + 1;
ftruncate($fp, 0); rewind($fp);
fwrite($fp, json_encode($d, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
fflush($fp); flock($fp, LOCK_UN); fclose($fp);
echo '{"ok":true}';
