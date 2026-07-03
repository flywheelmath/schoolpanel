import math
from typing import Any, Dict, List, Tuple
from core.models import Cell, Node, DomainEntity

class BaseGridRenderStrategy:
    def render(self, node: Node, visitor: Any) -> None:
        raise NotImplementedError("Grid layout strategies must implement render()")

class DualHeightRowsGridStrategy(BaseGridRenderStrategy):
    def render(self, node: Node, visitor: Any) -> None:
        out = visitor.output

        cells: List[Node] = [
            child for child in node.children
            if isinstance(child, (Cell, DomainEntity))
        ]

        idx = 0
        while idx < len(cells):
            current_row_cells, idx = self._pack_row_line(cells, idx)
            if not current_row_cells:
                break

            max_line_row_span = self._get_max_row_span(current_row_cells)
            min_line_row_span = self._get_min_row_span(current_row_cells)

            if max_line_row_span == min_line_row_span:
                if len(current_row_cells) == 1:
                    cell = current_row_cells[0]
                    visitor.context.set_width(cell, self._get_config(cell, "col_span", 4) / 12.0)
                    visitor.visit(cell)
                    visitor.emit_line("\\par\n")
                else:
                    visitor.emit_line("\\begin{gridrow}\n")
                    with visitor.indent():
                        for cell in current_row_cells:
                            visitor.context.set_width(cell, self._get_config(cell, "col_span", 4) / 12.0)
                            visitor.visit(cell)
                    visitor.emit_line("\\end{gridrow}\n")
                continue

            best_split_index = self._find_best_partition_split(current_row_cells)
            left_partition = current_row_cells[0:best_split_index]
            right_partition = current_row_cells[best_split_index:]

            tracks = self._get_track_assignment(left_partition, right_partition)

            visitor.emit_line("\\begin{gridrow}\n")
            with visitor.indent():
                if tracks["total_left_cols"] > 0:
                    if tracks["taller_on_left"]:
                        self._emit_taller_column(left_partition, tracks['total_left_cols'], visitor)
                    else:
                        idx = self._emit_shorter_column(
                            left_partition,
                            tracks["total_left_cols"],
                            tracks["taller_max_h"],
                            tracks["shorter_max_h"],
                            cells,
                            idx,
                            visitor
                        )
                if tracks["total_right_cols"] > 0:
                    if not tracks["taller_on_left"]:
                        self._emit_taller_column(right_partition, tracks["total_right_cols"], visitor)
                    else:
                        idx = self._emit_shorter_column(
                            right_partition,
                            tracks["total_right_cols"],
                            tracks["taller_max_h"],
                            tracks["shorter_max_h"],
                            cells,
                            idx,
                            visitor
                        )
            visitor.emit_line("\\end{gridrow}\n")

    def _get_config(self, node: Node, key: str, default: int = 1) -> int:
        if hasattr(node, "config") and isinstance(node.config, dict):
            return int(node.config.get(key, default))
        return default

    def _get_max_row_span(self, subset: List[Node]) -> int:
        if not subset: return 0
        return max(self._get_config(c, "row_span", 1) for c in subset)

    def _get_min_row_span(self, subset: List[Node]) -> int:
        if not subset: return 0
        return min(self._get_config(c, "row_span", 1) for c in subset)

    def _sum_col_spans(self, subset: List[Node]) -> int:
        return sum(self._get_config(c, "col_span", 1) for c in subset)

    def _pack_row_line(self, cells: List[Node], start_idx: int) -> Tuple[List[Node], int]:
        packed_cells: List[Node] = []
        accumulated_cols = 0
        idx = start_idx

        while idx < len(cells):
            next_cell = cells[idx]
            col_span = self._get_config(next_cell, "col_span", default=1)

            if accumulated_cols + col_span <= 12:
                packed_cells.append(next_cell)
                accumulated_cols += col_span
                idx += 1
            else:
                break
        return packed_cells, idx

    def _find_best_partition_split(self, row_cells: List[Node]) -> int:
        best_split_index = 0
        min_variance = float("inf")
        best_balance = float("inf")

        for i in range(len(row_cells) + 1):
            left_subset = row_cells[0:i]
            right_subset = row_cells[i:]

            variance = abs(self._get_max_row_span(left_subset) - self._get_min_row_span(left_subset)) + \
                        abs(self._get_max_row_span(right_subset) - self._get_min_row_span(right_subset))

            balance = abs(self._sum_col_spans(left_subset) - self._sum_col_spans(right_subset))

            if variance < min_variance:
                min_variance = variance
                best_balance = balance
                best_split_index = i
            elif variance == min_variance and balance < best_balance:
                best_balance = balance
                best_split_index = i

        return best_split_index

    def _get_track_assignment(self, left: List[Node], right: List[Node]) -> Dict[str, Any]:
        left_max_h = self._get_max_row_span(left)
        right_max_h = self._get_max_row_span(right)

        taller_on_left = left_max_h >= right_max_h

        return {
            "total_left_cols": self._sum_col_spans(left),
            "total_right_cols": self._sum_col_spans(right),
            "taller_max_h": left_max_h if taller_on_left else right_max_h,
            "shorter_max_h": right_max_h if taller_on_left else left_max_h,
            "taller_on_left": taller_on_left
        }

    def _compute_filler_rows(self, total_cols: int, remaining_height: int, cells: List[Node], start_idx: int) -> Tuple[List[Node], int]:
        filler_rows: List[List[Node]] = []
        temp_idx = start_idx

        while remaining_height > 0 and temp_idx < len(cells):
            inner_row_cells: List[Node] = []
            inner_accumulated_cols = 0
            inner_max_row_span = 0
            peek_idx = temp_idx

            while peek_idx < len(cells):
                next_cell = cells[peek_idx]
                next_span = self._get_config(next_cell, "col_span", default=1)
                next_row_span = self._get_config(next_cell, "row_span", default=1)

                remaining_sum = sum(self._get_config(cells[k], "col_span", 1) for k in range(peek_idx, len(cells)))
                all_remaining_fit_in_width = (inner_accumulated_cols + remaining_sum) <= total_cols

                if (inner_accumulated_cols + next_span <= total_cols) and \
                        (next_row_span <= remaining_height or all_remaining_fit_in_width):
                    inner_row_cells.append(next_cell)
                    inner_accumulated_cols += next_span
                    inner_max_row_span = max(inner_max_row_span, next_row_span)
                    peek_idx += 1
                else:
                    break

            if not inner_row_cells:
                break

            filler_rows.append(inner_row_cells)
            temp_idx = peek_idx

            if inner_max_row_span >= remaining_height:
                remaining_height = 0
            else:
                remaining_height -= inner_max_row_span

        return filler_rows, temp_idx

    def _emit_taller_column(self, partition_cells: List[Node], total_cols: int, visitor: Any) -> None:
        out = visitor.output
        width_fraction = total_cols / 12.0

        if len(partition_cells) == 1:
            cell = partition_cells[0]
            visitor.context.set_width(cell, width_fraction)
            visitor.visit(cell)
            return

        visitor.emit_line(f"\\begin{{gridcolumn}}[{width_fraction:.4f}]\n")
        with visitor.indent():
            for cell in partition_cells:
                visitor.context.set_width(cell, 1.0)
                visitor.visit(cell)
        visitor.emit_line("\\end{gridcolumn}%\n")

    def _emit_shorter_column(self, partition_cells: List[Node], total_cols: int, taller_max: int, shorter_max: int, cells: List[Node], global_idx: int, visitor: Any) -> int:
        out = visitor.output
        width_fraction = total_cols / 12.0

        remaining_height_space = taller_max - shorter_max
        filler_rows, updated_idx = self._compute_filler_rows(total_cols, remaining_height_space, cells, global_idx)

        total_items = len(partition_cells) + sum(len(row) for row in filler_rows)
        if total_items == 1:
            cell = partition_cells[0]
            visitor.context.set_width(cell, width_fraction)
            visitor.visit(cell)
            return updated_idx

        visitor.emit_line(f"\\begin{{gridcolumn}}[{width_fraction:.4f}]\n")
        with visitor.indent():
            for cell in partition_cells:
                cell_span = self._get_config(cell, "col_span", default=1)
                visitor.context.set_width(cell, cell_span / total_cols)
                visitor.visit(cell)
    
            if filler_rows:
                visitor.emit_line("\\par\n")
    
            for i, row in enumerate(filler_rows):
                for cell in row:
                    cell_span = self._get_config(cell, "col_span", default=1)
                    visitor.context.set_width(cell, cell_span / total_cols)
                    visitor.visit(cell)
    
                if i < len(filler_rows) - 1:
                    visitor.emit_line("\\par\n")

        visitor.emit_line("\\end{gridcolumn}%\n")
        return updated_idx
