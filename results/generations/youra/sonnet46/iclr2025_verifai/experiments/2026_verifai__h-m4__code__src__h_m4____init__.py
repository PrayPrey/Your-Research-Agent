"""h_m4 — difficulty-stratified ECE analysis for h-m4 hypothesis."""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("h-m4")
except PackageNotFoundError:
    __version__ = "0.1.0"
