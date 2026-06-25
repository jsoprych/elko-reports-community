<?php
/**
 * Elko Reports — HTML proxy for elko.ai/reports/
 *
 * Serves report HTML files from the GitHub repo with proper Content-Type.
 * Magic happens here: raw.githubusercontent.com serves as text/plain,
 * this proxy re-serves it as text/html so browsers render it.
 *
 * URLs:
 *   /reports/                          → index (list available reports)
 *   /reports/2026-05-02-elko-horizon   → that report's HTML
 *   /reports/2026-05-02-elko-horizon.json → that report's JSON
 *   /reports/2026-05-02-main-street-signals → that report's HTML
 */

const GITHUB_RAW = 'https://raw.githubusercontent.com/jsoprych/elko-reports-community/refs/heads/main';
const REPO_API   = 'https://api.github.com/repos/jsoprych/elko-reports-community/contents/daily';

// ---------- routing ----------

$request = trim($_SERVER['REQUEST_URI'], '/');
$parts   = explode('/', $request);

// Expect: reports/<name>[.<ext>]
if (count($parts) >= 2 && $parts[0] === 'reports') {
    $slug = $parts[1] ?? '';
    if ($slug === '') {
        render_index();
        exit;
    }
    render_report($slug);
    exit;
}

// Fallback: show index
render_index();

// ---------- renderers ----------

function render_index(): void {
    $cache_file = __DIR__ . '/.report_cache.json';
    $reports = null;

    // Use cached list (fresh within 1 hour)
    if (file_exists($cache_file) && (time() - filemtime($cache_file)) < 3600) {
        $reports = json_decode(file_get_contents($cache_file), true);
    }

    if (!$reports) {
        $reports = fetch_report_list();
        if ($reports) {
            file_put_contents($cache_file, json_encode($reports));
        }
    }

    ?><!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Elko Reports — elko.ai</title>
<style>
  :root {
    --bg: #0f0f1a;
    --surface: #1a1a2e;
    --surface-hover: #222240;
    --text: #e2e6f0;
    --text-muted: #8892b0;
    --accent: #4a6cf7;
    --accent-glow: rgba(74,108,247,0.3);
    --border: #2a2a44;
    --radius: 12px;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font: 16px/1.6 -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }
  .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
  header {
    margin-bottom: 48px;
    text-align: center;
  }
  header h1 {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4a6cf7, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
  }
  header p { color: var(--text-muted); font-size: 0.95rem; }
  .report-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .report-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s ease;
    cursor: pointer;
    text-decoration: none;
    color: var(--text);
  }
  .report-card:hover {
    background: var(--surface-hover);
    border-color: var(--accent);
    box-shadow: 0 0 20px var(--accent-glow);
    transform: translateY(-1px);
  }
  .report-info h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 4px;
  }
  .report-info .date {
    font-size: 0.85rem;
    color: var(--text-muted);
  }
  .report-links { display: flex; gap: 8px; }
  .badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .badge-html {
    background: rgba(74,108,247,0.15);
    color: #818cf8;
  }
  .badge-json {
    background: rgba(34,197,94,0.15);
    color: #22c55e;
  }
  .empty {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
  }
  footer {
    margin-top: 48px;
    text-align: center;
    font-size: 0.85rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 24px;
  }
  footer a { color: var(--accent); text-decoration: none; }
  footer a:hover { text-decoration: underline; }
  @media (max-width: 600px) {
    .report-card { flex-direction: column; align-items: flex-start; gap: 12px; }
    .report-links { align-self: flex-end; }
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>📊 Elko Reports</h1>
    <p>Daily intelligence briefings &amp; local business insights</p>
  </header>

  <?php if ($reports && count($reports) > 0): ?>
  <div class="report-grid">
    <?php foreach ($reports as $r):
      $name = preg_replace('/\.\w+$/', '', $r['name']);
      // Skip .gitkeep or hidden files
      if (str_starts_with($r['name'], '.')) continue;
      $is_html = str_ends_with($r['name'], '.html');
      $is_json = str_ends_with($r['name'], '.json');
      $basename = $r['name'];
      $display_name = $basename;
    ?>
    <a href="<?= htmlspecialchars($name) ?>" class="report-card">
      <div class="report-info">
        <h3><?= htmlspecialchars($display_name) ?></h3>
        <div class="date"><?= date('F j, Y', strtotime(substr($basename, 0, 10))) ?></div>
      </div>
      <div class="report-links">
        <?php if ($is_html): ?>
          <span class="badge badge-html">HTML</span>
        <?php elseif ($is_json): ?>
          <span class="badge badge-json">JSON</span>
        <?php endif; ?>
      </div>
    </a>
    <?php endforeach; ?>
  </div>
  <?php else: ?>
    <div class="empty">
      <p>No reports available yet. Check back soon.</p>
    </div>
  <?php endif; ?>

  <footer>
    Generated by <a href="https://elko.ai">elko.ai</a> —
    <a href="https://github.com/jsoprych/elko-reports-community">Source on GitHub</a>
  </footer>
</div>
</body>
</html>
<?php
}

function render_report(string $slug): void {
    // Determine extension
    if (str_ends_with($slug, '.json')) {
        $file = $slug;
        $mime = 'application/json';
    } else {
        $slug = preg_replace('/\.html?$/i', '', $slug);
        $file = $slug . '.html';
        $mime = 'text/html';
    }

    $url = GITHUB_RAW . '/daily/' . $file;
    $ctx = stream_context_create(['http' => ['timeout' => 10, 'user_agent' => 'elko-reports/1.0']]);
    $content = @file_get_contents($url, false, $ctx);

    if ($content === false) {
        http_response_code(404);
        ?><!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Not Found — Elko Reports</title>
<style>body{font:16px/1.6 sans-serif;background:#0f0f1a;color:#e2e6f0;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.container{text-align:center}h1{font-size:3rem;color:#4a6cf7;margin-bottom:8px}p{color:#8892b0}a{color:#818cf8}</style></head>
<body><div class="container"><h1>404</h1><p>Report not found: <?= htmlspecialchars($file) ?></p>
<p><a href="/reports/">← Back to reports</a></p></div></body></html>
<?php
        return;
    }

    header('Content-Type: ' . $mime . '; charset=utf-8');
    header('Access-Control-Allow-Origin: *');
    header('X-Proxy: elko-reports-gateway');
    echo $content;
}

function fetch_report_list(): ?array {
    $ctx = stream_context_create(['http' => ['timeout' => 10, 'user_agent' => 'elko-reports/1.0']]);
    $json = @file_get_contents(REPO_API, false, $ctx);
    if ($json === false) return null;
    $data = json_decode($json, true);
    if (!$data || !is_array($data)) return null;

    // Filter to .html and .json files, sort newest first
    $files = array_filter($data, fn($f) => (
        isset($f['name']) &&
        (str_ends_with($f['name'], '.html') || str_ends_with($f['name'], '.json')) &&
        !str_starts_with($f['name'], '.')
    ));
    usort($files, fn($a, $b) => strcmp($b['name'], $a['name']));
    return array_values($files);
}
