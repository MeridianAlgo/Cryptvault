"""
CryptVault Desktop Theme
Dark professional trading terminal color palette.
"""

# ── Background layers ─────────────────────────────────────────────────────────
BG_DEEP    = "#080c10"   # deepest background (root window)
BG_BASE    = "#0d1117"   # main panels
BG_PANEL   = "#161b22"   # card/panel surface
BG_HOVER   = "#1f2937"   # hover / selected
BG_BORDER  = "#21262d"   # subtle borders

# ── Text ──────────────────────────────────────────────────────────────────────
TEXT_PRIMARY   = "#e6edf3"
TEXT_SECONDARY = "#8b949e"
TEXT_MUTED     = "#484f58"

# ── Accent colours ────────────────────────────────────────────────────────────
ACCENT_BLUE    = "#58a6ff"
ACCENT_CYAN    = "#39d0d8"
ACCENT_PURPLE  = "#bc8cff"
ACCENT_ORANGE  = "#ffa657"

# ── Semantic colours ──────────────────────────────────────────────────────────
GREEN         = "#3fb950"   # bullish / profit / up
GREEN_DIM     = "#1a4a23"
RED           = "#f85149"   # bearish / loss / down
RED_DIM       = "#4a1a1a"
YELLOW        = "#e3b341"   # warning / neutral
BLUE          = "#58a6ff"   # info

# ── Chart colours ─────────────────────────────────────────────────────────────
CANDLE_UP      = "#3fb950"
CANDLE_DOWN    = "#f85149"
WICK_UP        = "#238636"
WICK_DOWN      = "#b62324"
MA5_COLOR      = "#ffa657"
MA20_COLOR     = "#58a6ff"
MA50_COLOR     = "#bc8cff"
MA200_COLOR    = "#e3b341"
BB_COLOR       = "#58a6ff"
VOLUME_UP      = "#1a4a23"
VOLUME_DOWN    = "#4a1a1a"
GRID_COLOR     = "#161b22"
CHART_BG       = "#0d1117"

# ── Typography ────────────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"
FONT_MONO   = "Consolas"

FONT_TINY   = (FONT_FAMILY, 8)
FONT_SMALL  = (FONT_FAMILY, 10)
FONT_BODY   = (FONT_FAMILY, 11)
FONT_LABEL  = (FONT_FAMILY, 11, "bold")
FONT_TITLE  = (FONT_FAMILY, 13, "bold")
FONT_H1     = (FONT_FAMILY, 18, "bold")
FONT_MONO_S = (FONT_MONO, 10)
FONT_MONO_L = (FONT_MONO, 14, "bold")

# ── Sizing ────────────────────────────────────────────────────────────────────
SIDEBAR_WIDTH  = 200
TOPBAR_HEIGHT  = 56
STATUSBAR_H    = 24
CARD_RADIUS    = 8
BTN_RADIUS     = 6
PAD            = 12
PAD_SM         = 6

# ── ttk style name ────────────────────────────────────────────────────────────
STYLE_NAME = "CryptVault.TFrame"


def apply_ttk_theme(style) -> None:
    """Apply dark theme to ttk widgets."""
    style.theme_use("clam")

    style.configure(
        ".",
        background=BG_BASE,
        foreground=TEXT_PRIMARY,
        fieldbackground=BG_PANEL,
        troughcolor=BG_BORDER,
        bordercolor=BG_BORDER,
        focuscolor=ACCENT_BLUE,
        selectbackground=ACCENT_BLUE,
        selectforeground=TEXT_PRIMARY,
        insertcolor=TEXT_PRIMARY,
        font=FONT_BODY,
    )

    style.configure("TFrame", background=BG_BASE)
    style.configure("Card.TFrame", background=BG_PANEL)
    style.configure("Deep.TFrame", background=BG_DEEP)
    style.configure("Sidebar.TFrame", background=BG_DEEP)
    style.configure("TopBar.TFrame", background=BG_DEEP)
    style.configure("Status.TFrame", background=BG_DEEP)

    style.configure(
        "TLabel",
        background=BG_BASE,
        foreground=TEXT_PRIMARY,
        font=FONT_BODY,
    )
    style.configure("Card.TLabel", background=BG_PANEL)
    style.configure("Muted.TLabel", background=BG_BASE, foreground=TEXT_SECONDARY)
    style.configure("Deep.TLabel", background=BG_DEEP, foreground=TEXT_PRIMARY)
    style.configure("Sidebar.TLabel", background=BG_DEEP, foreground=TEXT_SECONDARY)
    style.configure("Title.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY, font=FONT_TITLE)
    style.configure(
        "BigPrice.TLabel",
        background=BG_PANEL,
        foreground=TEXT_PRIMARY,
        font=FONT_MONO_L,
    )
    style.configure("Green.TLabel", background=BG_PANEL, foreground=GREEN, font=FONT_LABEL)
    style.configure("Red.TLabel", background=BG_PANEL, foreground=RED, font=FONT_LABEL)
    style.configure("Accent.TLabel", background=BG_PANEL, foreground=ACCENT_BLUE, font=FONT_LABEL)
    style.configure("Status.TLabel", background=BG_DEEP, foreground=TEXT_SECONDARY, font=FONT_TINY)

    style.configure(
        "TButton",
        background=BG_HOVER,
        foreground=TEXT_PRIMARY,
        bordercolor=BG_BORDER,
        relief="flat",
        padding=(10, 6),
        font=FONT_BODY,
    )
    style.map(
        "TButton",
        background=[("active", BG_HOVER), ("pressed", ACCENT_BLUE)],
        foreground=[("active", TEXT_PRIMARY)],
    )

    style.configure(
        "Accent.TButton",
        background=ACCENT_BLUE,
        foreground="#000000",
        bordercolor=ACCENT_BLUE,
        font=FONT_LABEL,
        padding=(12, 6),
    )
    style.map("Accent.TButton", background=[("active", "#4a90e2")])

    style.configure(
        "Nav.TButton",
        background=BG_DEEP,
        foreground=TEXT_SECONDARY,
        bordercolor=BG_DEEP,
        relief="flat",
        padding=(8, 10),
        font=FONT_BODY,
        anchor="w",
    )
    style.map(
        "Nav.TButton",
        background=[("active", BG_HOVER), ("selected", BG_PANEL)],
        foreground=[("active", TEXT_PRIMARY), ("selected", ACCENT_BLUE)],
    )

    style.configure(
        "TEntry",
        fieldbackground=BG_HOVER,
        foreground=TEXT_PRIMARY,
        insertcolor=TEXT_PRIMARY,
        bordercolor=BG_BORDER,
        relief="flat",
        padding=(8, 5),
        font=FONT_BODY,
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT_BLUE)])

    style.configure(
        "TCombobox",
        fieldbackground=BG_HOVER,
        foreground=TEXT_PRIMARY,
        background=BG_HOVER,
        arrowcolor=TEXT_SECONDARY,
        bordercolor=BG_BORDER,
        relief="flat",
    )
    style.map("TCombobox", fieldbackground=[("readonly", BG_HOVER)])

    style.configure(
        "Vertical.TScrollbar",
        background=BG_HOVER,
        troughcolor=BG_BASE,
        arrowcolor=TEXT_SECONDARY,
        bordercolor=BG_BASE,
        relief="flat",
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=BG_HOVER,
        troughcolor=BG_BASE,
        arrowcolor=TEXT_SECONDARY,
        bordercolor=BG_BASE,
        relief="flat",
    )

    style.configure(
        "TNotebook",
        background=BG_BASE,
        bordercolor=BG_BORDER,
        tabmargins=[0, 0, 0, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=BG_DEEP,
        foreground=TEXT_SECONDARY,
        padding=(14, 7),
        font=FONT_BODY,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BG_BASE)],
        foreground=[("selected", ACCENT_BLUE)],
    )

    style.configure(
        "TSeparator",
        background=BG_BORDER,
    )

    style.configure(
        "TProgressbar",
        background=ACCENT_BLUE,
        troughcolor=BG_HOVER,
        bordercolor=BG_HOVER,
        lightcolor=ACCENT_BLUE,
        darkcolor=ACCENT_BLUE,
    )
    style.configure(
        "Green.TProgressbar",
        background=GREEN,
        troughcolor=BG_HOVER,
    )
    style.configure(
        "Red.TProgressbar",
        background=RED,
        troughcolor=BG_HOVER,
    )
