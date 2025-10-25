from tortoise import fields
from tortoise.models import Model


class QuestionAttempt(Model):
    id = fields.IntField(primary_key=True)
    user_id = fields.TextField()
    title = fields.CharField(max_length=255, unique=True)
    description = fields.TextField()
    code_template = fields.TextField()
    solution_sample = fields.TextField()
    difficulty = fields.TextField()
    category = fields.TextField()
    submitted_solution = fields.TextField()
    feedback = fields.TextField()
    attmpted_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Title:\t{self.title}\nDifficulty:\t{self.difficulty}\nCategory:\t{self.category}\nAttempted at:\t{self.attmpted_at}\nDescription:\n{self.description}\nAttempted Solution:\n{self.submitted_solution}"

    class Meta:
        table = "question_attempt"
