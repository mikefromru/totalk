from django.db import models
from django.template.defaultfilters import slugify

class Topic(models.Model):

	topic = models.CharField(max_length=100, unique=True)
	created = models.DateTimeField(auto_now_add=True)
	slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

	def __str__(self):
		return self.topic

	def save(self, *args, **kwargs):
		self.slug = slugify(self.topic)
		super(Topic, self).save(*args, **kwargs)

def content_file_name(instance, filename):
	return "sounds/{instance}/{file}".format(instance=instance.topic, file=filename)

class Question(models.Model):

	topic = models.ForeignKey(Topic, related_name='question', on_delete=models.CASCADE)
	name = models.CharField(max_length=650)
	sound = models.FileField(upload_to=content_file_name, blank=True, null=True)

	def __str__(self):
		check = None
		if self.sound:
			check = True
		else:
			check = False
		return f'{self.topic}/{self.name}  < Sound: {check} >'
