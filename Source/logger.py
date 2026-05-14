"""
logger.py - Structured logging system for PrimaryTeachingSMA.

Format: [2026-05-14 HH:MM:SS][AGENT-X][STEP] message
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

LOG_FILE   = os.getenv("LOG_FILE", "./outputs/agents.log")
LOG_LEVEL  = os.getenv("LOG_LEVEL", "INFO")
TRACE_FILE = os.getenv("TRACE_FILE", "../Learning_Log/execution_trace.txt")

Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
Path(TRACE_FILE).parent.mkdir(parents=True, exist_ok=True)


# ── Custom formatter ───────────────────────────────────────────────────────────

class AgentFormatter(logging.Formatter):
    """Produces lines like: [2026-05-14 10:32:05][AGENT-1][ANALYSIS] message"""

    def format(self, record: logging.LogRecord) -> str:
        ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        agent = getattr(record, "agent", "SYSTEM")
        step  = getattr(record, "step",  "INFO")
        return f"[{ts}][{agent}][{step}] {record.getMessage()}"


# ── Singleton logger setup ─────────────────────────────────────────────────────

_configured = False

def get_logger(name: str = "PrimaryTeachingSMA") -> logging.Logger:
    """
    Returns a logger that writes:
    - structured lines to outputs/agents.log
    - same lines to stdout
    Call once per module: logger = get_logger(__name__)
    """
    global _configured
    logger = logging.getLogger(name)

    if _configured or logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    fmt = AgentFormatter()

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    _configured = True
    return logger


# ── Convenience helpers ────────────────────────────────────────────────────────

def log_agent(logger: logging.Logger, agent: str, step: str, msg: str,
              level: str = "info") -> None:
    """
    Emit a structured log line.
    agent : e.g. 'AGENT-1', 'AGENT-2', 'AGENT-3', 'RAG', 'PDF', 'WORKFLOW'
    step  : e.g. 'ANALYSIS', 'GENERATION', 'RETRIEVAL', 'ERROR', 'COMPLETE'
    """
    extra = {"agent": agent, "step": step}
    getattr(logger, level)(msg, extra=extra)


# ── Execution trace writer ─────────────────────────────────────────────────────

class ExecutionTrace:
    """
    Appends a human-readable execution trace to Learning_Log/execution_trace.txt.
    Each run gets a timestamped block.
    """

    def __init__(self, trace_path: str = TRACE_FILE):
        self.path = Path(trace_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lines: list[str] = []

    def start(self, params: dict) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._lines = [
            "=" * 70,
            f"  EXECUTION TRACE — PrimaryTeachingSMA",
            f"  Started : {ts}",
            "=" * 70,
            "",
            "INPUT PARAMETERS",
            "-" * 40,
        ]
        for k, v in params.items():
            self._lines.append(f"  {k:<20} : {v}")
        self._lines.append("")

    def record(self, agent: str, step: str, detail: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._lines.append(f"[{ts}][{agent}][{step}]")
        self._lines.append(f"  {detail}")
        self._lines.append("")

    def finish(self, pdf_path: str, duration_sec: float) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._lines += [
            "-" * 40,
            "EXECUTION SUMMARY",
            "-" * 40,
            f"  Finished  : {ts}",
            f"  Duration  : {duration_sec:.2f}s",
            f"  PDF output: {pdf_path}",
            "",
            "=" * 70,
            "",
        ]
        with open(self.path, "a", encoding="utf-8") as f:
            f.write("\n".join(self._lines))

    def error(self, agent: str, error_msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._lines += [
            f"[{ts}][{agent}][ERROR]",
            f"  {error_msg}",
            "",
            "  *** EXECUTION ABORTED ***",
            "",
            "=" * 70,
            "",
        ]
        with open(self.path, "a", encoding="utf-8") as f:
            f.write("\n".join(self._lines))
