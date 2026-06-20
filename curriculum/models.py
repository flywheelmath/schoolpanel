from django.db import models
from django.db.models import Q

class ProcessType(models.TextChoices):
    RULE_BASED = 'RULE_BASED', 'Rule-based process'
    SCHEMA_BASED = 'SCHEMA_BASED', 'Schema-based process'

class Action(models.TextChoices):
    REWRITE = 'REWRITE', 'Rewrite'
    REPRESENT = 'REPRESENT', 'Represent'
    VERIFY = 'VERIFY', 'Verify'
    IDENTIFY = 'IDENTIFY', 'Identify'
    COMPARE = 'COMPARE', 'Compare'

class Modality(models.TextChoices):
    ALGEBRAIC = 'ALGEBRAIC', 'Algebraic'
    GRAPHICAL = 'GRAPHICAL', 'Graphical'
    NUMERICAL = 'NUMERICAL', 'Numerical'
    VERBAL = 'VERBAL', 'Verbal'
    MIXED = 'MIXED', 'Mixed'

class State(models.TextChoices):
    BRACKETED = 'BRACKETED', 'Bracketed' 
    RATIONAL = 'RATIONAL', 'Rational'

    UNCOMBINED_LIKE_TERMS = 'UNCOMBINED_LIKE_TERMS', 'Uncombined like terms'
    BILATERAL_LIKE_TERMS = 'BILATERAL_VARIABLE', 'Bilateral variable'

    ONE_STEP_ADDITIVE = 'ONE_STEP_ADDITIVE', 'Additive one-step'
    ONE_STEP_MULTIPLICATIVE = 'ONE_STEP_MULTIPLICATIVE', 'Multiplicative one-step'
    ONE_STEP_QUADRATIC = 'ONE_STEP_QUADRATIC', 'Quadratic one-step'
    ONE_STEP_RADICAL = 'ONE_STEP_RADICAL', 'Radical one-step'
    ONE_STEP_EXPONENTIAL = 'ONE_STEP_EXPONENTIAL', 'Exponential one-step'
    ONE_STEP_LOGARITHMIC = 'ONE_STEP_LOGARITHMIC', 'Logarithmic one-step'

    TWO_STEP_EQUATION = 'TWO_STEP_EQUATION', 'Two-step equation'
    MULTI_STEP_EQUATION = 'MULTI_STEP_EQUATION', 'Multi-step equation'

    STANDARD_FORM = 'STANDARD_FORM', 'Standard Form'
    FACTORED_FORM = 'FACTORED_FORM', 'Factored Form'
    PARAMETRIZED_FORM = 'PARAMETRIZED_FORM', 'Parametrized form'

    ISOLATED_VARIABLE = 'ISOLATED_VARIABLE', 'Isolated variable'
    EVALUATED_OUTPUT = 'EVALUATED_OUTPUT', 'Evaluated output'
    TRUTH_VALUE = 'TRUTH_VALUE', 'Truth value'

    CONSTANT_CHANGE_PATTERN = 'CONSTANT-CHANGE PATTERN', 'Constant-change pattern'
    EXTREMA = 'EXTREMA', 'Extrema'
    INTERCEPTS = 'INTERCEPTS', 'Intercepts'
    SOLUTION_SET = 'SOLUTION_SET', 'Solution set'

    BEHAVIOR_CLASSIFICATION = 'BEHAVIOR_CLASSIFICATION','Behavior classification'
    SOLUTIONS_COUNT = 'SOLUTIONS_COUNT', 'Solutions count'

class SyntacticStructure(models.TextChoices):
    EXPRESSION = 'EXPRESSION', 'Expression'
    EQUALITY = 'EQUALITY', 'Equality'
    INEQUALITY = 'INEQUALITY', 'Inequality'
    FUNCTION = 'FUNCTION', 'Function'
    SEQUENCE = 'SEQUENCE', 'Sequence'
    DATA_SET = 'DATA_SET', 'Bivariate Data'
    SYSTEM = 'SYSTEM', 'System'

class Behavior(models.TextChoices):
    LINEAR = 'LINEAR', 'Linear'
    QUADRATIC = 'QUADRATIC', 'Quadratic'
    EXPONENTIAL = 'EXPONENTIAL', 'Exponential'
    GENERIC = 'GENERIC', 'Generic'
    SYSTEM = 'SYSTEM', 'System'
    NONE = '', 'None'



class MathObject(models.Model):
    syntactic_structure = models.CharField(
        max_length=50, 
        choices=SyntacticStructure.choices
    )
    type = models.CharField(
        max_length=50, 
        choices=Behavior.choices,
        default=Behavior.NONE,
        blank=True
    )
    system_components = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        help_text="Components of a system of syntactic structure."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['syntactic_structure', 'type'],
                name='unique_math_objects'
            ),
            models.CheckConstraint(
                check=~Q(syntactic_structure='SYSTEM') | Q(type='SYSTEM'),
                name='system_parent_has_system_type'
            )
        ]

    def __str__(self):
        syntactic_structure = self.get_syntactic_structure_display()
        type = self.get_family_display()
        return f"{type} {syntactic_structure}".strip()

class TaskClass(models.Model):
    title = models.CharField(max_length=255)
    process_type = models.CharField(
        max_length=50,
        choices=ProcessType.choices,
        default=ProcessType.RULE_BASED,
        help_text="Defines whether the problem-solving process is rule-based (recurrent) or schema-based (non-recurrent)."
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    math_object = models.ForeignKey(MathObject, on_delete=models.PROTECT, related_name='task_classes')
    given_state = models.CharField(max_length=50, choices=State.choices)
    goal_state = models.CharField(max_length=50, choices=State.choices)
    rep_in = models.CharField(max_length=50, choices=Modality.choices)
    rep_out = models.CharField(max_length=50, choices=Modality.choices)
    supportive_information = models.TextField(blank=True, help_text="Supportive Information for the task class.")
    procedural_information = models.TextField(blank=True, help_text="Procedural Information for the task class.")
    common_errors = models.JSONField(default=dict, blank=True, help_text="Anticipated misrules and misconceptions.")
    prerequisites = models.ManyToManyField(
        'self',
        through='TaskPrerequisite',
        symmetrical=False,
        blank=True
    )
    mcap_evidence_statements = models.ManyToManyField('standards.MCAPEvidenceStatement', blank=True, related_name="task_classes")
    terminal_duration = models.PositiveIntegerField(help_text="Minutes allocated")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(given_state=models.F('goal_state')),
                name='task_class_must_transition_state'
            )
        ]

    def __str__(self):
        return self.title

class TaskPrerequisite(models.Model):
    whole_task = models.ForeignKey(TaskClass, on_delete=models.CASCADE, related_name='required_prerequisites')
    prerequisite_task = models.ForeignKey(TaskClass, on_delete=models.CASCADE, related_name='required_by')
    requires_automation = models.BooleanField(
        default=False,
        help_text="Defines whether the prerequisite task must be automated to a high degree of fluency."
    )

    class Meta:
        unique_together = ['whole_task', 'prerequisite_task']

    def __str__(self):
        return f"{self.whole_task.title} requires {self.prerequisite_task.title}"

class ScaffoldLevel(models.TextChoices):
    WORKED_EXAMPLE = 'WORKED_EXAMPLE', 'Worked Example'
    COMPLETION_TASK = 'COMPLETION_TASK', 'Completion Task'
    PRACTICE = 'PRACTICE', 'Practice'
    FLUENCY = 'FLUENCY', 'Fluency'

class LearningTask(models.Model):
    task_class = models.ForeignKey(TaskClass, on_delete=models.CASCADE, related_name='learning_tasks')
    scaffold_level = models.CharField(max_length=20, choices=ScaffoldLevel.choices)
    content_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['task_class', 'scaffold_level']
