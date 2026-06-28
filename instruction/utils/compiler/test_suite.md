# Comprehensive Layout Stress Test

::: composite_block
  
  ::: task_block {rows_per_page_tex=12, cols_tex=4}
    ## Task Set A
    
    ### Subtask A1 {col_span=2, row_span=1}
    This subtask takes 2 columns.
    
    ### Subtask A2 {col_span=2, row_span=1}
    ::: graph_block {xmin=-5, xmax=5, ymin=-5, ymax=5}
    * y = 0.5x + 1
    :::
  :::

  ::: task_block {rows_per_page_tex=12, cols_tex=4}
    ## Task Set B
    
    ### Subtask B1 {col_span=4, row_span=2}
    This is a large subtask spanning the full width of the block.
    
    ::: table_block {col_width=5em}
    | x | f(x)=x^2 [h: \Delta] |
    |---|---|
    | 1 | 1 |
    | 2 [v: +1] | 4 [v: +3] |
    | 3 [v: +1] | 9 [v: +5] |
    :::
    
    ### Subtask B2 {col_span=2, row_span=1}
    Small side-by-side cell 1.
    
    ### Subtask B3 {col_span=2, row_span=1}
    Small side-by-side cell 2.
  :::

:::
