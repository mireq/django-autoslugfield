======================================
Automatic slug generation from content
======================================

|codecov| |version| |downloads| |license|

This package is used to automatically create unique slugs.

Install
-------

.. code:: bash

	pip install django-easy-autoslug

Usage
-----

Basic example
^^^^^^^^^^^^^

.. code:: python

	# models.py

	from django_autoslugfield import AutoSlugField

	class Item(models.Model):
		title = models.CharField(max_length=255)
		slug = AutoSlugField(max_length=255, unique=True)

Slug is created from ``__str__`` method. If another object with same slug
already exists slug will be suffixed with number ``-2``, ``-3`` …

Advanced usage
^^^^^^^^^^^^^^

AutoSlugField arguments are:

* `reserve_chars` - number of characters reserved for suffix (including sparator
  ``-``)
* `title_field` - use specific field instread of `__str__` method
* `in_respect_to` - generate unique slug for specific subset of fields

Following code can create same slug for another month / year.

.. code:: python

	from django_autoslugfield import AutoSlugField

	class Blog(models.Model):
		title = models.CharField(max_length=255)
		slug = AutoSlugField(filter_fields=('year', 'month'), max_length=255)
		year = models.IntegerField()
		month = models.IntegerField()

		class Meta:
			unique_together = ('slug', 'year', 'month')


.. |codecov| image:: https://codecov.io/gh/mireq/django-autoslugfield/branch/master/graph/badge.svg?token=T801PBRI31
	:target: https://codecov.io/gh/mireq/django-autoslugfield

.. |version| image:: https://badge.fury.io/py/django-easy-autoslug.svg
	:target: https://pypi.python.org/pypi/django-easy-autoslug/

.. |downloads| image:: https://img.shields.io/pypi/dw/django-easy-autoslug.svg
	:target: https://pypi.python.org/pypi/django-easy-autoslug/

.. |license| image:: https://img.shields.io/pypi/l/django-easy-autoslug.svg
	:target: https://pypi.python.org/pypi/django-easy-autoslug/
