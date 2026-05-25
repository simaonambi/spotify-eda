"""Tkinter dashboard for Week 4 visualization."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from src.visualization.queries import CURATED_QUERIES, CuratedQuery, query_map
from src.visualization.repository import DashboardRepository, QueryResult, SummaryMetric
from src.visualization.services import BackgroundRunner, TaskEvent


class DashboardApp:
    """Single-pane analytical dashboard."""

    def __init__(self, database_path: Path | str) -> None:
        self.repository = DashboardRepository(database_path)
        self.runner = BackgroundRunner()
        self.curated = query_map()
        self.root = tk.Tk()
        self.status_var = tk.StringVar(value="Ready")
        self.query_var = tk.StringVar(value=CURATED_QUERIES[0].title)
        self.description_var = tk.StringVar(value=CURATED_QUERIES[0].description)
        self.metric_vars: dict[str, tk.StringVar] = {}
        self.columns: tuple[str, ...] = ()
        self._configure_root()
        self._build_layout()
        self._bind_events()

    def run(self) -> None:
        """Start the dashboard event loop."""
        self.refresh_summary()
        self.run_selected_query()
        self.root.mainloop()

    def _configure_root(self) -> None:
        self.root.title("Spotify EDA")
        self.root.geometry("1320x820")
        self.root.configure(bg="#F7F7F2")
        self.root.protocol("WM_DELETE_WINDOW", self._shutdown)
        self._configure_style()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        colors = {"bg": "#F7F7F2", "fg": "#111111", "muted": "#5A5A5A", "line": "#D8D8D2"}
        style.configure(".", background=colors["bg"], foreground=colors["fg"], font=("Helvetica", 11))
        style.configure("Card.TFrame", background="#FFFFFF", borderwidth=0)
        style.configure("CardTitle.TLabel", font=("Helvetica", 10), foreground=colors["muted"])
        style.configure("CardValue.TLabel", font=("Helvetica", 24, "bold"))
        style.configure("Headline.TLabel", font=("Helvetica", 24, "bold"))
        style.configure("Body.TLabel", foreground=colors["muted"], wraplength=480)
        style.configure("Mono.TLabel", font=("Courier New", 10), foreground=colors["muted"])
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", rowheight=28)
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.map("Treeview", background=[("selected", "#111111")], foreground=[("selected", "#F7F7F2")])

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=32)
        container.pack(fill="both", expand=True)
        self._build_header(container)
        self._build_metrics(container)
        self._build_console(container)
        self._build_results(container)
        self._build_log(container)

    def _build_header(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=(0, 24))
        ttk.Label(frame, text="Spotify EDA", style="Headline.TLabel").pack(anchor="w")
        ttk.Label(frame, text="One surface. Curated analytics. Zero blocking.", style="Body.TLabel").pack(anchor="w", pady=(6, 0))

    def _build_metrics(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=(0, 24))
        for index, label in enumerate(("Artists", "Tracks", "Facts", "Sources")):
            self._build_metric_card(frame, index, label)

    def _build_metric_card(self, parent: ttk.Frame, index: int, label: str) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.grid(row=0, column=index, padx=(0, 16), sticky="nsew")
        parent.columnconfigure(index, weight=1)
        ttk.Label(card, text=label, style="CardTitle.TLabel").pack(anchor="w")
        variable = tk.StringVar(value="...")
        ttk.Label(card, textvariable=variable, style="CardValue.TLabel").pack(anchor="w", pady=(10, 0))
        self.metric_vars[label] = variable

    def _build_console(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=24)
        frame.pack(fill="x", pady=(0, 24))
        ttk.Label(frame, text="Curated SQL Console", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.query_box = ttk.Combobox(frame, textvariable=self.query_var, values=[item.title for item in CURATED_QUERIES], state="readonly")
        self.query_box.grid(row=1, column=0, sticky="ew", pady=(12, 12))
        ttk.Button(frame, text="Run", command=self.run_selected_query).grid(row=1, column=1, padx=(16, 0))
        ttk.Button(frame, text="Refresh", command=self.refresh_summary).grid(row=1, column=2, padx=(12, 0))
        ttk.Label(frame, textvariable=self.description_var, style="Body.TLabel").grid(row=2, column=0, columnspan=3, sticky="w")
        self.sql_text = tk.Text(frame, height=8, relief="flat", bg="#FFFFFF", fg="#111111", wrap="word", font=("Courier New", 10))
        self.sql_text.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(16, 0))
        frame.columnconfigure(0, weight=1)
        self._set_sql_preview(CURATED_QUERIES[0])

    def _build_results(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=18)
        frame.pack(fill="both", expand=True, pady=(0, 24))
        header = ttk.Frame(frame)
        header.pack(fill="x")
        ttk.Label(header, text="Result Grid", style="CardTitle.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.status_var, style="Mono.TLabel").pack(side="right")
        self.tree = ttk.Treeview(frame, show="headings")
        self.tree.pack(fill="both", expand=True, pady=(16, 0))

    def _build_log(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=18)
        frame.pack(fill="x")
        ttk.Label(frame, text="Progress", style="CardTitle.TLabel").pack(anchor="w")
        self.log_text = tk.Text(frame, height=6, relief="flat", bg="#FFFFFF", fg="#111111", font=("Courier New", 10))
        self.log_text.pack(fill="x", pady=(14, 0))
        self.log_text.configure(state="disabled")

    def _bind_events(self) -> None:
        self.query_box.bind("<<ComboboxSelected>>", self._on_query_selected)
        self.root.after(120, self._process_events)

    def _on_query_selected(self, _event: object) -> None:
        query = self._selected_query()
        self.description_var.set(query.description)
        self._set_sql_preview(query)

    def refresh_summary(self) -> None:
        self.runner.submit("Refresh summary", self.repository.fetch_summary)

    def run_selected_query(self) -> None:
        query = self._selected_query()
        self._set_busy(f"Running {query.title}")
        self.runner.submit(query.title, lambda: self.repository.run_query(query))

    def _selected_query(self) -> CuratedQuery:
        title = self.query_var.get()
        return next(query for query in CURATED_QUERIES if query.title == title)

    def _set_sql_preview(self, query: CuratedQuery) -> None:
        self.sql_text.configure(state="normal")
        self.sql_text.delete("1.0", "end")
        self.sql_text.insert("1.0", query.sql.strip())
        self.sql_text.configure(state="disabled")

    def _process_events(self) -> None:
        for event in self.runner.drain():
            self._handle_event(event)
        self.root.after(120, self._process_events)

    def _handle_event(self, event: TaskEvent) -> None:
        if event.kind == "started":
            self._append_log(f"{event.payload} started")
        if event.kind == "completed":
            self._handle_completion(*event.payload)
        if event.kind == "failed":
            self._handle_failure(*event.payload)

    def _handle_completion(self, label: str, payload: object) -> None:
        if isinstance(payload, tuple) and payload and isinstance(payload[0], SummaryMetric):
            self._apply_metrics(payload)
        if isinstance(payload, QueryResult):
            self._render_result(payload)
        self.status_var.set(f"{label} complete")
        self._append_log(f"{label} complete")

    def _handle_failure(self, label: str, error: Exception) -> None:
        self.status_var.set(f"{label} failed")
        self._append_log(f"{label} failed: {error}")

    def _apply_metrics(self, metrics: tuple[SummaryMetric, ...]) -> None:
        for metric in metrics:
            self.metric_vars[metric.label].set(metric.value)

    def _render_result(self, result: QueryResult) -> None:
        self.tree.delete(*self.tree.get_children())
        self._configure_columns(result.columns)
        for row in result.rows:
            self.tree.insert("", "end", values=tuple(row))
        self.status_var.set(f"{len(result.rows)} rows in {result.elapsed_ms:.1f} ms")

    def _configure_columns(self, columns: tuple[str, ...]) -> None:
        if columns == self.columns:
            return
        self.columns = columns
        self.tree.configure(columns=columns)
        for name in columns:
            self.tree.heading(name, text=name.replace("_", " ").title())
            self.tree.column(name, width=160, anchor="w")

    def _append_log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{stamp}  {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_busy(self, message: str) -> None:
        self.status_var.set(message)
        self._append_log(message)

    def _shutdown(self) -> None:
        self.runner.shutdown()
        self.root.destroy()


def launch_dashboard(database_path: Path | str) -> None:
    """Bootstrap the Tkinter dashboard."""
    DashboardApp(database_path=database_path).run()
