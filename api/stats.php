<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate');
$file = __DIR__ . '/../_analytics/counts.json';
$d = file_exists($file) ? json_decode((string)file_get_contents($file), true) : [];
if (!is_array($d)) $d = [];
$d += ['totals'=>[], 'days'=>[], 'recipes'=>[], 'sources'=>[]];
$today = gmdate('Y-m-d');
$tot = $d['totals'];
$out = [
  'ok'=>true,
  'totals'=>[
    'page_view'=>(int)($tot['page_view'] ?? 0),
    'recipe_open'=>(int)($tot['recipe_open'] ?? 0),
    'youtube_play'=>(int)($tot['youtube_play'] ?? 0),
    'youtube_outbound_click'=>(int)($tot['youtube_outbound_click'] ?? 0),
    'youtube_subscribe_click'=>(int)($tot['youtube_subscribe_click'] ?? 0),
  ],
  'today'=>$d['days'][$today] ?? [],
  'recipes'=>$d['recipes'],
  'sources'=>$d['sources'],
];
echo json_encode($out, JSON_UNESCAPED_UNICODE);
