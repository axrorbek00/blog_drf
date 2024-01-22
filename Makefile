run:
	./manage.py runserver

mig:
	python manage.py makemigrations
	python manage.py migrate


createsuperuser:
	 python manage.py createsuperuser