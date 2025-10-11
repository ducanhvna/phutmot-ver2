from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AuditModel(models.Model):
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	created_user = models.ForeignKey(User, related_name="%(class)s_created", on_delete=models.SET_NULL, null=True, blank=True)
	modified_user = models.ForeignKey(User, related_name="%(class)s_modified", on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		abstract = True

class AttributeGroup(AuditModel):
	name = models.CharField(max_length=100, unique=True)
	display_name = models.CharField(max_length=150)
	description = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.display_name

class AttributeSubGroup(AuditModel):
	group = models.ForeignKey(AttributeGroup, on_delete=models.CASCADE, related_name="subgroups")
	name = models.CharField(max_length=100)
	display_name = models.CharField(max_length=150)
	sequence = models.PositiveIntegerField(default=0)
	description = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.display_name

class Attribute(AuditModel):
	subgroup = models.ForeignKey(AttributeSubGroup, on_delete=models.CASCADE, related_name="attributes")
	name = models.CharField(max_length=100)
	display_name = models.CharField(max_length=150)
	code_mch = models.CharField(max_length=50)
	sequence = models.PositiveIntegerField(default=0)
	info = models.JSONField(blank=True, null=True)

	def __str__(self):
		return self.display_name

# ProductGroup model
class ProductGroup(AuditModel):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.name

class Tag(AuditModel):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.name

class Product(AuditModel):
	product_group = models.ForeignKey('ProductGroup', on_delete=models.PROTECT, related_name='products', null=True)
	name = models.CharField(max_length=150)
	description = models.TextField(blank=True, null=True)
	info = models.JSONField(blank=True, null=True)
	tags = models.ManyToManyField(Tag, related_name="products", blank=True)

	def __str__(self):
		return self.name
