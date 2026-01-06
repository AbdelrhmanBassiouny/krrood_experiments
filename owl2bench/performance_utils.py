import enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np


class Backend(enum.Enum):
    SQLAlchemy = "SQLAlchemy"
    SPARQLWrapper = "SPARQLWrapper"
    EQL = "EQL"
    RDFLib = "RDFLib"
    Owlready2 = "owlready2"


@dataclass
class QueryTiming:
    query_id: int
    backend_runtimes: Dict[Backend, List[float]]
    results_count: int

    @property
    def label(self) -> str:
        """
        Returns the label for this query.
        """
        return f"Q{self.query_id}"

    def get_average_runtime(self, backend: Backend) -> float:
        """
        Returns the average runtime for a given backend.
        """
        runtimes = self.backend_runtimes.get(backend, [])
        if not runtimes:
            return float("nan")
        return float(np.mean(runtimes))

    def get_runtime_standard_deviation(self, backend: Backend) -> float:
        """
        Returns the standard deviation of the runtime for a given backend.
        """
        runtimes = self.backend_runtimes.get(backend, [])
        if not runtimes:
            return float("nan")
        return float(np.std(runtimes))


@dataclass
class LoadingTiming:
    backend_runtimes: Dict[Backend, float]

    def get_runtime(self, backend: Backend) -> float:
        """
        Returns the loading runtime for a given backend.
        """
        return self.backend_runtimes.get(backend, float("nan"))


class LatexPerformanceExporter:
    def __init__(
        self,
        timings: Optional[List[QueryTiming]] = None,
        loading_timing: Optional[LoadingTiming] = None,
    ):
        self.timings = timings or []
        self.loading_timing = loading_timing

    def _format_timing(self, mean: float, std: float, is_best: bool = False) -> str:
        """
        Formats the timing results for LaTeX.
        """
        if np.isnan(mean):
            return "---"
        formatted = f"{mean * 1000:.2f} \\pm {std * 1000:.2f}"
        if is_best:
            return f"\\mathbf{{{formatted}}}"
        return formatted

    def _format_value(self, value: float, is_best: bool = False) -> str:
        """
        Formats a single value for LaTeX.
        """
        if np.isnan(value):
            return "---"
        formatted = f"{value * 1000:.2f}"
        if is_best:
            formatted = f"\\mathbf{{{formatted}}}"
        return f"${formatted}$"

    def _write_table(
        self, output_path: str, columns: List[str], rows: List[List[str]]
    ) -> None:
        """
        Writes a LaTeX table to a file.
        """
        column_spec = "l" * len(columns)
        header = " & ".join([f"\\textbf{{{col}}}" for col in columns]) + " \\\\"
        content = [
            "\\begin{tabular}{" + column_spec + "}",
            "\\hline",
            header,
            "\\hline",
        ]
        for row in rows:
            content.append(" & ".join(row) + " \\\\")
        content.append("\\hline")
        content.append("\\end{tabular}")

        with open(output_path, "w", encoding="utf-8") as file:
            file.write("\n".join(content))
        print(f"LaTeX table saved to {output_path}")

    def export_query_performance(
        self, output_path: str = "query_performance.tex"
    ) -> None:
        """
        Exports the query timing results to a LaTeX table.
        """
        backend_names = [backend.value.replace("_", "\\_") for backend in Backend]
        columns = ["Query", "Results"] + backend_names
        rows = []

        for timing in self.timings:
            means = {
                backend: timing.get_average_runtime(backend) for backend in Backend
            }
            stds = {
                backend: timing.get_runtime_standard_deviation(backend)
                for backend in Backend
            }

            valid_means = [mean for mean in means.values() if not np.isnan(mean)]
            min_mean = min(valid_means) if valid_means else float("inf")

            row_cells = [timing.label, str(timing.results_count)]
            for backend in Backend:
                is_best = not np.isnan(means[backend]) and means[backend] == min_mean
                formatted = self._format_timing(means[backend], stds[backend], is_best)
                row_cells.append(f"${formatted}$")
            rows.append(row_cells)

        rows.append(["\\hline"])  # Add separator before summary

        # Add geometric mean summary row
        backend_geomeans = self._calculate_geometric_means()
        valid_geomeans = [
            mean for mean in backend_geomeans.values() if not np.isnan(mean)
        ]
        min_geomean = min(valid_geomeans) if valid_geomeans else float("inf")

        summary_cells = ["\\textbf{Geom. Mean}", "---"]
        for backend in Backend:
            value = backend_geomeans[backend]
            is_best = not np.isnan(value) and value == min_geomean
            summary_cells.append(self._format_value(value, is_best))
        rows.append(summary_cells)

        self._write_table(output_path, columns, rows)

    def _calculate_geometric_means(self) -> Dict[Backend, float]:
        """
        Calculates geometric means for all backends.
        """
        backend_geomeans = {}
        for backend in Backend:
            runtimes = [timing.get_average_runtime(backend) for timing in self.timings]
            valid_runtimes = [
                runtime for runtime in runtimes if not np.isnan(runtime) and runtime > 0
            ]
            if valid_runtimes:
                backend_geomeans[backend] = float(
                    np.exp(np.mean(np.log(valid_runtimes)))
                )
            else:
                backend_geomeans[backend] = float("nan")
        return backend_geomeans

    def export_loading_performance(
        self, output_path: str = "loading_performance.tex"
    ) -> None:
        """
        Exports the loading timing results to a LaTeX table.
        """
        if self.loading_timing is None:
            raise ValueError("Loading timing data is not provided.")

        backend_names = [backend.value.replace("_", "\\_") for backend in Backend]
        columns = ["Backend", "Loading Time (ms)"]
        rows = []

        loading_runtimes = {
            backend: self.loading_timing.get_runtime(backend) for backend in Backend
        }
        valid_runtimes = [
            runtime for runtime in loading_runtimes.values() if not np.isnan(runtime)
        ]
        min_runtime = min(valid_runtimes) if valid_runtimes else float("inf")

        for backend in Backend:
            runtime = loading_runtimes[backend]
            is_best = not np.isnan(runtime) and runtime == min_runtime
            rows.append(
                [
                    backend.value.replace("_", "\\_"),
                    self._format_value(runtime, is_best),
                ]
            )

        self._write_table(output_path, columns, rows)
