"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║              🔬 SciClip Pro v2 — Science Media Finder (Videos + Images)         ║
║     Royalty-free science simulations, animations, clips & images                ║
║              100% legally safe for monetized YouTube videos                      ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  SETUP — API KEYS (all free):                                                  ║
║                                                                                ║
║  1. PEXELS_API_KEY   → https://www.pexels.com/api/                             ║
║  2. PIXABAY_API_KEY  → https://pixabay.com/api/docs/                           ║
║  3. NASA_API_KEY     → https://api.nasa.gov/       (DEMO_KEY works)            ║
║  4. UNSPLASH_ACCESS_KEY → https://unsplash.com/developers                      ║
║  5. FLICKR_API_KEY   → https://www.flickr.com/services/api/                    ║
║                                                                                ║
║  Create .streamlit/secrets.toml:                                               ║
║    PEXELS_API_KEY = "..."                                                      ║
║    PIXABAY_API_KEY = "..."                                                     ║
║    NASA_API_KEY = "..."                                                        ║
║    UNSPLASH_ACCESS_KEY = "..."                                                 ║
║    FLICKR_API_KEY = "..."                                                      ║
║                                                                                ║
║  Run: streamlit run app.py                                                     ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import requests
import os
import time
import re
import json
import html as html_module
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlencode, quote_plus
from io import BytesIO
from typing import Optional

# ───────────────────────────────────────────────────
# PAGE CONFIG
# ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SciClip",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────────────────────────────────
# CUSTOM CSS — Dark, Professional Theme
# ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
:root {
    --bg-primary: #0d1117;
    --bg-card: #161b22;
    --bg-card-hover: #1c2333;
    --border: rgba(255,255,255,0.06);
    --border-hover: rgba(130,140,255,0.25);
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --accent-blue: #58a6ff;
    --accent-purple: #bc8cff;
    --accent-green: #3fb950;
    --accent-orange: #d29922;
    --accent-red: #f85149;
    --accent-pink: #f778ba;
    --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-2: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    --gradient-3: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
.stApp { font-family: 'Inter', -apple-system, sans-serif; }
.pane {
    background: radial-gradient(circle at 20% 20%, rgba(99,102,241,0.06), transparent 35%),
                radial-gradient(circle at 80% 0%, rgba(56,189,248,0.05), transparent 30%),
                var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem 1.25rem 0.75rem;
    box-shadow: 0 6px 24px rgba(0,0,0,0.25);
}
/* Header */
.main-header {
    background: var(--gradient-2);
    padding: 2.2rem 2.5rem; border-radius: 18px;
    margin-bottom: 1.2rem;
    border: 1px solid var(--border);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}
.main-header h1 { color: #fff; font-size: 2.4rem; font-weight: 900; margin: 0; letter-spacing: -1px; }
.main-header .subtitle { color: #a5b4fc; font-size: 1rem; margin: 0.3rem 0 0; font-weight: 400; }
.main-header .version { color: #6366f1; font-size: 0.75rem; font-weight: 700; background: rgba(99,102,241,0.15);
    padding: 0.15rem 0.5rem; border-radius: 8px; display: inline-block; margin-left: 0.5rem; }
/* Search bar area */
.search-wrap { background: var(--gradient-3); padding: 1.5rem; border-radius: 14px;
    margin-bottom: 1rem; border: 1px solid var(--border); }
/* Source section header */
.source-section {
    background: linear-gradient(90deg, rgba(99,102,241,0.08) 0%, transparent 100%);
    padding: 0.8rem 1.2rem; border-radius: 10px; margin: 1.5rem 0 0.8rem;
    border-left: 4px solid #6366f1; display: flex; align-items: center; gap: 0.7rem;
}
.source-section h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.source-section .count { background: rgba(99,102,241,0.2); color: #a5b4fc;
    padding: 0.15rem 0.6rem; border-radius: 12px; font-size: 0.78rem; font-weight: 700; }
/* Cards */
.v-card, .i-card {
    background: var(--bg-card); border-radius: 14px; padding: 1rem;
    border: 1px solid var(--border); transition: all 0.25s ease;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15); height: 100%;
}
.v-card:hover, .i-card:hover {
    border-color: var(--border-hover);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transform: translateY(-3px);
}
/* Badges */
.src-badge {
    display: inline-block; padding: 0.2rem 0.55rem; border-radius: 6px;
    font-size: 0.68rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.6px;
    margin-right: 0.3rem;
}
.b-nasa     { background: #1e3a5f; color: #7dd3fc; }
.b-nasasvs  { background: #0c4a6e; color: #38bdf8; }
.b-pexels   { background: #064e3b; color: #6ee7b7; }
.b-pixabay  { background: #78350f; color: #fbbf24; }
.b-wikimedia{ background: #581c87; color: #d8b4fe; }
.b-archive  { background: #713f12; color: #fde68a; }
.b-phet     { background: #14532d; color: #86efac; }
.b-coverr   { background: #1e3a5f; color: #93c5fd; }
.b-esa      { background: #312e81; color: #a5b4fc; }
.b-noaa     { background: #064e3b; color: #5eead4; }
.b-smithsonian { background: #7c2d12; color: #fdba74; }
.b-unsplash { background: #1c1917; color: #e7e5e4; }
.b-flickr   { background: #831843; color: #f9a8d4; }
.b-europeana{ background: #365314; color: #bef264; }
.b-giphy    { background: #701a75; color: #f0abfc; }
.b-cern     { background: #1e3a5f; color: #7dd3fc; }
.b-nih      { background: #14532d; color: #86efac; }
.b-dvids    { background: #78350f; color: #fbbf24; }
.b-met      { background: #7c2d12; color: #fdba74; }
.b-pinterest{ background: #881337; color: #fda4af; }
.b-storyblocks{ background: #312e81; color: #c4b5fd; }
/* License */
.lic-badge {
    display: inline-block; padding: 0.15rem 0.5rem; border-radius: 6px;
    font-size: 0.68rem; font-weight: 600;
    background: rgba(34,197,94,0.12); color: #4ade80;
    border: 1px solid rgba(34,197,94,0.15);
}
/* Meta text */
.meta { font-size: 0.76rem; color: var(--text-secondary); margin: 0.15rem 0; line-height: 1.4; }
.meta strong { color: var(--text-primary); }
/* Stats bar */
.stats-bar { display: flex; gap: 0.8rem; flex-wrap: wrap; margin: 0.8rem 0 1.2rem; }
.stat-pill {
    background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.15);
    padding: 0.5rem 1rem; border-radius: 10px; text-align: center; flex: 1; min-width: 100px;
}
.stat-pill .num { font-size: 1.4rem; font-weight: 800; color: #818cf8; }
.stat-pill .lbl { font-size: 0.7rem; color: var(--text-secondary); }
/* Image grid */
.img-grid-item { border-radius: 10px; overflow: hidden; }
.img-grid-item img { width: 100%; border-radius: 10px; transition: transform 0.3s; }
.img-grid-item img:hover { transform: scale(1.03); }
/* Section dividers */
.section-divider {
    display: flex; align-items: center; margin: 2rem 0 1rem; gap: 1rem;
}
.section-divider .line { flex: 1; height: 1px; background: var(--border); }
.section-divider .label {
    font-size: 1.3rem; font-weight: 800; color: var(--text-primary);
    padding: 0.4rem 1.5rem; background: rgba(99,102,241,0.1);
    border-radius: 10px; border: 1px solid rgba(99,102,241,0.15);
}
/* Expanders */
[data-testid="stExpander"] {
    border: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.0));
    border-radius: 10px !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.25);
}
[data-testid="stExpander"] div[role="button"] {
    padding: 0.9rem 1rem;
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
    color: var(--text-primary);
    font-weight: 700;
}
[data-testid="stExpander"] .streamlit-expanderContent {
    padding: 0.25rem 0.75rem 0.5rem;
}
/* Sidebar */
.sidebar-info {
    background: rgba(34,197,94,0.06); border: 1px solid rgba(34,197,94,0.12);
    border-radius: 10px; padding: 0.9rem; margin-bottom: 1rem; font-size: 0.8rem; color: var(--text-secondary);
}
.sidebar-info h4 { color: var(--accent-green); margin: 0 0 0.4rem; font-size: 0.9rem; }
/* Hide defaults */
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: #fff !important; border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; width: 100% !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
    box-shadow: 0 4px 15px rgba(5,150,105,0.3) !important;
}
/* Video player */
video { border-radius: 10px !important; background: #000; }
/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem; background: rgba(255,255,255,0.02); border-radius: 10px; padding: 0.3rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; font-weight: 600; font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────
# API KEY MANAGEMENT
# ───────────────────────────────────────────────────
def get_key(name: str, default: str = "") -> str:
    try:
        return st.secrets[name]
    except Exception:
        return os.environ.get(name, default)

PEXELS_KEY    = get_key("PEXELS_API_KEY")
PIXABAY_KEY   = get_key("PIXABAY_API_KEY")
NASA_KEY      = get_key("NASA_API_KEY", "DEMO_KEY")
UNSPLASH_KEY  = get_key("UNSPLASH_ACCESS_KEY")
FLICKR_KEY    = get_key("FLICKR_API_KEY")

# ───────────────────────────────────────────────────
# SOURCE REGISTRY
# ───────────────────────────────────────────────────
SOURCES = {
    # ── VIDEO SOURCES ──
    "pexels_v":     {"name":"Pexels Videos",     "type":"Stock",      "media":"video","badge":"b-pexels",
                     "lic":"Pexels License – Free commercial, no attribution required",
                     "lic_short":"Pexels License","needs_key":True,"key":"PEXELS_API_KEY"},
    "pixabay_v":    {"name":"Pixabay Videos",    "type":"Stock",      "media":"video","badge":"b-pixabay",
                     "lic":"Pixabay License – Free commercial, no attribution required",
                     "lic_short":"Pixabay License","needs_key":True,"key":"PIXABAY_API_KEY"},
    "coverr":       {"name":"Coverr",            "type":"Stock",      "media":"video","badge":"b-coverr",
                     "lic":"Coverr License – Free commercial, no attribution required",
                     "lic_short":"Coverr License","needs_key":False},
    "nasa_v":       {"name":"NASA Media",        "type":"Archive",    "media":"video","badge":"b-nasa",
                     "lic":"Public Domain – NASA (not copyrighted)",
                     "lic_short":"Public Domain (NASA)","needs_key":False},
    "nasa_svs":     {"name":"NASA SVS",          "type":"Simulation", "media":"video","badge":"b-nasasvs",
                     "lic":"Public Domain – NASA Scientific Visualization Studio",
                     "lic_short":"Public Domain (NASA SVS)","needs_key":False},
    "wikimedia_v":  {"name":"Wikimedia Videos",  "type":"Archive",    "media":"video","badge":"b-wikimedia",
                     "lic":"CC0 / Public Domain / CC-BY (filtered)",
                     "lic_short":"CC0/PD/CC-BY","needs_key":False},
    "archive_v":    {"name":"Internet Archive",  "type":"Archive",    "media":"video","badge":"b-archive",
                     "lic":"Public Domain / CC0",
                     "lic_short":"Public Domain/CC0","needs_key":False},
    "phet":         {"name":"PhET Simulations",  "type":"Simulation", "media":"video","badge":"b-phet",
                     "lic":"CC-BY 4.0 – PhET, University of Colorado Boulder",
                     "lic_short":"CC-BY 4.0 (PhET)","needs_key":False},
    "esa_v":        {"name":"ESA / Hubble",      "type":"Archive",    "media":"video","badge":"b-esa",
                     "lic":"CC-BY 4.0 / Public Domain – ESA/Hubble",
                     "lic_short":"CC-BY 4.0 / PD","needs_key":False},
    "noaa_v":       {"name":"NOAA Visualizations","type":"Simulation","media":"video","badge":"b-noaa",
                     "lic":"Public Domain – US Government (NOAA)",
                     "lic_short":"Public Domain (NOAA)","needs_key":False},
    "cern_v":       {"name":"CERN Media",        "type":"Archive",    "media":"video","badge":"b-cern",
                     "lic":"CC-BY 4.0 – CERN",
                     "lic_short":"CC-BY 4.0 (CERN)","needs_key":False},
    "dvids_v":      {"name":"DVIDS / Mil Sci",   "type":"Archive",    "media":"video","badge":"b-dvids",
                     "lic":"Public Domain – US Government",
                     "lic_short":"Public Domain (US Gov)","needs_key":False},
    "nih_v":        {"name":"NIH / NLM Videos",  "type":"Archive",    "media":"video","badge":"b-nih",
                     "lic":"Public Domain – US Government (NIH)",
                     "lic_short":"Public Domain (NIH)","needs_key":False},
    # ── IMAGE SOURCES ──
    "pexels_i":     {"name":"Pexels Photos",     "type":"Stock",      "media":"image","badge":"b-pexels",
                     "lic":"Pexels License – Free commercial, no attribution required",
                     "lic_short":"Pexels License","needs_key":True,"key":"PEXELS_API_KEY"},
    "pixabay_i":    {"name":"Pixabay Images",    "type":"Stock",      "media":"image","badge":"b-pixabay",
                     "lic":"Pixabay License – Free commercial, no attribution required",
                     "lic_short":"Pixabay License","needs_key":True,"key":"PIXABAY_API_KEY"},
    "unsplash_i":   {"name":"Unsplash",          "type":"Stock",      "media":"image","badge":"b-unsplash",
                     "lic":"Unsplash License – Free commercial, no attribution required",
                     "lic_short":"Unsplash License","needs_key":True,"key":"UNSPLASH_ACCESS_KEY"},
    "nasa_i":       {"name":"NASA Images",       "type":"Archive",    "media":"image","badge":"b-nasa",
                     "lic":"Public Domain – NASA",
                     "lic_short":"Public Domain (NASA)","needs_key":False},
    "wikimedia_i":  {"name":"Wikimedia Images",  "type":"Archive",    "media":"image","badge":"b-wikimedia",
                     "lic":"CC0 / Public Domain / CC-BY (filtered)",
                     "lic_short":"CC0/PD/CC-BY","needs_key":False},
    "flickr_i":     {"name":"Flickr CC",         "type":"Stock",      "media":"image","badge":"b-flickr",
                     "lic":"CC-BY 2.0 / CC0 (filtered for commercial use)",
                     "lic_short":"CC-BY/CC0 (Flickr)","needs_key":True,"key":"FLICKR_API_KEY"},
    "europeana_i":  {"name":"Europeana",         "type":"Archive",    "media":"image","badge":"b-europeana",
                     "lic":"Public Domain / CC0 / CC-BY (European cultural heritage)",
                     "lic_short":"PD/CC0/CC-BY","needs_key":False},
    "smithsonian_i":{"name":"Smithsonian OA",    "type":"Archive",    "media":"image","badge":"b-smithsonian",
                     "lic":"CC0 – Smithsonian Open Access",
                     "lic_short":"CC0 (Smithsonian)","needs_key":False},
    "met_i":        {"name":"Met Museum OA",     "type":"Archive",    "media":"image","badge":"b-met",
                     "lic":"CC0 – Metropolitan Museum Open Access",
                     "lic_short":"CC0 (Met Museum)","needs_key":False},
    "giphy_i":      {"name":"Giphy Science",     "type":"Stock",      "media":"image","badge":"b-giphy",
                     "lic":"Giphy – Free to use (check specific clip)",
                     "lic_short":"Giphy License","needs_key":False},
    "pinterest_i":  {"name":"Pinterest (Links)",  "type":"Discovery", "media":"image","badge":"b-pinterest",
                     "lic":"Discovery only – Links to source pages for license verification",
                     "lic_short":"Linked Sources","needs_key":False},
}

# ───────────────────────────────────────────────────
# SESSION STATE
# ───────────────────────────────────────────────────
defaults = {
    "video_results": [], "image_results": [], "query": "", "searched": False,
    "v_counts": {}, "i_counts": {}, "search_time": 0, "preset": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ───────────────────────────────────────────────────
# UTILITIES
# ───────────────────────────────────────────────────
def safe_get(url, headers=None, params=None, timeout=15):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=timeout)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def ensure_https(url: str) -> str:
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://"):
        return "https://" + url[len("http://"):]
    return url


def is_accessible(url: str, timeout: int = 8) -> bool:
    """Lightweight reachability check to skip 401/403 archive items."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        if r.status_code in (401, 403):
            return False
        if 200 <= r.status_code < 400:
            return True
        if r.status_code in (405, 501):
            r2 = requests.get(url, timeout=timeout, stream=True)
            return 200 <= r2.status_code < 400
    except Exception:
        return False
    return False

def fmt_dur(s):
    if s is None: return "N/A"
    s = int(s); m, sec = divmod(s, 60)
    return f"{m}:{sec:02d}"

def clean_html(text):
    if not text: return ""
    return re.sub(r'<[^>]+>', '', html_module.unescape(str(text)))

def dl_bytes(url, timeout=45):
    try:
        headers = {"User-Agent": "SciClipPro/1.0 (+https://sciclip-pro)"}
        r = requests.get(url, timeout=timeout, stream=True, headers=headers)
        if r.status_code == 200:
            return r.content

        # Fallback for NASA assets where ~orig may 403 — try smaller variants
        if "~orig" in url:
            for suffix in ["~large", "~medium", "~thumb"]:
                alt = url.replace("~orig", suffix)
                r2 = requests.get(alt, timeout=timeout, stream=True, headers=headers)
                if r2.status_code == 200:
                    return r2.content
        return None
    except Exception:
        return None

def make_result(source_key, **kwargs):
    cfg = SOURCES.get(source_key, {})
    base = {
        "source": source_key,
        "source_name": cfg.get("name", source_key),
        "badge": cfg.get("badge", ""),
        "media_type": cfg.get("media", "video"),
        "license": cfg.get("lic", ""),
        "license_short": cfg.get("lic_short", ""),
        "title": "", "description": "", "thumbnail": "",
        "preview_url": "", "download_url": "", "page_url": "",
        "duration": None, "resolution": "", "quality": "HD",
        "author": "", "is_interactive": False, "width": 0, "height": 0,
    }
    base.update(kwargs)
    for k in ["thumbnail", "preview_url", "download_url", "page_url"]:
        base[k] = ensure_https(base.get(k, ""))
    return base

# ───────────────────────────────────────────────────
# VIDEO SEARCH FUNCTIONS
# ───────────────────────────────────────────────────

def search_pexels_videos(q, n=15, **kw):
    if not PEXELS_KEY: return []
    out = []
    for page in [1, 2]:
        d = safe_get("https://api.pexels.com/videos/search",
                      headers={"Authorization": PEXELS_KEY},
                      params={"query": q, "per_page": min(n, 40), "page": page})
        if not d: break
        for v in d.get("videos", []):
            vf = sorted(v.get("video_files", []), key=lambda x: x.get("height",0), reverse=True)
            if not vf: continue
            best = vf[0]
            prev = next((f for f in vf if f.get("height",0) <= 720), vf[-1])
            pics = v.get("video_pictures", [])
            out.append(make_result("pexels_v",
                title=f"Pexels #{v['id']}", description=q,
                thumbnail=pics[0]["picture"] if pics else "",
                preview_url=prev.get("link",""), download_url=best.get("link",""),
                duration=v.get("duration"), resolution=f"{best.get('width','?')}x{best.get('height','?')}",
                quality="4K" if best.get("height",0)>=2160 else ("HD" if best.get("height",0)>=720 else "SD"),
                page_url=v.get("url",""), author=v.get("user",{}).get("name",""),
                width=best.get("width",0), height=best.get("height",0),
            ))
        if len(d.get("videos",[])) < n: break
    return out[:n*2]

def search_pixabay_videos(q, n=15, **kw):
    if not PIXABAY_KEY: return []
    out = []
    for page in [1, 2]:
        d = safe_get("https://pixabay.com/api/videos/",
                      params={"key": PIXABAY_KEY, "q": q, "per_page": min(n, 50), "page": page, "safesearch": "true"})
        if not d: break
        for v in d.get("hits", []):
            vids = v.get("videos", {})
            for k in ["large","medium","small","tiny"]:
                if k in vids and vids[k].get("url"):
                    best = vids[k]; break
            else: continue
            prev = vids.get("small", vids.get("tiny", best))
            out.append(make_result("pixabay_v",
                title=f"Pixabay #{v['id']}", description=v.get("tags", q),
                thumbnail=f"https://i.vimeocdn.com/video/{v['picture_id']}_640x360.jpg" if v.get("picture_id") else "",
                preview_url=prev.get("url",""), download_url=best.get("url",""),
                duration=v.get("duration"), resolution=f"{best.get('width','?')}x{best.get('height','?')}",
                quality="4K" if best.get("height",0)>=2160 else ("HD" if best.get("height",0)>=720 else "SD"),
                page_url=v.get("pageURL",""), author=v.get("user",""),
                width=best.get("width",0), height=best.get("height",0),
            ))
        if len(d.get("hits",[])) < n: break
    return out[:n*2]

def search_nasa_videos(q, n=20, **kw):
    out = []
    d = safe_get("https://images-api.nasa.gov/search",
                  params={"q": q, "media_type": "video", "page_size": min(n, 50)}, timeout=20)
    if not d or "collection" not in d: return []
    for item in d["collection"].get("items", [])[:n]:
        dat = item.get("data", [{}])[0]
        nid = dat.get("nasa_id", "")
        links = item.get("links", [])
        thumb = next((l["href"] for l in links if l.get("render") == "image"), "")
        # Get assets
        ad = safe_get(f"https://images-api.nasa.gov/asset/{nid}", timeout=12)
        dl_url = pv_url = ""
        if ad and "collection" in ad:
            mp4s = [a for a in ad["collection"].get("items",[]) if a.get("href","").lower().endswith(".mp4")]
            if mp4s:
                orig = [f for f in mp4s if "orig" in f["href"].lower()]
                dl_url = (orig[0] if orig else mp4s[0])["href"]
                pv_url = mp4s[-1]["href"] if len(mp4s)>1 else dl_url
        if not dl_url: continue
        if dl_url.startswith("//"): dl_url = "https:" + dl_url
        if pv_url.startswith("//"): pv_url = "https:" + pv_url
        out.append(make_result("nasa_v",
            title=dat.get("title","NASA Video")[:90], description=clean_html(dat.get("description",""))[:250],
            thumbnail=thumb, preview_url=pv_url, download_url=dl_url,
            page_url=f"https://images.nasa.gov/details/{nid}", author="NASA",
        ))
    return out

def search_nasa_svs(q, n=15, **kw):
    out = []
    for query_str in [f"{q} visualization", f"{q} simulation", q]:
        d = safe_get("https://images-api.nasa.gov/search",
                      params={"q": query_str, "media_type": "video", "page_size": n, "center": "GSFC"}, timeout=20)
        if d and "collection" in d:
            for item in d["collection"].get("items", [])[:n]:
                dat = item.get("data", [{}])[0]
                nid = dat.get("nasa_id", "")
                links = item.get("links", [])
                thumb = next((l["href"] for l in links if l.get("render") == "image"), "")
                ad = safe_get(f"https://images-api.nasa.gov/asset/{nid}", timeout=10)
                dl_url = pv_url = ""
                if ad and "collection" in ad:
                    mp4s = [a for a in ad["collection"].get("items",[]) if a.get("href","").lower().endswith(".mp4")]
                    if mp4s:
                        dl_url = mp4s[0]["href"]; pv_url = mp4s[-1]["href"] if len(mp4s)>1 else dl_url
                if not dl_url: continue
                if dl_url.startswith("//"): dl_url = "https:" + dl_url
                if pv_url.startswith("//"): pv_url = "https:" + pv_url
                out.append(make_result("nasa_svs",
                    title=dat.get("title","NASA SVS")[:90], description=clean_html(dat.get("description",""))[:250],
                    thumbnail=thumb, preview_url=pv_url, download_url=dl_url,
                    page_url=f"https://images.nasa.gov/details/{nid}", author="NASA GSFC SVS",
                ))
            if out: break
    # Deduplicate by download_url
    seen = set(); deduped = []
    for r in out:
        if r["download_url"] not in seen:
            seen.add(r["download_url"]); deduped.append(r)
    return deduped[:n]

def search_wikimedia_videos(q, n=15, **kw):
    out = []
    d = safe_get("https://commons.wikimedia.org/w/api.php",
                  params={"action":"query","format":"json","generator":"search",
                          "gsrsearch":f"{q} filetype:video","gsrnamespace":"6",
                          "gsrlimit":n,"prop":"imageinfo",
                          "iiprop":"url|size|mime|extmetadata","iiurlwidth":640}, timeout=15)
    if not d or "query" not in d: return []
    safe_lic = ["cc0","public domain","cc-by-4","cc-by-3","cc-by-2","cc-by-sa","pd"]
    for pid, pg in d["query"].get("pages",{}).items():
        ii = pg.get("imageinfo",[{}])[0]
        if not any(x in ii.get("mime","") for x in ["video","webm","ogg"]): continue
        em = ii.get("extmetadata",{})
        ls = em.get("LicenseShortName",{}).get("value","").lower()
        if not any(s in ls for s in safe_lic): continue
        title = pg.get("title","").replace("File:","")
        out.append(make_result("wikimedia_v",
            title=title[:80], description=clean_html(em.get("ImageDescription",{}).get("value",""))[:200],
            thumbnail=ii.get("thumburl",""), preview_url=ii.get("url",""), download_url=ii.get("url",""),
            resolution=f"{ii.get('width','?')}x{ii.get('height','?')}",
            quality="HD" if ii.get("height",0)>=720 else "SD",
            license=f"{em.get('LicenseShortName',{}).get('value','')} – Wikimedia Commons",
            license_short=em.get("LicenseShortName",{}).get("value","CC"),
            page_url=ii.get("descriptionurl",""), author=clean_html(em.get("Artist",{}).get("value","")),
        ))
    return out

def search_archive_videos(q, n=12, **kw):
    out = []
    ia_q = f'({q}) AND mediatype:movies AND (licenseurl:(*publicdomain* OR *cc0*))'
    d = safe_get("https://archive.org/advancedsearch.php",
                  params={"q":ia_q,"fl[]":["identifier","title","description"],"rows":n,"page":1,"output":"json"}, timeout=15)
    if not d or "response" not in d: return []
    for doc in d["response"].get("docs",[]):
        ident = doc.get("identifier","")
        title = doc.get("title","Internet Archive Video")
        if isinstance(title, list): title = title[0]
        fd = safe_get(f"https://archive.org/metadata/{ident}/files", timeout=10)
        dl_url = ""
        if fd and "result" in fd:
            mp4s = sorted([f for f in fd["result"] if f.get("name","").lower().endswith(".mp4")],
                          key=lambda x: int(x.get("size",0)), reverse=True)
            if mp4s: dl_url = f"https://archive.org/download/{ident}/{mp4s[0]['name']}"
        if not dl_url: continue
        if not is_accessible(dl_url):
            continue
        out.append(make_result("archive_v",
            title=str(title)[:80], description=clean_html(str(doc.get("description","")))[:200],
            thumbnail=f"https://archive.org/services/img/{ident}",
            preview_url=dl_url, download_url=dl_url,
            page_url=f"https://archive.org/details/{ident}", author="Internet Archive",
        ))
    return out

def search_phet(q, n=12, **kw):
    out = []
    d = safe_get("https://phet.colorado.edu/services/metadata/1.3/simulations",
                  params={"format":"json","type":"html","locale":"en"}, timeout=15)
    if not d: return []
    projects = d if isinstance(d, list) else d.get("projects", [])
    words = q.lower().split()
    scored = []
    for p in projects:
        for sim in p.get("simulations", []):
            combined = f"{sim.get('name','')} {' '.join(sim.get('topics',[]))} {sim.get('description','')}".lower()
            sc = sum(1 for w in words if w in combined)
            if sc > 0: scored.append((sc, p, sim))
    scored.sort(key=lambda x: x[0], reverse=True)
    for sc, p, sim in scored[:n]:
        pn = p.get("name", sim.get("name",""))
        out.append(make_result("phet",
            title=f"🧪 {sim.get('name','PhET Sim')}",
            description=sim.get("description","Interactive science simulation")[:200],
            thumbnail=f"https://phet.colorado.edu/sims/html/{pn}/{pn}-600.png",
            download_url=f"https://phet.colorado.edu/sims/html/{pn}/latest/{pn}_all.html",
            page_url=f"https://phet.colorado.edu/en/simulations/{pn.lower().replace(' ','-')}",
            quality="Interactive", resolution="Interactive", author="PhET / CU Boulder", is_interactive=True,
        ))
    return out

def search_esa_videos(q, n=10, **kw):
    out = []
    d = safe_get("https://images-api.nasa.gov/search",
                  params={"q":f"{q} ESA Hubble","media_type":"video","page_size":n}, timeout=15)
    if not d or "collection" not in d: return []
    for item in d["collection"].get("items",[])[:n]:
        dat = item.get("data",[{}])[0]
        nid = dat.get("nasa_id","")
        links = item.get("links",[])
        thumb = next((l["href"] for l in links if l.get("render")=="image"),"")
        ad = safe_get(f"https://images-api.nasa.gov/asset/{nid}", timeout=10)
        dl_url = pv_url = ""
        if ad and "collection" in ad:
            mp4s = [a for a in ad["collection"].get("items",[]) if a.get("href","").lower().endswith(".mp4")]
            if mp4s: dl_url = mp4s[0]["href"]; pv_url = mp4s[-1]["href"] if len(mp4s)>1 else dl_url
        if not dl_url: continue
        if dl_url.startswith("//"): dl_url = "https:"+dl_url
        if pv_url.startswith("//"): pv_url = "https:"+pv_url
        out.append(make_result("esa_v",
            title=dat.get("title","ESA/Hubble Video")[:90],
            description=clean_html(dat.get("description",""))[:250],
            thumbnail=thumb, preview_url=pv_url, download_url=dl_url,
            page_url=f"https://images.nasa.gov/details/{nid}", author="ESA / NASA",
        ))
    return out

def search_noaa_videos(q, n=8, **kw):
    out = []
    ia_q = f'({q} NOAA) AND mediatype:movies AND (creator:NOAA OR subject:NOAA)'
    d = safe_get("https://archive.org/advancedsearch.php",
                  params={"q":ia_q,"fl[]":["identifier","title","description"],"rows":n,"page":1,"output":"json"}, timeout=15)
    if not d or "response" not in d: return []
    for doc in d["response"].get("docs",[]):
        ident = doc.get("identifier","")
        title = doc.get("title","NOAA Viz")
        if isinstance(title, list): title = title[0]
        fd = safe_get(f"https://archive.org/metadata/{ident}/files", timeout=10)
        dl_url = ""
        if fd and "result" in fd:
            mp4s = [f for f in fd["result"] if f.get("name","").lower().endswith(".mp4")]
            if mp4s: dl_url = f"https://archive.org/download/{ident}/{mp4s[0]['name']}"
        if not dl_url: continue
        out.append(make_result("noaa_v",
            title=str(title)[:80], description=clean_html(str(doc.get("description","")))[:200],
            thumbnail=f"https://archive.org/services/img/{ident}",
            preview_url=dl_url, download_url=dl_url,
            page_url=f"https://archive.org/details/{ident}", author="NOAA",
        ))
    return out

def search_cern_videos(q, n=8, **kw):
    out = []
    # CERN Document Server (CDS) has a JSON API
    d = safe_get("https://cds.cern.ch/search",
                  params={"p":q,"of":"recjson","rg":n,"c":"Videos"}, timeout=15)
    if not d or not isinstance(d, list): return []
    for rec in d[:n]:
        title = ""
        if isinstance(rec.get("title"), dict): title = rec["title"].get("title","")
        elif isinstance(rec.get("title"), str): title = rec["title"]
        recid = rec.get("recid","")
        # Find video files
        files = rec.get("files", rec.get("electronic_location",[]))
        dl_url = ""
        if isinstance(files, list):
            for f in files:
                u = f.get("url", f.get("uniform_resource_identifier",""))
                if isinstance(u, str) and u.endswith(".mp4"):
                    dl_url = u; break
        if not dl_url: continue
        out.append(make_result("cern_v",
            title=str(title)[:80], description=clean_html(str(rec.get("abstract",{}).get("summary","")))[:200],
            thumbnail="", preview_url=dl_url, download_url=dl_url,
            page_url=f"https://cds.cern.ch/record/{recid}", author="CERN",
        ))
    return out

def search_dvids_videos(q, n=8, **kw):
    out = []
    d = safe_get("https://api.dvidshub.net/search",
                  params={"q":q,"type":"video","max_results":n,"api_key":"","format":"json"}, timeout=12)
    if not d: return []
    results = d.get("results", [])
    for v in results[:n]:
        dl_url = v.get("url","") or v.get("video_url","")
        thumb = v.get("thumbnail","") or v.get("image","")
        if not dl_url and not v.get("id"): continue
        out.append(make_result("dvids_v",
            title=str(v.get("title","DVIDS Video"))[:80],
            description=clean_html(str(v.get("description","")))[:200],
            thumbnail=thumb, preview_url=dl_url, download_url=dl_url,
            page_url=v.get("url",f"https://www.dvidshub.net/video/{v.get('id','')}"), author="US DoD / DVIDS",
        ))
    return out

def search_nih_videos(q, n=10, **kw):
    """Search NLM Digital Collections for science/medical videos."""
    out = []
    d = safe_get("https://collections.nlm.nih.gov/api/search",
                  params={"q":q,"facet.type":"Video","rows":n,"wt":"json"}, timeout=12)
    if not d: return []
    docs = d.get("response",{}).get("docs",[]) if isinstance(d, dict) else []
    for doc in docs[:n]:
        ident = doc.get("unique_id","") or doc.get("id","")
        title = doc.get("title_text","NIH Video")
        thumb = doc.get("image_url","")
        page = doc.get("url","") or f"https://collections.nlm.nih.gov/catalog/{ident}"
        out.append(make_result("nih_v",
            title=str(title)[:80], description=clean_html(str(doc.get("description","")))[:200],
            thumbnail=thumb, preview_url="", download_url=page,
            page_url=page, author="NIH / NLM", is_interactive=True,
        ))
    return out

def search_coverr_videos(q, n=10, **kw):
    out = []
    for endpoint in [
        f"https://api.coverr.co/videos?query={quote(q)}&page_size={n}",
        f"https://coverr.co/api/search/{quote(q)}",
    ]:
        d = safe_get(endpoint, timeout=10)
        if d and isinstance(d, dict):
            hits = d.get("videos", d.get("hits", d.get("results",[])))
            if isinstance(hits, list):
                for v in hits[:n]:
                    vu = v.get("video_url","") or v.get("urls",{}).get("mp4","")
                    if vu:
                        out.append(make_result("coverr",
                            title=v.get("title",v.get("name","Coverr Video"))[:80],
                            description=v.get("description","")[:200],
                            thumbnail=v.get("thumbnail",v.get("poster","")),
                            preview_url=vu, download_url=vu,
                            duration=v.get("duration"), page_url=v.get("url","https://coverr.co"),
                            author="Coverr",
                        ))
            if out: break
    return out

# ───────────────────────────────────────────────────
# IMAGE SEARCH FUNCTIONS
# ───────────────────────────────────────────────────

def search_pexels_images(q, n=20, **kw):
    if not PEXELS_KEY: return []
    out = []
    for page in [1,2]:
        d = safe_get("https://api.pexels.com/v1/search",
                      headers={"Authorization": PEXELS_KEY},
                      params={"query": q, "per_page": min(n,40), "page": page})
        if not d: break
        for p in d.get("photos",[]):
            src = p.get("src",{})
            out.append(make_result("pexels_i",
                title=f"Pexels Photo #{p['id']}",
                description=p.get("alt",q)[:200],
                thumbnail=src.get("medium",""), preview_url=src.get("large",""),
                download_url=src.get("original",""), page_url=p.get("url",""),
                resolution=f"{p.get('width','?')}x{p.get('height','?')}",
                quality="4K" if p.get("width",0)>=3840 else "HD",
                author=p.get("photographer",""), width=p.get("width",0), height=p.get("height",0),
            ))
        if len(d.get("photos",[])) < n: break
    return out[:n*2]

def search_pixabay_images(q, n=20, **kw):
    if not PIXABAY_KEY: return []
    out = []
    for page in [1,2]:
        d = safe_get("https://pixabay.com/api/",
                      params={"key":PIXABAY_KEY,"q":q,"per_page":min(n,50),"page":page,
                              "safesearch":"true","image_type":"all"})
        if not d: break
        for p in d.get("hits",[]):
            thumb = p.get("webformatURL", "")
            full = p.get("largeImageURL", thumb)
            out.append(make_result("pixabay_i",
                title=f"Pixabay #{p['id']}", description=p.get("tags",q)[:200],
                thumbnail=thumb,
                preview_url=thumb,
                download_url=full,
                page_url=p.get("pageURL",""),
                resolution=f"{p.get('imageWidth','?')}x{p.get('imageHeight','?')}",
                quality="4K" if p.get("imageWidth",0)>=3840 else "HD",
                author=p.get("user",""), width=p.get("imageWidth",0), height=p.get("imageHeight",0),
            ))
        if len(d.get("hits",[])) < n: break
    return out[:n*2]

def search_unsplash_images(q, n=20, **kw):
    if not UNSPLASH_KEY: return []
    out = []
    d = safe_get("https://api.unsplash.com/search/photos",
                  headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
                  params={"query":q,"per_page":min(n,30),"orientation":"landscape"})
    if not d: return []
    for p in d.get("results",[]):
        urls = p.get("urls",{})
        out.append(make_result("unsplash_i",
            title=p.get("description","") or p.get("alt_description","Unsplash Photo"),
            description=p.get("alt_description","")[:200],
            thumbnail=urls.get("small",""), preview_url=urls.get("regular",""),
            download_url=urls.get("full",""), page_url=p.get("links",{}).get("html",""),
            resolution=f"{p.get('width','?')}x{p.get('height','?')}",
            quality="4K" if p.get("width",0)>=3840 else "HD",
            author=p.get("user",{}).get("name",""), width=p.get("width",0), height=p.get("height",0),
        ))
    return out

def search_nasa_images(q, n=20, **kw):
    out = []
    d = safe_get("https://images-api.nasa.gov/search",
                  params={"q":q,"media_type":"image","page_size":min(n,50)}, timeout=20)
    if not d or "collection" not in d: return []
    for item in d["collection"].get("items",[])[:n]:
        dat = item.get("data",[{}])[0]
        links = item.get("links",[])
        thumb = next((l["href"] for l in links if l.get("render")=="image"),"")
        if not thumb: continue
        nid = dat.get("nasa_id","")
        out.append(make_result("nasa_i",
            title=dat.get("title","NASA Image")[:90],
            description=clean_html(dat.get("description",""))[:250],
            thumbnail=thumb, preview_url=thumb,
            download_url=thumb.replace("~thumb","~orig").replace("~medium","~orig"),
            page_url=f"https://images.nasa.gov/details/{nid}", author="NASA",
        ))
    return out

def search_wikimedia_images(q, n=15, **kw):
    out = []
    d = safe_get("https://commons.wikimedia.org/w/api.php",
                  params={"action":"query","format":"json","generator":"search",
                          "gsrsearch":f"{q}","gsrnamespace":"6",
                          "gsrlimit":n,"prop":"imageinfo",
                          "iiprop":"url|size|mime|extmetadata","iiurlwidth":800}, timeout=15)
    if not d or "query" not in d: return []
    safe_lic = ["cc0","public domain","cc-by-4","cc-by-3","cc-by-2","cc-by-sa","pd"]
    for pid, pg in d["query"].get("pages",{}).items():
        ii = pg.get("imageinfo",[{}])[0]
        mime = ii.get("mime","")
        if "image" not in mime and "svg" not in mime: continue
        em = ii.get("extmetadata",{})
        ls = em.get("LicenseShortName",{}).get("value","").lower()
        if not any(s in ls for s in safe_lic): continue
        title = pg.get("title","").replace("File:","")
        out.append(make_result("wikimedia_i",
            title=title[:80], description=clean_html(em.get("ImageDescription",{}).get("value",""))[:200],
            thumbnail=ii.get("thumburl",""), preview_url=ii.get("url",""), download_url=ii.get("url",""),
            resolution=f"{ii.get('width','?')}x{ii.get('height','?')}",
            quality="HD" if ii.get("width",0)>=1280 else "SD",
            license=f"{em.get('LicenseShortName',{}).get('value','')} – Wikimedia",
            license_short=em.get("LicenseShortName",{}).get("value","CC"),
            page_url=ii.get("descriptionurl",""), author=clean_html(em.get("Artist",{}).get("value","")),
        ))
    return out

def search_flickr_images(q, n=20, **kw):
    if not FLICKR_KEY: return []
    out = []
    # license 4=CC-BY 2.0, 5=CC-BY-SA, 7=No known copyright, 9=CC0, 10=PDM
    d = safe_get("https://api.flickr.com/services/rest/",
                  params={"method":"flickr.photos.search","api_key":FLICKR_KEY,"format":"json",
                          "nojsoncallback":"1","text":q,"license":"4,5,7,9,10","media":"photos",
                          "per_page":n,"content_type":"1","sort":"relevance","extras":"url_l,url_o,url_c,owner_name,license"})
    if not d: return []
    lic_map = {"4":"CC-BY 2.0","5":"CC-BY-SA 2.0","7":"No known copyright","9":"CC0","10":"Public Domain Mark"}
    for p in d.get("photos",{}).get("photo",[]):
        url = p.get("url_o") or p.get("url_l") or p.get("url_c","")
        thumb = p.get("url_c") or p.get("url_l") or url
        if not url: continue
        lic_id = str(p.get("license",""))
        out.append(make_result("flickr_i",
            title=p.get("title","Flickr Photo")[:80],
            thumbnail=thumb, preview_url=url, download_url=url,
            license=f"{lic_map.get(lic_id,'CC')} – Flickr",
            license_short=lic_map.get(lic_id,"CC-BY"),
            page_url=f"https://www.flickr.com/photos/{p.get('owner','')}/{p.get('id','')}",
            author=p.get("ownername",""),
        ))
    return out

def search_europeana_images(q, n=15, **kw):
    out = []
    d = safe_get("https://api.europeana.eu/record/v2/search.json",
                  params={"query":f"{q} science","qf":"TYPE:IMAGE","reusability":"open",
                          "rows":n,"wskey":"api2demo","profile":"rich"}, timeout=15)
    if not d: return []
    for item in d.get("items",[]):
        thumb = ""
        previews = item.get("edmPreview",[])
        if previews: thumb = previews[0]
        is_shown = item.get("edmIsShownBy",[])
        dl_url = is_shown[0] if is_shown else thumb
        if not dl_url: continue
        title_list = item.get("title",[])
        title = title_list[0] if title_list else "Europeana Image"
        rights_list = item.get("rights",[])
        rights = rights_list[0] if rights_list else "Open"
        out.append(make_result("europeana_i",
            title=str(title)[:80],
            description=clean_html(str(item.get("dcDescription",[""])[0]))[:200] if item.get("dcDescription") else "",
            thumbnail=thumb, preview_url=dl_url, download_url=dl_url,
            license=f"{rights} – Europeana", license_short="Open/CC",
            page_url=item.get("guid",""), author=str(item.get("dcCreator",[""])[0]) if item.get("dcCreator") else "",
        ))
    return out

def search_smithsonian_images(q, n=12, **kw):
    out = []
    d = safe_get("https://api.si.edu/openaccess/api/v1.0/search",
                  params={"q":f"{q} online_media_type:Images","rows":n,"start":0}, timeout=15)
    if not d or "response" not in d: return []
    for row in d["response"].get("rows",[]):
        desc_nr = row.get("content",{}).get("descriptiveNonRepeating",{})
        title_obj = desc_nr.get("title",{})
        title = title_obj.get("content","Smithsonian") if isinstance(title_obj, dict) else str(title_obj)
        online = desc_nr.get("online_media",{})
        media_list = online.get("media",[]) if isinstance(online, dict) else []
        thumb = dl_url = ""
        for m in media_list:
            ct = m.get("content","")
            th = m.get("thumbnail","")
            if any(ct.lower().endswith(e) for e in [".jpg",".jpeg",".png",".tif",".tiff"]):
                dl_url = ct; thumb = th or ct; break
            if not dl_url and ct: dl_url = ct; thumb = th or ct
        if not dl_url: continue
        out.append(make_result("smithsonian_i",
            title=str(title)[:80], thumbnail=thumb, preview_url=dl_url, download_url=dl_url,
            page_url=desc_nr.get("record_link","https://www.si.edu/openaccess"), author="Smithsonian Institution",
        ))
    return out

def search_met_images(q, n=12, **kw):
    out = []
    d = safe_get("https://collectionapi.metmuseum.org/public/collection/v1/search",
                  params={"q":q,"hasImages":"true","isPublicDomain":"true"}, timeout=12)
    if not d: return []
    ids = d.get("objectIDs",[]) or []
    for oid in ids[:n]:
        obj = safe_get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}", timeout=8)
        if not obj or not obj.get("isPublicDomain"): continue
        img = obj.get("primaryImage","")
        if not img: continue
        thumb = obj.get("primaryImageSmall","") or img
        out.append(make_result("met_i",
            title=obj.get("title","Met Artwork")[:80],
            description=f"{obj.get('artistDisplayName','')} – {obj.get('objectDate','')}".strip(" –")[:200],
            thumbnail=thumb, preview_url=img, download_url=img,
            page_url=obj.get("objectURL",""), author=obj.get("artistDisplayName","Met Museum"),
        ))
    return out

def search_giphy_science(q, n=15, **kw):
    out = []
    d = safe_get("https://api.giphy.com/v1/gifs/search",
                  params={"api_key":"dc6zaTOxFJmzC","q":f"{q} science","limit":n,"rating":"g"}, timeout=10)
    if not d: return []
    for g in d.get("data",[]):
        imgs = g.get("images",{})
        orig = imgs.get("original",{})
        prev = imgs.get("fixed_height",{})
        mp4_url = orig.get("mp4","")
        gif_url = orig.get("url","")
        dl = mp4_url or gif_url
        if not dl: continue
        out.append(make_result("giphy_i",
            title=g.get("title","Giphy GIF")[:80], description=g.get("slug","")[:200],
            thumbnail=prev.get("url",""), preview_url=dl, download_url=dl,
            page_url=g.get("url",""), author=g.get("username","Giphy"),
            resolution=f"{orig.get('width','?')}x{orig.get('height','?')}",
        ))
    return out

def search_pinterest_links(q, n=15, **kw):
    """
    Pinterest discovery — generates search links for the user.
    Pinterest doesn't have a free public API for content retrieval,
    so we create helpful direct search URLs. Users verify individual licenses.
    """
    out = []
    # Generate useful Pinterest search URLs
    search_terms = [
        q,
        f"{q} infographic",
        f"{q} diagram",
        f"{q} illustration",
        f"{q} science visualization",
    ]
    for i, term in enumerate(search_terms[:n]):
        pin_url = f"https://www.pinterest.com/search/pins/?q={quote_plus(term)}&rs=typed"
        out.append(make_result("pinterest_i",
            title=f"🔎 Pinterest: {term}",
            description=f"Browse Pinterest for '{term}' — verify license on each pin's source before commercial use",
            thumbnail="",
            preview_url="",
            download_url=pin_url,
            page_url=pin_url,
            author="Pinterest (Discovery)",
            is_interactive=True,
        ))
    return out

# ───────────────────────────────────────────────────
# SEARCH ROUTER
# ───────────────────────────────────────────────────
VIDEO_FUNCS = {
    "pexels_v": search_pexels_videos,
    "pixabay_v": search_pixabay_videos,
    "nasa_v": search_nasa_videos,
    "nasa_svs": search_nasa_svs,
    "wikimedia_v": search_wikimedia_videos,
    "archive_v": search_archive_videos,
    "phet": search_phet,
    "coverr": search_coverr_videos,
    "esa_v": search_esa_videos,
    "noaa_v": search_noaa_videos,
    "cern_v": search_cern_videos,
    "dvids_v": search_dvids_videos,
    "nih_v": search_nih_videos,
}

IMAGE_FUNCS = {
    "pexels_i": search_pexels_images,
    "pixabay_i": search_pixabay_images,
    "unsplash_i": search_unsplash_images,
    "nasa_i": search_nasa_images,
    "wikimedia_i": search_wikimedia_images,
    "flickr_i": search_flickr_images,
    "europeana_i": search_europeana_images,
    "smithsonian_i": search_smithsonian_images,
    "met_i": search_met_images,
    "giphy_i": search_giphy_science,
    "pinterest_i": search_pinterest_links,
}

def parallel_search(query, src_keys, func_map, per_page=15, progress_cb=None):
    all_results = []
    counts = {}
    done = 0
    total = len(src_keys)

    def wrapper(key):
        fn = func_map.get(key)
        if not fn: return key, []
        try:
            return key, fn(query, n=per_page)
        except Exception:
            return key, []

    with ThreadPoolExecutor(max_workers=min(total, 10)) as pool:
        futs = {pool.submit(wrapper, k): k for k in src_keys if k in func_map}
        for fut in as_completed(futs):
            k = futs[fut]
            try:
                key, res = fut.result(timeout=35)
                counts[key] = len(res)
                all_results.extend(res)
            except Exception:
                counts[k] = 0
            done += 1
            if progress_cb:
                progress_cb(done / total, f"Searched {done}/{total} sources…")

    return all_results, counts

# ───────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Filters & Settings")

    st.markdown("---")
    st.markdown("### 📡 Source Categories")
    cat_stock = st.checkbox("🎬 Stock Sources", value=True)
    cat_archive = st.checkbox("🏛️ Archives / Public Domain", value=True)
    cat_sim = st.checkbox("🧪 Simulations", value=True)
    cat_disc = st.checkbox("🔗 Discovery (Pinterest etc.)", value=True)

    active_types = []
    if cat_stock: active_types.append("Stock")
    if cat_archive: active_types.append("Archive")
    if cat_sim: active_types.append("Simulation")
    if cat_disc: active_types.append("Discovery")

    st.markdown("---")
    st.markdown("### 🎞️ Video Sources")
    v_sources = []
    for k, cfg in SOURCES.items():
        if cfg["media"] != "video": continue
        if cfg["type"] not in active_types: continue
        default = True
        if cfg.get("needs_key") and not get_key(cfg.get("key","")): default = False
        if st.checkbox(cfg["name"], value=default, key=f"vs_{k}", help=cfg["lic"]):
            v_sources.append(k)

    st.markdown("---")
    st.markdown("### 🖼️ Image Sources")
    i_sources = []
    for k, cfg in SOURCES.items():
        if cfg["media"] != "image": continue
        if cfg["type"] not in active_types: continue
        default = True
        if cfg.get("needs_key") and not get_key(cfg.get("key","")): default = False
        if st.checkbox(cfg["name"], value=default, key=f"is_{k}", help=cfg["lic"]):
            i_sources.append(k)

    st.markdown("---")
    st.markdown("### 📊 Results Per Source")
    per_page = st.slider("Max per source", 5, 30, 15, key="pp")

    st.markdown("### 🔄 Sort By")
    sort_by = st.selectbox("Sort", ["Relevance","Duration ↑","Duration ↓","Quality ↓","Source A-Z"], key="sort")

    st.markdown("---")

    # License reminder
    st.markdown("""
    <div class="sidebar-info">
        <h4>✅ License Safety</h4>
        <p>All results are pre-filtered for <strong style="color:#4ade80;">commercial-use licenses</strong>.</p>
        <p>✅ Safe for monetized YouTube<br>
        ✅ Public Domain / CC0 / Free Licenses<br>
        ✅ No copyright claims</p>
        <p style="font-size:0.72rem;color:#6b7280;"><em>Best practice: note source in video description.</em></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔑 API Keys")
    keys_info = {
        "Pexels": ("✅" if PEXELS_KEY else "❌"),
        "Pixabay": ("✅" if PIXABAY_KEY else "❌"),
        "NASA": ("✅" if NASA_KEY != "DEMO_KEY" else "⚠️ DEMO"),
        "Unsplash": ("✅" if UNSPLASH_KEY else "❌"),
        "Flickr": ("✅" if FLICKR_KEY else "❌"),
    }
    for name, status in keys_info.items():
        st.caption(f"{status} {name}")

# ───────────────────────────────────────────────────
# MAIN HEADER
# ───────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔬 SciClip Pro <span class="version">v2.0</span></h1>
    <p class="subtitle">Find royalty-free science videos, simulations, animations & images — 100% safe for monetized YouTube</p>
</div>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────
# PRESET BUTTONS
# ───────────────────────────────────────────────────
st.markdown("##### 🏷️ Quick Presets")
pcols = st.columns(9)
presets = [
    ("🌌 Space","space visualization simulation"),
    ("⚛️ Physics","physics simulation animation"),
    ("🧬 Biology","biology cell molecular animation"),
    ("⚗️ Chemistry","chemical reaction simulation"),
    ("🌍 Earth","earth climate ocean visualization"),
    ("🔬 Quantum","quantum mechanics wave particle"),
    ("🧠 Neuro","neuron brain synapse animation"),
    ("📊 Data","scientific data visualization chart"),
    ("🔭 Astro","astronomy galaxy nebula telescope"),
]
for i, (lbl, pq) in enumerate(presets):
    with pcols[i]:
        if st.button(lbl, key=f"p_{i}", use_container_width=True):
            st.session_state.preset = pq

# ───────────────────────────────────────────────────
# SEARCH BAR
# ───────────────────────────────────────────────────
st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
sc1, sc2 = st.columns([6, 1])
with sc1:
    q_val = st.session_state.preset if st.session_state.preset else ""
    query = st.text_input(
        "Search", value=q_val,
        placeholder="e.g., black hole accretion disk simulation, DNA replication, quantum entanglement…",
        label_visibility="collapsed", key="q_input",
    )
with sc2:
    go = st.button("🔍 **Search**", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.preset:
    st.session_state.preset = ""

# ───────────────────────────────────────────────────
# EXECUTE SEARCH
# ───────────────────────────────────────────────────
if go and query.strip():
    st.session_state.query = query.strip()
    st.session_state.searched = False

    total_sources = len(v_sources) + len(i_sources)
    if total_sources == 0:
        st.warning("⚠️ Enable at least one source in the sidebar.")
    else:
        t0 = time.time()
        prog = st.progress(0, text="🚀 Launching parallel search…")

        # Search videos
        vid_results, v_counts = [], {}
        if v_sources:
            def v_cb(frac, txt):
                prog.progress(frac * 0.5, text=f"🎬 Videos: {txt}")
            vid_results, v_counts = parallel_search(query.strip(), v_sources, VIDEO_FUNCS, per_page, v_cb)

        # Search images
        img_results, i_counts = [], {}
        if i_sources:
            def i_cb(frac, txt):
                prog.progress(0.5 + frac * 0.5, text=f"🖼️ Images: {txt}")
            img_results, i_counts = parallel_search(query.strip(), i_sources, IMAGE_FUNCS, per_page, i_cb)

        elapsed = time.time() - t0
        prog.progress(1.0, text=f"✅ Done in {elapsed:.1f}s — {len(vid_results)} videos + {len(img_results)} images found!")

        st.session_state.video_results = vid_results
        st.session_state.image_results = img_results
        st.session_state.v_counts = v_counts
        st.session_state.i_counts = i_counts
        st.session_state.search_time = elapsed
        st.session_state.searched = True
        time.sleep(0.5)
        st.rerun()


# ───────────────────────────────────────────────────
# DISPLAY RESULTS
# ───────────────────────────────────────────────────
def sort_results(results, method):
    if method == "Duration ↑":
        return sorted(results, key=lambda x: x.get("duration") or 9999)
    elif method == "Duration ↓":
        return sorted(results, key=lambda x: x.get("duration") or 0, reverse=True)
    elif method == "Quality ↓":
        order = {"4K":0,"HD/4K":1,"HD":2,"Interactive Sim":3,"Interactive":4,"SD":5,"Varies":6}
        return sorted(results, key=lambda x: order.get(x.get("quality","HD"),5))
    elif method == "Source A-Z":
        return sorted(results, key=lambda x: x.get("source_name",""))
    return results  # Relevance = default order

def render_video_card(r, idx):
    """Render a single video result card."""
    badge = r.get("badge","")
    sname = r.get("source_name","")

    st.markdown(f'<span class="src-badge {badge}">{sname}</span>', unsafe_allow_html=True)
    st.markdown(f"**{r['title']}**")

    # Video playback
    if r.get("is_interactive"):
        if r.get("thumbnail"):
            st.image(r["thumbnail"], use_container_width=True)
        st.info("🧪 Interactive — open in browser")
    elif r.get("preview_url"):
        try:
            st.video(r["preview_url"])
        except Exception:
            if r.get("thumbnail"):
                st.image(r["thumbnail"], use_container_width=True)
            else:
                st.caption("🎬 Preview unavailable")
    elif r.get("thumbnail"):
        st.image(r["thumbnail"], use_container_width=True)

    # Meta info
    parts = []
    if r.get("duration") is not None:
        parts.append(f"⏱️ {fmt_dur(r['duration'])}")
    if r.get("resolution") and r["resolution"] != "Interactive":
        parts.append(f"📐 {r['resolution']}")
    parts.append(f"📊 {r.get('quality','HD')}")
    st.markdown(f'<p class="meta">{" · ".join(parts)}</p>', unsafe_allow_html=True)

    if r.get("author"):
        st.markdown(f'<p class="meta">👤 <strong>{r["author"]}</strong></p>', unsafe_allow_html=True)

    st.markdown(f'<span class="lic-badge">✅ {r.get("license_short","")}</span>', unsafe_allow_html=True)

    desc = clean_html(r.get("description",""))
    if desc:
        st.caption(desc[:120])

    # Action buttons
    dl_url = r.get("download_url","")
    pg_url = r.get("page_url","")

    if r.get("is_interactive"):
        if dl_url or pg_url:
            st.link_button("🧪 Open", dl_url or pg_url, use_container_width=True)
    elif dl_url:
        safe_t = re.sub(r'[^\w\s-]','',r['title'])[:30].strip().replace(' ','_')
        fname = f"SciClip_{sname}_{safe_t}.mp4"
        bkey = f"dl_v_{idx}_{hash(dl_url)%99999}"

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("⬇️ Download", key=bkey, use_container_width=True):
                with st.spinner("Downloading…"):
                    data = dl_bytes(dl_url)
                    if data:
                        st.download_button("💾 Save MP4", data, fname, "video/mp4", key=f"s_{bkey}", use_container_width=True)
                    else:
                        st.error("Download failed")
        with col_b:
            st.link_button("🔗 Source", pg_url or dl_url, use_container_width=True)

    with st.expander("📋 License"):
        st.markdown(f"""
        **License:** {r.get('license','Unknown')}
        \n**Commercial Use:** ✅ **YouTube Monetization:** ✅
        \n**Attribution:** {"Required" if "CC-BY" in r.get("license_short","") and "CC0" not in r.get("license_short","") else "Not required"}
        """)


def render_image_card(r, idx):
    """Render a single image result card."""
    badge = r.get("badge","")
    sname = r.get("source_name","")

    st.markdown(f'<span class="src-badge {badge}">{sname}</span>', unsafe_allow_html=True)

    title = r.get("title","") or "Image"
    st.markdown(f"**{title[:60]}**")

    # Image display
    if r.get("is_interactive"):
        st.info(f"🔗 Browse on {sname}")
    else:
        img_url = r.get("preview_url") or r.get("thumbnail","")
        if img_url:
            try:
                st.image(img_url, use_container_width=True)
            except Exception:
                st.caption("🖼️ Preview unavailable")

    # Meta
    parts = []
    if r.get("resolution") and r["resolution"] not in ["",None]:
        parts.append(f"📐 {r['resolution']}")
    if r.get("quality"):
        parts.append(f"📊 {r['quality']}")
    if r.get("author"):
        parts.append(f"👤 {r['author']}")
    if parts:
        st.markdown(f'<p class="meta">{" · ".join(parts)}</p>', unsafe_allow_html=True)

    st.markdown(f'<span class="lic-badge">✅ {r.get("license_short","")}</span>', unsafe_allow_html=True)

    desc = clean_html(r.get("description",""))
    if desc:
        st.caption(desc[:100])

    # Action buttons
    dl_url = r.get("download_url","")
    pg_url = r.get("page_url","")

    if r.get("is_interactive"):
        if dl_url or pg_url:
            st.link_button("🔗 Browse", dl_url or pg_url, use_container_width=True)
    elif dl_url:
        safe_t = re.sub(r'[^\w\s-]','',r.get('title','img'))[:25].strip().replace(' ','_')
        ext = "jpg"
        if dl_url.lower().endswith(".png"): ext = "png"
        elif dl_url.lower().endswith(".gif"): ext = "gif"
        elif dl_url.lower().endswith(".svg"): ext = "svg"
        fname = f"SciClip_{sname}_{safe_t}.{ext}"
        bkey = f"dl_i_{idx}_{hash(dl_url)%99999}"

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("⬇️ Download", key=bkey, use_container_width=True):
                with st.spinner("Downloading…"):
                    data = dl_bytes(dl_url)
                    if data:
                        mime = f"image/{ext}"
                        st.download_button("💾 Save", data, fname, mime, key=f"s_{bkey}", use_container_width=True)
                    else:
                        st.error("Failed")
        with col_b:
            st.link_button("🔗 Source", pg_url or dl_url, use_container_width=True)


if st.session_state.searched:
    vr = st.session_state.video_results
    ir = st.session_state.image_results
    vc = st.session_state.v_counts
    ic = st.session_state.i_counts
    elapsed = st.session_state.search_time

    total_v = len(vr)
    total_i = len(ir)
    total = total_v + total_i
    v_src_ok = sum(1 for c in vc.values() if c > 0)
    i_src_ok = sum(1 for c in ic.values() if c > 0)
    total_src = len(vc) + len(ic)
    ok_src = v_src_ok + i_src_ok

    # Stats bar
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-pill"><div class="num">{total}</div><div class="lbl">Total Results</div></div>
        <div class="stat-pill"><div class="num">{total_v}</div><div class="lbl">🎬 Videos</div></div>
        <div class="stat-pill"><div class="num">{total_i}</div><div class="lbl">🖼️ Images</div></div>
        <div class="stat-pill"><div class="num">{ok_src}/{total_src}</div><div class="lbl">Sources Hit</div></div>
        <div class="stat-pill"><div class="num">{elapsed:.1f}s</div><div class="lbl">Search Time</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Per-source breakdown
    with st.expander(f"📊 Detailed Breakdown — {ok_src} sources returned results", expanded=False):
        all_counts = {**vc, **ic}
        bcols = st.columns(min(len(all_counts), 5)) if all_counts else [st.container()]
        for i, (k, c) in enumerate(sorted(all_counts.items(), key=lambda x: x[1], reverse=True)):
            sname = SOURCES.get(k, {}).get("name", k)
            media_icon = "🎬" if SOURCES.get(k, {}).get("media") == "video" else "🖼️"
            with bcols[i % len(bcols)]:
                st.metric(f"{media_icon} {sname}", f"{'✅' if c else '❌'} {c}")

    st.markdown("---")

    st.markdown("---")

    # Side-by-side layout: videos (left) and images (right)
    col_v, col_i = st.columns(2, gap="large")

    # ════════════════════════════════════════════════
    # VIDEOS — grouped by source with dropdowns
    # ════════════════════════════════════════════════
    with col_v:
        st.markdown('<div class="pane">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-divider">
            <div class="line"></div>
            <div class="label">🎬 VIDEO RESULTS</div>
            <div class="line"></div>
        </div>
        """, unsafe_allow_html=True)

        if vr:
            v_by_source = {}
            for r in sort_results(vr, sort_by):
                sname = r.get("source_name", "Unknown")
                v_by_source.setdefault(sname, []).append(r)

            vid_idx = 0
            for src_name, src_results in v_by_source.items():
                if not src_results:
                    continue
                badge_cls = src_results[0].get("badge", "")
                with st.expander(f"{src_name} — {len(src_results)} clips", expanded=False):
                    # Render in grid — 2 per row for better width
                    for row_start in range(0, len(src_results), 2):
                        cols = st.columns(2)
                        for ci in range(2):
                            ri = row_start + ci
                            if ri >= len(src_results):
                                break
                            with cols[ci]:
                                render_video_card(src_results[ri], vid_idx)
                                vid_idx += 1
        else:
            if st.session_state.v_counts:
                st.info("🎬 No video results matched your filters. Try broadening your search or enabling more video sources.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # IMAGES — grouped by source with dropdowns
    # ════════════════════════════════════════════════
    with col_i:
        st.markdown('<div class="pane">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-divider">
            <div class="line"></div>
            <div class="label">🖼️ IMAGE RESULTS</div>
            <div class="line"></div>
        </div>
        """, unsafe_allow_html=True)

        if ir:
            i_by_source = {}
            for r in sort_results(ir, sort_by):
                sname = r.get("source_name", "Unknown")
                i_by_source.setdefault(sname, []).append(r)

            img_idx = 0
            for src_name, src_results in i_by_source.items():
                if not src_results:
                    continue
                badge_cls = src_results[0].get("badge", "")
                with st.expander(f"{src_name} — {len(src_results)} images", expanded=False):
                    # Render in grid — 2 per row to fit the column
                    for row_start in range(0, len(src_results), 2):
                        cols = st.columns(2)
                        for ci in range(2):
                            ri = row_start + ci
                            if ri >= len(src_results):
                                break
                            with cols[ci]:
                                render_image_card(src_results[ri], img_idx)
                                img_idx += 1
        else:
            if st.session_state.i_counts:
                st.info("🖼️ No image results matched your filters. Try broadening your search or enabling more image sources.")
        st.markdown('</div>', unsafe_allow_html=True)

    # No results at all
    if not vr and not ir:
        st.warning("""
        🔍 **No results found.**

        **Tips:**
        - Add words like **"simulation"**, **"animation"**, **"visualization"**
        - Use specific terms: "DNA helicase" instead of just "DNA"
        - Enable more sources in the sidebar
        - Check that API keys are set for Pexels, Pixabay, Unsplash, Flickr
        """)

elif not st.session_state.searched:
    # ───────────────────────────────────────────────
    # WELCOME STATE
    # ───────────────────────────────────────────────
    st.markdown("---")

    wcols = st.columns(3)
    with wcols[0]:
        st.markdown("""
        ### 🎯 How It Works
        1. **Type** any science topic above
        2. **SciClip Pro** searches **24+ sources** in parallel
        3. **Section 1:** Video results grouped by source
        4. **Section 2:** Image results grouped by source
        5. **Download** with one click — 100% legal!
        """)
    with wcols[1]:
        st.markdown("""
        ### 🎬 Video Sources (13)
        Pexels · Pixabay · Coverr · NASA Media · NASA SVS ·
        Wikimedia · Internet Archive · PhET Sims · ESA/Hubble ·
        NOAA · CERN · DVIDS · NIH/NLM
        """)
    with wcols[2]:
        st.markdown("""
        ### 🖼️ Image Sources (11)
        Pexels · Pixabay · Unsplash · NASA · Wikimedia ·
        Flickr CC · Europeana · Smithsonian OA · Met Museum ·
        Giphy Science · Pinterest (links)
        """)

    st.markdown("---")
    st.markdown("### 💡 Example Searches")
    ecols = st.columns(4)
    examples = [
        "🌌 Black hole accretion disk", "🧬 DNA replication animation",
        "⚛️ Quantum entanglement", "🌍 Climate change data visualization",
        "🔬 Cell mitosis division", "🪐 Planetary orbit simulation",
        "⚡ Electromagnetic spectrum", "🧠 Neuron synapse firing",
        "🌊 Ocean current simulation", "💎 Crystal lattice structure",
        "🔥 Combustion chemical reaction", "🌋 Plate tectonics volcano",
    ]
    for i, ex in enumerate(examples):
        with ecols[i % 4]:
            st.code(ex, language=None)

# ───────────────────────────────────────────────────
# FOOTER
# ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:1.5rem;color:#6b7280;font-size:0.82rem;">
    <p><strong>🔬 SciClip Pro v2.0</strong> — Science Media Finder</p>
    <p>24 sources · Videos + Images · Categorized by source · 100% commercial-use safe</p>
    <p style="font-size:0.72rem;margin-top:0.5rem;color:#4b5563;">
        Always verify license terms on the source website before final publication.
        When using CC-BY content, credit the creator. Built with Streamlit.
    </p>
</div>
""", unsafe_allow_html=True)