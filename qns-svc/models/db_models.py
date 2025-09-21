from tortoise.models import Model
from tortoise import fields


class Category(Model):
    name = fields.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        table = "category"


class Difficulty(Model):
    level = fields.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.level

    class Meta:
        table = "difficulty"


class Question(Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    difficulty = fields.ForeignKeyField("models.Difficulty", related_name="difficulty")

    def __str__(self):
        return f"{self.title}\t{self.difficulty}\n{self.description}"

    class Meta:
        table = "question"


class QuestionCategory(Model):
    id = fields.IntField(primary_key=True)
    category = fields.ForeignKeyField("models.Category", related_name="questions")
    question = fields.ForeignKeyField("models.Question", related_name="categories")

    def __str__(self):
        return f"{self.question}\t{self.category}"

    class Meta:
        table = "question_category"
        unique_together = (("category", "question"),)
