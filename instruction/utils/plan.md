* populate database with learning tasks
* create database models for Lesson and LessonTask
  - Lesson:
    * data
    * title
    * tex_preamble
  - LessonTask:
    * lesson: foreign key to Lesson
    * task: foreign key to LearningTask
    * sort_order
    * on_worksheet: boolean
    * on_slides: boolean

* task numbering
  - constraint: worksheet task and subtask numbering must match slide task and subtask numbering, but slides and worksheet may include different tasks and subtasks
  - solution: calculate numbering at compile time
    * loop through LessonTask objects ordered by sort_order
      - if on_worksheet = True, calculate counter values and insert identical task and subtask labels into TeX and Vue files
      - increment task counter

* updating list of LessonTask objects included in lesson
  - constraint: if the user edits the TeX or Vue files for a lesson after the initial fetch and then decides to edit the list of LessonTask objects by including or removing a task, we need to preserve the edits to the source code for the already fetched items
  - solution: when the lesson source code is initialized, create a dedicated directory:

lessons/{date}/
|- worksheet.tex
|- slides.md
|- tasks/
    |- task1.tex
    |- task1.md
    |- task2.tex
    |- task2.md

  - if the lesson object is updated and a LearningTask object is appended to the LessonTask list field, create new task TeX and md files, but do not overwrite files for previously included LearningTask objects

* graphs and tables
  - semantic graph and table objects are processed by TeX and Vue renderers when the lesson directory is populated/updated
