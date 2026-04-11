"""
F1 Driver Lap Time Visualizer
Uses the OpenF1 API (https://openf1.org) — data available from 2023 onwards.

Requirements:
    pip install requests matplotlib pandas
"""

import time
import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.widgets import Button, RadioButtons


# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL   = "https://api.openf1.org/v1"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "f1_sessions_cache.json")

TEAM_COLOURS = {
    "red bull":     "#3671C6",
    "mercedes":     "#27F4D2",
    "ferrari":      "#E8002D",
    "mclaren":      "#FF8000",
    "aston":        "#229971",
    "alpine":       "#FF87BC",
    "williams":     "#64C4FF",
    "haas":         "#B6BABD",
    "sauber":       "#52E252",
    "audi":         "#52E252",
    "cadillac":     "#CC0000",
    "rb ":          "#6692FF",
    "racing bulls": "#6692FF",
}

FALLBACK_COLOURS = [
    "#e6194b","#3cb44b","#ffe119","#4363d8","#f58231",
    "#911eb4","#42d4f4","#f032e6","#bfef45","#fabed4",
    "#469990","#dcbeff","#9A6324","#fffac8","#800000",
    "#aaffc3","#808000","#ffd8b1","#000075","#a9a9a9",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def api_get(endpoint: str, retries: int = 6, **params) -> list:
    url = f"{BASE_URL}/{endpoint}"
    for attempt in range(retries):
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 429:
            wait = 2 + 2 ** attempt  # 3, 4, 6, 10, 18, 34s
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"API still rate-limiting after {retries} retries: {endpoint}")

def format_lap_time(seconds) -> str:
    if seconds is None:
        return "N/A"
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return "N/A"
    if seconds != seconds:
        return "N/A"
    m = int(seconds // 60)
    s = seconds - m * 60
    return f"{m}:{s:06.3f}"


def team_colour(team_name: str, fallback_idx: int) -> str:
    name_lower = (team_name or "").lower()
    for fragment, colour in TEAM_COLOURS.items():
        if fragment in name_lower:
            return colour
    return FALLBACK_COLOURS[fallback_idx % len(FALLBACK_COLOURS)]


def fetch_meeting_name(meeting_key) -> str:
    if not meeting_key:
        return None
    try:
        data = api_get("meetings", meeting_key=meeting_key)
        if data:
            return data[0].get("meeting_official_name") or data[0].get("meeting_name")
    except Exception:
        pass
    return None


def session_label(session: dict) -> str:
    name = session.get("meeting_name")
    if not name:
        name = fetch_meeting_name(session.get("meeting_key"))
    if not name:
        name = f"Session {session['session_key']}"
    year = (session.get("date_start") or "")[:4]
    label = name.strip()
    if year and year not in label:
        label = f"{label} {year}"
    session_type = session.get("session_name") or ""
    if session_type and session_type.lower() not in label.lower():
        label = f"{label} ({session_type})"
    return label


# ── Session discovery ─────────────────────────────────────────────────────────

def probe_session(session: dict) -> tuple:
    """Return (session, has_data), retrying on 429 rate-limit responses."""
    params = {"session_key": session["session_key"], "lap_number": 1}
    for attempt in range(4):
        try:
            r = requests.get(f"{BASE_URL}/laps", params=params, timeout=10)
            if r.status_code == 200:
                return session, bool(r.json())
            elif r.status_code == 429:
                wait = 2 ** attempt * 2  # 2, 4, 8, 16s
                time.sleep(wait)
                continue
            else:
                return session, False
        except Exception:
            return session, False
    return session, False


def load_all_race_sessions(force_refresh: bool = False) -> list:
    from datetime import datetime, timezone

    if not force_refresh and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cached = json.load(f)
        cached_sessions = cached.get("sessions", [])
        if cached_sessions:
            # Check for any new races since the last cache
            from datetime import datetime, timezone
            cached_keys = {s["session_key"] for s in cached_sessions}
            now_check   = datetime.now(timezone.utc)
            new_sessions = []
            now_iso = now_check.isoformat()
            for year in range(2025, now_check.year + 1):
                year_sessions = []
                for stype in ("Race", "Sprint"):
                    try:
                        year_sessions.extend(api_get("sessions", session_type=stype, year=year))
                    except Exception:
                        pass
                past      = [s for s in year_sessions if s.get("date_start") and s["date_start"] <= now_iso]
                unchecked = [s for s in past if s["session_key"] not in cached_keys]
                if unchecked:
                    print(f"  Checking {len(unchecked)} new sessions...")
                    with ThreadPoolExecutor(max_workers=4) as pool:
                        futures = {pool.submit(probe_session, s): s for s in unchecked}
                        for future in as_completed(futures):
                            session, has_data = future.result()
                            if has_data:
                                new_sessions.append(session)

            if new_sessions:
                print(f"  Found {len(new_sessions)} new race(s), adding to cache.")
                all_sessions = new_sessions + cached_sessions
                # Re-sort newest first by date
                all_sessions.sort(key=lambda s: s.get("date_start", ""), reverse=True)
                with open(CACHE_FILE, "w") as f:
                    json.dump({
                        "cached_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "sessions":  all_sessions,
                    }, f, indent=2)
                print(f"  Cache updated ({len(all_sessions)} total races).\n")
                return all_sessions
            else:
                print(f"  Loaded {len(cached_sessions)} races from cache (saved {cached.get('cached_on','?')}, no new races).\n")
                return cached_sessions

    print("Scanning OpenF1 for races (one-time scan)...")
    now          = datetime.now(timezone.utc)
    all_sessions = []

    for year in range(2025, now.year + 1):
        print(f"  Fetching {year} sessions...")
        for stype in ("Race", "Sprint"):
            try:
                all_sessions.extend(api_get("sessions", session_type=stype, year=year))
            except Exception as e:
                print(f"  Warning: {year} {stype} failed: {e}")

    if not all_sessions:
        raise RuntimeError("No race sessions found.")

    # Filter to past sessions only
    now_iso       = now.isoformat()
    past_sessions = [
        s for s in all_sessions
        if s.get("date_start") and s["date_start"] <= now_iso
    ]
    print(f"  Probing all {len(past_sessions)} past sessions in parallel (no early stop)...")

    # Fire all probes concurrently
    results = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(probe_session, s): s for s in past_sessions}
        done = 0
        for future in as_completed(futures):
            session, has_data = future.result()
            results[session["session_key"]] = (session, has_data)
            done += 1
            print(f"  ... {done}/{len(past_sessions)} checked", end="\r")

    print()

    # Preserve newest->oldest order
    valid = [
        results[s["session_key"]][0]
        for s in reversed(past_sessions)
        if results.get(s["session_key"], (None, False))[1]
    ]

    if not valid:
        raise RuntimeError("No race sessions with lap data found.")

    for s in valid:
        print(f"  [+] {session_label(s)}")

    with open(CACHE_FILE, "w") as f:
        json.dump({
            "cached_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "sessions":  valid,
        }, f, indent=2)
    print(f"\n  Cached {len(valid)} races to {CACHE_FILE}.\n")
    return valid

# ── Data fetching ─────────────────────────────────────────────────────────────

def get_drivers(session_key: int) -> pd.DataFrame:
    data = api_get("drivers", session_key=session_key)
    df   = pd.DataFrame(data).drop_duplicates(subset="driver_number")
    return df.set_index("driver_number")


def get_laps(session_key: int) -> pd.DataFrame:
    data = api_get("laps", session_key=session_key)
    df   = pd.DataFrame(data)
    if df.empty:
        raise RuntimeError("No lap data for this session.")
    if "lap_duration" not in df.columns:
        raise RuntimeError("Unexpected API schema: 'lap_duration' missing.")

    df["lap_time_s"] = pd.to_numeric(df["lap_duration"], errors="coerce")
    df = df.dropna(subset=["lap_time_s"])
    df = df[df["lap_time_s"] > 0]

    def drop_outliers(grp):
        # Keep all laps for drivers with very few laps (early DNF)
        if len(grp) <= 3:
            return grp
        median   = grp["lap_time_s"].median()
        # Use 5x threshold to avoid dropping legitimate slow laps (SC, VSC)
        filtered = grp[grp["lap_time_s"] <= median * 5]
        return filtered if not filtered.empty else grp.nsmallest(1, "lap_time_s")

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = df.groupby("driver_number", group_keys=False).apply(drop_outliers)
    df["lap_number"] = pd.to_numeric(df["lap_number"], errors="coerce")
    return df


def get_positions(session_key: int) -> dict:
    """
    Return {driver_number: finishing_position} using the /position endpoint.
    OpenF1 doesn't have a results endpoint, so we take each driver's last
    recorded position at the end of the race as their finishing position.
    """
    try:
        data = api_get("position", session_key=session_key)
        if not data:
            return {}
        df = pd.DataFrame(data)
        if "date" not in df.columns or "driver_number" not in df.columns or "position" not in df.columns:
            return {}
        # Take the last recorded position entry per driver
        df = df.sort_values("date").groupby("driver_number").last().reset_index()
        # Only keep positions 1-20 (discard 0 or nulls which mean not classified)
        df = df[df["position"].between(1, 22)]
        return dict(zip(df["driver_number"].astype(int), df["position"].astype(int)))
    except Exception:
        return {}


def compute_stats(laps_df: pd.DataFrame, drivers_df: pd.DataFrame = None) -> pd.DataFrame:
    stats = (
        laps_df.groupby("driver_number")["lap_time_s"]
        .agg(fastest="min", slowest="max", average="mean", lap_count="count")
        .reset_index()
    )
    if drivers_df is not None:
        all_drivers = pd.DataFrame({"driver_number": drivers_df.index.tolist()})
        stats = all_drivers.merge(stats, on="driver_number", how="left")
        stats["lap_count"] = stats["lap_count"].fillna(0).astype(int)
    return stats


def load_session_data(session: dict) -> tuple:
    key        = session["session_key"]
    drivers_df = get_drivers(key)
    time.sleep(0.3)
    laps_df    = get_laps(key)
    time.sleep(0.3)
    stats_df   = compute_stats(laps_df, drivers_df)
    positions  = get_positions(key)
    return drivers_df, laps_df, stats_df, positions


# ── Interactive chart ─────────────────────────────────────────────────────────

class F1Viewer:
    """
    Self-contained interactive matplotlib figure.
    - Prev / Next buttons to move between races
    - Dropdown (RadioButtons) to jump to any race
    - Hover tooltip showing driver name + lap time
    - No terminal interaction needed after startup
    """

    BTN_COLOR      = "#2a2a3e"
    BTN_HOVER      = "#3a3a5e"
    PANEL_BG       = "#0f0f0f"
    CHART_BG       = "#1a1a2e"
    TEXT_COLOR      = "white"
    SUBTEXT_COLOR   = "#aaaaaa"

    def __init__(self, sessions: list):
        self.sessions    = sessions
        self.idx         = 0
        self.cache       = {}          # session_key -> (drivers_df, laps_df, stats_df)
        self._build_figure()
        self._load_and_draw()

    # ── Figure skeleton ───────────────────────────────────────────────────

    def _build_figure(self):
        self.fig = plt.figure(figsize=(20, 11), facecolor=self.PANEL_BG)
        self.fig.canvas.manager.set_window_title("F1 Lap Time Visualizer")

        # ── Axes layout ───────────────────────────────────────────────────
        # [dropdown panel | lap chart | stats chart]
        # [               | prev/next buttons      ]

        # Left panel: race dropdown
        self.ax_radio = self.fig.add_axes(
            [0.01, 0.12, 0.13, 0.83], facecolor="#111118"
        )
        for spine in self.ax_radio.spines.values():
            spine.set_edgecolor("#333")

        # Main lap chart
        self.ax_main = self.fig.add_axes([0.17, 0.18, 0.50, 0.72], facecolor=self.CHART_BG)

        # Stats bar chart
        self.ax_stats = self.fig.add_axes([0.70, 0.18, 0.29, 0.72], facecolor=self.CHART_BG)

        # Prev / Next buttons
        self.ax_prev = self.fig.add_axes([0.17, 0.04, 0.08, 0.06])
        self.ax_next = self.fig.add_axes([0.59, 0.04, 0.08, 0.06])

        self.btn_prev = Button(self.ax_prev, "◀  Older", color=self.BTN_COLOR, hovercolor=self.BTN_HOVER)
        self.btn_next = Button(self.ax_next, "Newer  ▶", color=self.BTN_COLOR, hovercolor=self.BTN_HOVER)

        for btn in (self.btn_prev, self.btn_next):
            btn.label.set_color(self.TEXT_COLOR)
            btn.label.set_fontsize(10)

        self.btn_prev.on_clicked(self._on_prev)
        self.btn_next.on_clicked(self._on_next)

        # Title text
        self.title_text = self.fig.text(
            0.17 + 0.50 / 2, 0.97, "",
            ha="center", va="top", color=self.TEXT_COLOR,
            fontsize=14, fontweight="bold",
        )

        # Loading / status text (centre of lap chart area)
        self.status_text = self.fig.text(
            0.17 + 0.50 / 2, 0.55, "",
            ha="center", va="center", color=self.SUBTEXT_COLOR,
            fontsize=11,
        )

        # Tooltip annotation
        self.tooltip = self.ax_main.annotate(
            "", xy=(0, 0), xytext=(15, 15),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.4", fc="#111", ec="#555", alpha=0.9),
            color="white", fontsize=8, visible=False,
        )

        self.fig.canvas.mpl_connect("motion_notify_event", self._on_hover)

        # Build radio buttons (race list in left panel)
        self._build_radio()

    def _build_radio(self):
        """Create RadioButtons for race selection in the left panel."""
        self.ax_radio.clear()
        labels = [self._short_label(s) for s in self.sessions]

        # matplotlib RadioButtons need at least 1 option
        self.radio = RadioButtons(
            self.ax_radio, labels,
            active=self.idx,
            activecolor="#E8002D",
        )
        # Style
        self.ax_radio.set_title("Races", color=self.TEXT_COLOR, fontsize=9, pad=4)
        for lbl in self.radio.labels:
            lbl.set_fontsize(7)
            lbl.set_color(self.TEXT_COLOR)


        self.radio.on_clicked(self._on_radio)

    def _short_label(self, session: dict) -> str:
        """Abbreviated label that fits in the narrow left panel."""
        full  = session_label(session)
        # Strip "FORMULA 1 " / "Formula 1 " prefix — too wide
        for prefix in ("FORMULA 1 ", "Formula 1 ", "FORMULA 1\n"):
            if full.upper().startswith(prefix.upper()):
                full = full[len(prefix):]
                break
        # Trim to ~28 chars
        return full if len(full) <= 28 else full[:26] + "…"

    # ── Event handlers ────────────────────────────────────────────────────

    def _on_prev(self, _event):
        if self.idx + 1 < len(self.sessions):
            self.idx += 1
            self._sync_radio()
            self._load_and_draw()

    def _on_next(self, _event):
        if self.idx > 0:
            self.idx -= 1
            self._sync_radio()
            self._load_and_draw()

    def _on_radio(self, label):
        labels = [self._short_label(s) for s in self.sessions]
        if label in labels:
            new_idx = labels.index(label)
            if new_idx != self.idx:
                self.idx = new_idx
                self._load_and_draw()

    def _sync_radio(self):
        """Update radio selection without triggering on_clicked."""
        self.radio.set_active(self.idx)

    def _on_hover(self, event):
        if event.inaxes != self.ax_main or not hasattr(self, "_plot_lines"):
            self.tooltip.set_visible(False)
            self.fig.canvas.draw_idle()
            return

        best_dist = 8          # pixels
        best_label = None
        best_xy    = None

        for line, name in self._plot_lines:
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            if len(xdata) == 0:
                continue
            # Transform data coords -> display coords
            xy_disp = self.ax_main.transData.transform(
                list(zip(xdata, ydata))
            )
            dists = ((xy_disp[:, 0] - event.x) ** 2 +
                     (xy_disp[:, 1] - event.y) ** 2) ** 0.5
            min_i = dists.argmin()
            if dists[min_i] < best_dist:
                best_dist  = dists[min_i]
                best_label = f"{name}  {format_lap_time(ydata[min_i])}  (Lap {int(xdata[min_i])})"
                best_xy    = (xdata[min_i], ydata[min_i])

        if best_label:
            self.tooltip.set_text(best_label)
            self.tooltip.xy = best_xy
            self.tooltip.set_visible(True)
        else:
            self.tooltip.set_visible(False)

        self.fig.canvas.draw_idle()

    # ── Drawing ───────────────────────────────────────────────────────────

    def _show_status(self, msg: str):
        self.ax_main.clear()
        self.ax_stats.clear()
        self.status_text.set_text(msg)
        self.fig.canvas.draw_idle()
        plt.pause(0.01)

    def _load_and_draw(self):
        session = self.sessions[self.idx]
        key     = session["session_key"]

        self.ax_prev.set_visible(self.idx + 1 < len(self.sessions))
        self.ax_next.set_visible(self.idx > 0)
        self.title_text.set_text(session_label(session))

        # If already cached, draw immediately
        if key in self.cache:
            drivers_df, laps_df, stats_df, positions = self.cache[key]
            self._draw(drivers_df, laps_df, stats_df, positions)
            return

        # Otherwise load in background thread so UI stays responsive
        self._show_status("Loading data…")

        def _fetch():
            try:
                result = load_session_data(session)
                self.cache[key] = result
                # Schedule draw back on main thread
                self._pending_draw = (key, result)
            except Exception as e:
                self._pending_draw = (key, e)

        self._pending_draw = None
        t = threading.Thread(target=_fetch, daemon=True)
        t.start()

        # Poll until done using matplotlib timer
        def _check(_):
            if self._pending_draw is None:
                return
            k, result = self._pending_draw
            self._pending_draw = None
            self._timer.stop()
            if isinstance(result, Exception):
                self._show_status(f"Failed to load:\n{result}")
            else:
                drivers_df, laps_df, stats_df, positions = result
                self.status_text.set_text("")
                self._draw(drivers_df, laps_df, stats_df, positions)

        self._timer = self.fig.canvas.new_timer(interval=200)
        self._timer.add_callback(_check, None)
        self._timer.start()


    def _draw(self, drivers_df, laps_df, stats_df, positions=None):
        ax_main  = self.ax_main
        ax_stats = self.ax_stats

        ax_main.clear()
        ax_stats.clear()
        self._plot_lines = []

        for ax in (ax_main, ax_stats):
            ax.set_facecolor(self.CHART_BG)
            ax.tick_params(colors=self.TEXT_COLOR)
            for spine in ax.spines.values():
                spine.set_edgecolor("#444")

        driver_numbers = sorted(stats_df["driver_number"].unique())
        n_drivers      = len(driver_numbers)
        legend_handles = []

        # ── Lap time lines ────────────────────────────────────────────────
        for idx, drv_num in enumerate(driver_numbers):
            drv_laps = laps_df[laps_df["driver_number"] == drv_num].sort_values("lap_number")
            if drv_laps.empty:
                continue  # DNS — no laps to plot
            drv_info = drivers_df.loc[drv_num] if drv_num in drivers_df.index else None
            name     = drv_info["name_acronym"] if drv_info is not None else str(drv_num)
            team     = (drv_info.get("team_name", "") if drv_info is not None else "")
            colour   = team_colour(team, idx)

            line, = ax_main.plot(
                drv_laps["lap_number"], drv_laps["lap_time_s"],
                color=colour, linewidth=1.2, alpha=0.85, zorder=2,
            )
            self._plot_lines.append((line, name))

            fastest_row = drv_laps.loc[drv_laps["lap_time_s"].idxmin()]
            ax_main.scatter(
                fastest_row["lap_number"], fastest_row["lap_time_s"],
                color=colour, marker="*", s=80, zorder=3,
            )
            legend_handles.append(Line2D([0], [0], color=colour, linewidth=2, label=name))

        ax_main.set_title("Lap Times per Driver  (* = fastest lap)", color=self.TEXT_COLOR, fontsize=11, pad=6)
        ax_main.set_xlabel("Lap Number", color=self.SUBTEXT_COLOR, fontsize=9)
        ax_main.set_ylabel("Lap Time", color=self.SUBTEXT_COLOR, fontsize=9)
        ax_main.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: format_lap_time(v)))
        ax_main.grid(color="#333", linestyle="--", linewidth=0.5, alpha=0.7)

        # Legend below main chart
        self.fig.legend(
            handles=legend_handles,
            loc="lower center",
            ncol=min(n_drivers, 11),
            bbox_to_anchor=(0.17 + 0.50 / 2, 0.01),
            facecolor="#111", edgecolor="#555", labelcolor=self.TEXT_COLOR,
            fontsize=7.5, framealpha=0.9, handlelength=1.5, columnspacing=0.8,
        )

        # ── Stats table ───────────────────────────────────────────────────
        merged = stats_df.merge(
            drivers_df[["name_acronym", "team_name"]].reset_index(),
            on="driver_number", how="left",
        )
        merged["name_acronym"] = merged["name_acronym"].fillna(merged["driver_number"].astype(str))

        # Classify each driver: finished, DNF (started but no finish pos), DNS (no laps)
        pos_map = positions or {}
        def classify(row):
            drv      = row["driver_number"]
            has_laps = row["lap_count"] > 0
            pos      = pos_map.get(drv)
            if pos and has_laps:
                return ("fin", pos)
            elif has_laps:
                return ("dnf", 900 - row["lap_count"])  # more laps = higher up in DNF section
            else:
                return ("dns", 999)

        merged[["status", "sort_key"]] = merged.apply(
            lambda r: pd.Series(classify(r)), axis=1
        )
        merged = merged.sort_values("sort_key").reset_index(drop=True)

        n_rows = len(merged)
        ax_stats.set_xlim(0, 1)
        ax_stats.set_ylim(-0.5, n_rows + 0.6)
        ax_stats.axis("off")
        ax_stats.set_title("Driver Lap Times", color=self.TEXT_COLOR, fontsize=11, pad=6)

        col_x    = [0.03, 0.14, 0.30, 0.50, 0.70, 0.88]
        col_hdrs = ["Pos", "Driver", "Laps", "Fastest", "Average", "Slowest"]
        for cx, hdr in zip(col_x, col_hdrs):
            ax_stats.text(cx, n_rows + 0.1, hdr,
                          color="#aaa", fontsize=7.5, fontweight="bold",
                          va="bottom", ha="left")
        ax_stats.axhline(n_rows - 0.1, color="#555", linewidth=0.8)

        for i, (_, row) in enumerate(merged.iterrows()):
            y      = n_rows - 1 - i
            colour = team_colour(row.get("team_name", ""), i)
            status = row["status"]

            if status == "fin":
                pos_str = str(int(pos_map[row["driver_number"]]))
                t_color = self.TEXT_COLOR
            elif status == "dnf":
                pos_str = "DNF"
                t_color = "#ff6b6b"
            else:
                pos_str = "DNS"
                t_color = "#888888"

            has_laps = row["lap_count"] > 0

            # Only show team colour stripe for classified finishers
            if status == "fin":
                ax_stats.barh(y, 1, 0.72, left=0, color=colour, alpha=0.12, zorder=0)
                ax_stats.barh(y, 0.008, 0.72, left=0, color=colour, alpha=1.0, zorder=1)

            lap_str  = str(int(row["lap_count"])) if has_laps else "0"
            row_data = [
                (col_x[0], pos_str,                                                t_color),
                (col_x[1], row["name_acronym"],                                    self.TEXT_COLOR),
                (col_x[2], lap_str,                                                t_color),
                (col_x[3], format_lap_time(row["fastest"]) if has_laps else "—",  t_color),
                (col_x[4], format_lap_time(row["average"]) if has_laps else "—",  t_color),
                (col_x[5], format_lap_time(row["slowest"]) if has_laps else "—",  t_color),
            ]
            for cx, val, tc in row_data:
                ax_stats.text(cx, y, val, color=tc, fontsize=7.5, va="center", ha="left")

            ax_stats.axhline(y - 0.38, color="#2a2a3e", linewidth=0.5)

        self.fig.canvas.draw_idle()

    def show(self):
        plt.show()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    sessions = load_all_race_sessions()
    viewer   = F1Viewer(sessions)
    viewer.show()


if __name__ == "__main__":
    main()