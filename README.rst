======================================
Automatic slug generation from content
======================================

Install
-------

`pip install https://github.com/mireq/django-autoslugfield.git`

Usage
-----

Settings
^^^^^^^^

.. code:: python

	INSTALLED_APPS = (
		# ...
		'django_autoslugfield',
	)

Basic example
^^^^^^^^^^^^^

.. code:: python

	# models.py

	from django_autoslugfield import AutoSlugField

	class Item(models.Model):
		title = models.CharField(max_length=255)
		slug = AutoSlugField(max_length=255, unique=True)

Slug is created from `__unicode__` method. If another object with same slug
already exists slug will be suffixed with number.

Advanced usage
^^^^^^^^^^^^^^

AutoSlugField arguments are:

* `reserve_chars` - number of characters reserved for suffix
* `title_field` - use specific field instread of `__unicode__` method
* `filter_fields` - fields under witch is model always filterd eg.

.. code:: python

	from django_autoslugfield import AutoSlugField

	class Blog(models.Model):
		title = models.CharField(max_length=255)
		slug = AutoSlugField(filter_fields=('year', 'month'), max_length=255)
		year = models.IntegerField()
		month = models.IntegerField()

		class Meta:
			unique_together = ('slug', 'year', 'month')
