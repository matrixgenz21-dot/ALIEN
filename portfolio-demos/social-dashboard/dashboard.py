"""
Social Media Analytics Dashboard
By: Matrix Tech Solutions (Fiverr Portfolio)

Features:
- Multi-platform analytics (Instagram, YouTube, TikTok, Twitter)
- Follower growth tracking
- Engagement rate calculator
- Post performance analysis
- Best posting time suggestions
- Charts and graphs
- Data export to Excel/PDF
- Beautiful dark theme GUI
- Demo data included for showcase

This is a professional analytics tool for social media managers.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
from datetime import datetime, timedelta
import json
import os

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ============ COLORS ============

COLORS = {
    "bg": "#0a0a1a",
    "sidebar": "#12122a",
    "card": "#1a1a35",
    "primary": "#6c5ce7",
    "instagram": "#e1306c",
    "youtube": "#ff0000",
    "tiktok": "#69c9d0",
    "twitter": "#1da1f2",
    "success": "#00b894",
    "warning": "#fdcb6e",
    "text": "#dfe6e9",
    "text_muted": "#636e72",
    "border": "#2d3436",
}


# ============ DEMO DATA GENERATOR ============

def generate_demo_data():
    """Generate realistic social media demo data."""
    platforms = {
        "Instagram": {
            "followers": 45200,
            "following": 1203,
            "posts": 342,
            "engagement_rate": 4.7,
            "color": COLORS["instagram"],
            "daily_followers": [],
            "post_performance": [],
            "hourly_engagement": [0] * 24,
        },
        "YouTube": {
            "followers": 12800,
            "following": 0,
            "posts": 156,
            "engagement_rate": 6.2,
            "color": COLORS["youtube"],
            "daily_followers": [],
            "post_performance": [],
            "hourly_engagement": [0] * 24,
        },
        "TikTok": {
            "followers": 89500,
            "following": 456,
            "posts": 567,
            "engagement_rate": 8.1,
            "color": COLORS["tiktok"],
            "daily_followers": [],
            "post_performance": [],
            "hourly_engagement": [0] * 24,
        },
        "Twitter": {
            "followers": 23100,
            "following": 890,
            "posts": 1245,
            "engagement_rate": 2.3,
            "color": COLORS["twitter"],
            "daily_followers": [],
            "post_performance": [],
            "hourly_engagement": [0] * 24,
        },
    }

    for name, data in platforms.items():
        base = data["followers"]
        # 30 days follower growth
        for i in range(30):
            growth = random.randint(-50, 200)
            base += growth
            data["daily_followers"].append({
                "date": (datetime.now() - timedelta(days=29 - i)).strftime("%d/%m"),
                "count": base,
                "growth": growth,
            })

        # Post performance (last 20 posts)
        for i in range(20):
            likes = random.randint(100, 5000)
            comments = random.randint(10, 500)
            shares = random.randint(5, 200)
            views = likes * random.randint(5, 20)
            data["post_performance"].append({
                "post": f"Post #{20 - i}",
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "views": views,
                "engagement": round((likes + comments + shares) / max(views, 1) * 100, 1),
                "date": (datetime.now() - timedelta(days=i * 2)).strftime("%Y-%m-%d"),
            })

        # Hourly engagement (best times to post)
        peak_hours = [9, 12, 17, 20, 21]
        for h in range(24):
            if h in peak_hours:
                data["hourly_engagement"][h] = random.randint(70, 100)
            elif abs(h - 12) < 4 or abs(h - 20) < 3:
                data["hourly_engagement"][h] = random.randint(40, 70)
            else:
                data["hourly_engagement"][h] = random.randint(5, 30)

    return platforms


# ============ MAIN APP ============

class SocialDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Social Media Analytics — Matrix Tech")
        self.root.geometry("1250x750")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(1050, 650)

        self.data = generate_demo_data()
        self.current_platform = "Instagram"

        self._create_sidebar()
        self._create_main_area()
        self._show_overview()

    def _create_sidebar(self):
        sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="SOCIAL", bg=COLORS["sidebar"], fg=COLORS["primary"],
                 font=("Segoe UI", 20, "bold")).pack(pady=(25, 0))
        tk.Label(sidebar, text="Analytics Dashboard", bg=COLORS["sidebar"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 9)).pack(pady=(0, 30))

        menu = [
            ("Overview", self._show_overview),
            ("Instagram", lambda: self._show_platform("Instagram")),
            ("YouTube", lambda: self._show_platform("YouTube")),
            ("TikTok", lambda: self._show_platform("TikTok")),
            ("Twitter", lambda: self._show_platform("Twitter")),
            ("Comparison", self._show_comparison),
            ("Best Times", self._show_best_times),
            ("Export Data", self._export_data),
        ]

        self.menu_buttons = {}
        for text, cmd in menu:
            btn = tk.Button(sidebar, text=f"  {text}", bg=COLORS["sidebar"], fg=COLORS["text_muted"],
                            font=("Segoe UI", 11), relief="flat", anchor="w", padx=15, pady=6,
                            activebackground=COLORS["card"], cursor="hand2", command=cmd)
            btn.pack(fill="x", padx=8, pady=2)
            self.menu_buttons[text] = btn

        tk.Label(sidebar, text="Matrix Tech Solutions", bg=COLORS["sidebar"],
                 fg=COLORS["text_muted"], font=("Segoe UI", 8)).pack(side="bottom", pady=10)

    def _set_active(self, key):
        for k, btn in self.menu_buttons.items():
            if k == key:
                btn.configure(bg=COLORS["card"], fg=COLORS["primary"])
            else:
                btn.configure(bg=COLORS["sidebar"], fg=COLORS["text_muted"])

    def _create_main_area(self):
        self.main = tk.Frame(self.root, bg=COLORS["bg"])
        self.main.pack(side="right", fill="both", expand=True)

    def _clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _header(self, title, sub=""):
        h = tk.Frame(self.main, bg=COLORS["bg"])
        h.pack(fill="x", padx=25, pady=(20, 15))
        tk.Label(h, text=title, bg=COLORS["bg"], fg=COLORS["text"],
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        if sub:
            tk.Label(h, text=sub, bg=COLORS["bg"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 10)).pack(side="left", padx=15, pady=(6, 0))
        return h

    # ============ OVERVIEW ============

    def _show_overview(self):
        self._clear()
        self._set_active("Overview")
        self._header("Dashboard Overview", "All platforms at a glance")

        # Platform cards
        cards = tk.Frame(self.main, bg=COLORS["bg"])
        cards.pack(fill="x", padx=25, pady=5)

        total_followers = 0
        total_posts = 0
        avg_engagement = 0

        for i, (name, data) in enumerate(self.data.items()):
            total_followers += data["followers"]
            total_posts += data["posts"]
            avg_engagement += data["engagement_rate"]

            card = tk.Frame(cards, bg=COLORS["card"], padx=18, pady=15)
            card.grid(row=0, column=i, padx=6, pady=5, sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=name, bg=COLORS["card"], fg=data["color"],
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")
            tk.Label(card, text=f"{data['followers']:,}", bg=COLORS["card"], fg=COLORS["text"],
                     font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(5, 0))
            tk.Label(card, text="Followers", bg=COLORS["card"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 9)).pack(anchor="w")

            growth = sum(d["growth"] for d in data["daily_followers"][-7:])
            growth_color = COLORS["success"] if growth > 0 else "#ff0000"
            tk.Label(card, text=f"{'+'if growth>0 else ''}{growth:,} this week", bg=COLORS["card"],
                     fg=growth_color, font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
            tk.Label(card, text=f"Engagement: {data['engagement_rate']}%", bg=COLORS["card"],
                     fg=COLORS["text_muted"], font=("Segoe UI", 9)).pack(anchor="w")

        avg_engagement /= len(self.data)

        # Summary row
        summary = tk.Frame(self.main, bg=COLORS["bg"])
        summary.pack(fill="x", padx=25, pady=10)

        for i, (label, value, color) in enumerate([
            ("Total Followers", f"{total_followers:,}", COLORS["primary"]),
            ("Total Posts", f"{total_posts:,}", COLORS["success"]),
            ("Avg Engagement", f"{avg_engagement:.1f}%", COLORS["warning"]),
            ("Platforms", str(len(self.data)), COLORS["primary"]),
        ]):
            sc = tk.Frame(summary, bg=COLORS["card"], padx=20, pady=12)
            sc.grid(row=0, column=i, padx=6, sticky="nsew")
            summary.grid_columnconfigure(i, weight=1)
            tk.Label(sc, text=value, bg=COLORS["card"], fg=color,
                     font=("Segoe UI", 20, "bold")).pack(anchor="w")
            tk.Label(sc, text=label, bg=COLORS["card"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 9)).pack(anchor="w")

        # Growth chart
        if MATPLOTLIB_AVAILABLE:
            chart_frame = tk.Frame(self.main, bg=COLORS["card"], padx=10, pady=10)
            chart_frame.pack(fill="both", expand=True, padx=25, pady=(5, 20))

            fig = Figure(figsize=(9, 3), facecolor=COLORS["card"])
            ax = fig.add_subplot(111)
            ax.set_facecolor(COLORS["bg"])

            for name, data in self.data.items():
                dates = [d["date"] for d in data["daily_followers"]]
                counts = [d["count"] for d in data["daily_followers"]]
                ax.plot(dates, counts, label=name, color=data["color"], linewidth=2)

            ax.set_title("30-Day Follower Growth", color=COLORS["text"], fontsize=12, pad=10)
            ax.legend(facecolor=COLORS["card"], edgecolor=COLORS["border"], labelcolor=COLORS["text"])
            ax.tick_params(colors=COLORS["text_muted"], labelsize=8)
            ax.set_xticks(dates[::5])
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    # ============ PLATFORM VIEW ============

    def _show_platform(self, platform):
        self._clear()
        self._set_active(platform)
        data = self.data[platform]
        self._header(f"{platform} Analytics", f"Engagement Rate: {data['engagement_rate']}%")

        # Stats
        stats_frame = tk.Frame(self.main, bg=COLORS["bg"])
        stats_frame.pack(fill="x", padx=25, pady=5)

        for i, (label, value) in enumerate([
            ("Followers", f"{data['followers']:,}"),
            ("Posts", str(data["posts"])),
            ("Engagement", f"{data['engagement_rate']}%"),
            ("Avg Likes", f"{sum(p['likes'] for p in data['post_performance']) // max(len(data['post_performance']),1):,}"),
        ]):
            card = tk.Frame(stats_frame, bg=COLORS["card"], padx=18, pady=12)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=value, bg=COLORS["card"], fg=data["color"],
                     font=("Segoe UI", 22, "bold")).pack(anchor="w")
            tk.Label(card, text=label, bg=COLORS["card"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 9)).pack(anchor="w")

        if MATPLOTLIB_AVAILABLE:
            charts = tk.Frame(self.main, bg=COLORS["bg"])
            charts.pack(fill="both", expand=True, padx=25, pady=(10, 20))

            fig = Figure(figsize=(10, 4), facecolor=COLORS["bg"])

            # Follower growth
            ax1 = fig.add_subplot(121)
            ax1.set_facecolor(COLORS["card"])
            dates = [d["date"] for d in data["daily_followers"]]
            counts = [d["count"] for d in data["daily_followers"]]
            ax1.fill_between(dates, counts, alpha=0.3, color=data["color"])
            ax1.plot(dates, counts, color=data["color"], linewidth=2)
            ax1.set_title("Follower Growth", color=COLORS["text"], fontsize=11)
            ax1.tick_params(colors=COLORS["text_muted"], labelsize=7)
            ax1.set_xticks(dates[::5])
            for spine in ax1.spines.values():
                spine.set_color(COLORS["border"])

            # Post performance
            ax2 = fig.add_subplot(122)
            ax2.set_facecolor(COLORS["card"])
            posts = data["post_performance"][:10]
            names = [p["post"] for p in posts]
            likes = [p["likes"] for p in posts]
            ax2.barh(names, likes, color=data["color"], alpha=0.8)
            ax2.set_title("Top Posts by Likes", color=COLORS["text"], fontsize=11)
            ax2.tick_params(colors=COLORS["text_muted"], labelsize=8)
            for spine in ax2.spines.values():
                spine.set_color(COLORS["border"])

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, charts)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    # ============ COMPARISON ============

    def _show_comparison(self):
        self._clear()
        self._set_active("Comparison")
        self._header("Platform Comparison", "Side-by-side analytics")

        if not MATPLOTLIB_AVAILABLE:
            tk.Label(self.main, text="Install matplotlib:\npip install matplotlib",
                     bg=COLORS["bg"], fg=COLORS["warning"], font=("Segoe UI", 14)).pack(pady=50)
            return

        fig = Figure(figsize=(10, 6), facecolor=COLORS["bg"])

        names = list(self.data.keys())
        colors_list = [self.data[n]["color"] for n in names]

        # Followers comparison
        ax1 = fig.add_subplot(221)
        ax1.set_facecolor(COLORS["card"])
        followers = [self.data[n]["followers"] for n in names]
        ax1.bar(names, followers, color=colors_list)
        ax1.set_title("Followers", color=COLORS["text"], fontsize=11)
        ax1.tick_params(colors=COLORS["text_muted"])
        for spine in ax1.spines.values():
            spine.set_color(COLORS["border"])

        # Engagement comparison
        ax2 = fig.add_subplot(222)
        ax2.set_facecolor(COLORS["card"])
        engagement = [self.data[n]["engagement_rate"] for n in names]
        ax2.bar(names, engagement, color=colors_list)
        ax2.set_title("Engagement Rate %", color=COLORS["text"], fontsize=11)
        ax2.tick_params(colors=COLORS["text_muted"])
        for spine in ax2.spines.values():
            spine.set_color(COLORS["border"])

        # Posts comparison
        ax3 = fig.add_subplot(223)
        ax3.set_facecolor(COLORS["card"])
        posts = [self.data[n]["posts"] for n in names]
        ax3.bar(names, posts, color=colors_list)
        ax3.set_title("Total Posts", color=COLORS["text"], fontsize=11)
        ax3.tick_params(colors=COLORS["text_muted"])
        for spine in ax3.spines.values():
            spine.set_color(COLORS["border"])

        # Follower share pie
        ax4 = fig.add_subplot(224)
        ax4.pie(followers, labels=names, colors=colors_list, autopct="%1.0f%%",
                textprops={"color": COLORS["text"], "fontsize": 9})
        ax4.set_title("Follower Share", color=COLORS["text"], fontsize=11)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.main)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 20))

    # ============ BEST TIMES ============

    def _show_best_times(self):
        self._clear()
        self._set_active("Best Times")
        self._header("Best Posting Times", "When your audience is most active")

        if not MATPLOTLIB_AVAILABLE:
            tk.Label(self.main, text="Install matplotlib:\npip install matplotlib",
                     bg=COLORS["bg"], fg=COLORS["warning"], font=("Segoe UI", 14)).pack(pady=50)
            return

        fig = Figure(figsize=(10, 5), facecolor=COLORS["bg"])

        hours = [f"{h:02d}:00" for h in range(24)]

        for i, (name, data) in enumerate(self.data.items()):
            ax = fig.add_subplot(2, 2, i + 1)
            ax.set_facecolor(COLORS["card"])
            vals = data["hourly_engagement"]
            bar_colors = [data["color"] if v > 60 else COLORS["text_muted"] for v in vals]
            ax.bar(range(24), vals, color=bar_colors, alpha=0.8)
            ax.set_title(name, color=data["color"], fontsize=11)
            ax.set_xticks(range(0, 24, 4))
            ax.set_xticklabels([hours[h] for h in range(0, 24, 4)])
            ax.tick_params(colors=COLORS["text_muted"], labelsize=7)
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])

            # Mark best times
            best = sorted(range(24), key=lambda h: vals[h], reverse=True)[:3]
            ax.set_xlabel(f"Best: {', '.join(f'{h}:00' for h in sorted(best))}",
                         color=COLORS["success"], fontsize=8)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.main)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 20))

    # ============ EXPORT ============

    def _export_data(self):
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Error", "Install openpyxl:\npip install openpyxl")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not filepath:
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Overview"
        ws.append(["Platform", "Followers", "Posts", "Engagement Rate"])
        for name, data in self.data.items():
            ws.append([name, data["followers"], data["posts"], data["engagement_rate"]])

        for name, data in self.data.items():
            ws2 = wb.create_sheet(f"{name} Growth")
            ws2.append(["Date", "Followers", "Daily Growth"])
            for d in data["daily_followers"]:
                ws2.append([d["date"], d["count"], d["growth"]])

            ws3 = wb.create_sheet(f"{name} Posts")
            ws3.append(["Post", "Likes", "Comments", "Shares", "Views", "Engagement %", "Date"])
            for p in data["post_performance"]:
                ws3.append([p["post"], p["likes"], p["comments"], p["shares"], p["views"], p["engagement"], p["date"]])

        wb.save(filepath)
        messagebox.showinfo("Exported!", f"All analytics data saved to:\n{filepath}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SocialDashboard()
    app.run()
