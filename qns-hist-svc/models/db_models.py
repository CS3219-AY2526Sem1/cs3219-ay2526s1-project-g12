from tortoise import fields
from tortoise.models import Model


class QuestionAttempt(Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    code_template = fields.TextField()
    solution_sample = fields.TextField()
    difficulty = fields.TextField()
    category = fields.TextField()
    time_elapsed = fields.IntField()
    submitted_solution = fields.TextField()
    attmpted_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Title:\t{self.title}\nDifficulty:\t{self.difficulty}\nCategory:\t{self.category}\nAttempted at:\t{self.attmpted_at}\nDescription:\n{self.description}\nAttempted Solution:\n{self.submitted_solution}"

    class Meta:
        table = "question_attempt"


class UserAttempt(Model):
    id = fields.IntField(primary_key=True)
    user_id = fields.CharField(max_length=255)
    question_attempt = fields.ForeignKeyField(
        model_name="models.QuestionAttempt", related_name="user_attempts"
    )

    def __str__(self):
        return f"User:\t{self.user_id}\nAttempt:\t{self.question_attempt}"

    class Meta:
        table = "user_question_attempt"
        unique_together = ("user_id", "question_attempt")


class AttemptFeedback(Model):
    id = fields.IntField(primary_key=True)
    question_attempt = fields.ForeignKeyField(
        model_name="models.QuestionAttempt",
        related_name="attempt_feedback",
        unique=True,
    )
    feedback = fields.TextField()

    def __str__(self):
        return f"Attempt:\n{self.question_attempt}\nFeedback:\n{self.feedback}"

    class Meta:
        table = "attempt_feedback"
