from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class Cargo(models.Model):
    id = fields.IntField(pk=True)
    date = fields.DateField()
    type = fields.CharField(max_length=50)
    rate = fields.FloatField()
    start_cost = fields.FloatField()
    add_cost = fields.FloatField()

