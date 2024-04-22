# OCR-P9
Django app
=======
# Python/Django - Book review platfrom "LITRevu"


A Django project enabling a community of users to publish book or article reviews and browse or request reviews on demand.


## Start project :

### Install environment :

#### 1 - Set virtual environment

`python -m venv ENV`

#### 2 - Activate virtual environment

`ENV/scripts/activate`

#### 3 - Install dependecies

`pip install -r requirements.txt`

#### 4 - Run local server

`python manage.py runserver`

#### 5 - Generate flake8 report

`flake8 --format=html --htmldir=flake8_report --exclude=ENV,.idea`

***

## Use it
### What can be done :

- Ask for a review about a new book
- Answer tickets with your review
- Create a review from scratch for a new book
- See all reviews about a book
- See all answers for a ticket
- Follow / unfollow / block other users
- Homepage : Watch activity from users you follow, answers to your tickets and your own activity
- Posts : Watch all activity about every other users
- Abonnements : Search users and manage your relations (follow / unfollow / ban / unban)
