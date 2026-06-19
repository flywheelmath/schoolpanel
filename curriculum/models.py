from django.db import models
from django.db.models import Q

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
