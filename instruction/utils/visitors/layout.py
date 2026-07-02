from core.models import Cell, Grid, TaskEntity


class BaseGridRenderStrategy:
    def render(self, node: Grid, visitor: "RenderTeXVisitor"):
        raise NotImplementedError("Grid layout strategies must implement render()")


class DualHeightRowsGridStrategy(BaseGridRenderStrategy):
    def render(self, node: Grid, visitor: "RenderTeXVisitor"):
        out = visitor.output
        out.append("% --- Begin Tree-Partition Lookahead Grid ---\n")

        cells = [
            child for child in node.children if isinstance(child, (Cell, TaskEntity))
        ]

        while cells:
            current_line_cells = []
            accumulated_cols = 0

            while cells and accumulated_cols < 12:
                next_c = cells[0]
                col_span = int(next_c.config.get("col_span", 1))
                if accumulated_cols + col_span <= 12:
                    current_line_cells.append(cells.pop(0))
                    accumulated_cols += col_span
                else:
                    break

            if not current_line_cells:
                break

            best_split = 0
            min_variance = float("inf")

            def get_max_span(subset):
                return (
                    max([int(c.config.get("row_span", 1)) for c in subset])
                    if subset
                    else 0
                )

            for i in range(len(current_line_cells) + 1):
                left_max = get_max_span(current_line_cells[:i])
                right_max = get_max_span(current_line_cells[i:])

                variance = abs(left_max - right_max)
                if variance < min_variance:
                    min_variance = variance
                    best_split = i

            left_partition = current_line_cells[:best_split]
            right_partition = current_line_cells[best_split:]

            left_max = get_max_span(left_partition)
            right_max = get_max_span(right_partition)

            left_width_cols = sum(
                int(c.config.get("col_span", 1)) for c in left_partition
            )
            right_width_cols = sum(
                int(c.config.get("col_span", 1)) for c in right_partition
            )

            left_width_fraction = max((left_width_cols / 12.0), 0)
            right_width_fraction = max((right_width_cols / 12.0), 0)

            out.append("\\begin{gridrow}\n")

            if (
                left_max == right_max
                or len(left_partition) == 0
                or len(right_partition) == 0
            ):
                for cell in current_line_cells:
                    span = int(cell.config.get("col_span", 1))
                    width_fraction = max((span / 12.0), 0)
                    visitor.context.set_width(cell, width_fraction)
                    visitor.visit(cell)
            else:
                is_left_taller = left_max > right_max
                taller_partition = left_partition if is_left_taller else right_partition
                shorter_partition = (
                    right_partition if is_left_taller else left_partition
                )

                taller_max = max(left_max, right_max)
                shorter_max = min(left_max, right_max)
                shorter_width_cols = (
                    right_width_cols if is_left_taller else left_width_cols
                )

                taller_width_fraction = (
                    left_width_fraction if is_left_taller else right_width_fraction
                )
                out.append(f"  \\begin{{gridcell}}[{taller_width_fraction:.4f}]\n")
                out.append(f"    \\begin{{grid}}\n")
                for cell in taller_partition:
                    span = int(cell.config.get("col_span", 1))
                    parent_width = sum(
                        int(x.config.get("col_span", 1)) for x in taller_partition
                    )
                    inner_width = span / parent_width
                    out.append(f"      \\begin{{gridcell}}[{inner_width:.4f}]\n")
                    if isinstance(cell, TaskEntity):
                        visitor.visit_taskentity(cell)
                    else:
                        visitor.generic_visit(cell)
                    out.append("      \\end{gridcell}\n")
                out.append("    \\end{grid}\n")
                out.append("  \\end{gridcell}\n")

                smaller_width_fraction = (
                    right_width_fraction if is_left_taller else left_width_fraction
                )
                out.append(f"  \\begin{{gridcell}}[{smaller_width_fraction:.4f}]\n")
                out.append("    \\begin{gridrow}\n")
                out.append("      \\begin{grid}\n")
                for cell in shorter_partition:
                    span = int(cell.config.get("col_span", 1))
                    inner_width = (
                        span / shorter_width_cols if shorter_width_cols > 0 else 1.0
                    )
                    visitor.context.set_width(cell, inner_width)
                    visitor.visit(cell)
                out.append("      \\end{grid}\n")
                out.append("    \\end{gridrow}\n")

                remaining_space = taller_max - shorter_max

                while remaining_space > 0 and cells:
                    next_cell = cells[0]
                    next_span = int(next_cell.config.get("col_span", 1))
                    next_row_span = int(next_cell.config.get("row_span", 1))

                    if next_span <= shorter_width_cols:
                        if next_row_span <= remaining_space + 1:
                            cells.pop(0)
                            out.append("    \\begin{gridrow}\n")
                            out.append("      \\begin{grid}\n")
                            inner_width = (
                                next_span / shorter_width_cols
                                if shorter_width_cols > 0
                                else 1.0
                            )
                            visitor.context.set_width(next_cell, inner_width)
                            visitor.visit(next_cell)
                            out.append("      \\end{grid}\n")
                            out.append("    \\end{gridrow}\n")

                            if next_row_span == remaining_space + 1:
                                remaining_space = 0
                            else:
                                remaining_space -= next_row_span
                        else:
                            break
                    else:
                        break

                out.append("  \\end{gridcell}\n")

            out.append("\\end{gridrow}\n")

        out.append("% --- End Tree-Partition Lookahead Grid ---\n")
