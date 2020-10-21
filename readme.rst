Jogging Statistics
==================

:author: David Palao (david.palao@gmail.com)
:abstract: REST API to record jogging times of users


Requirements
------------

1. API Users must be able to create an account and log in.
2. All API calls must be authenticated.
3. Implement at least three roles with different permission levels:

  * a regular user would only be able to CRUD on their owned records,
  * a user manager would be able to CRUD only users, and
  * an admin would be able to CRUD all records and users.

4. Each time entry when entered has a date, distance, time, and location.
5. Based on the provided date and location, API should connect to a weather
   API provider and get the weather conditions for the run, and store that with each run.
6. The API must create a report on average speed & distance per week.
7. The API must be able to return data in the JSON format.
8. The API should provide filter capabilities for all endpoints that return a
   list of elements, as well should be able to support pagination.
9. The API filtering should allow using parenthesis for defining operations
   precedence and use any combination of the available fields. The supported
   operations should at least include

   * or,
   * and,
   * eq (equals),
   * ne (not equals),
   * gt (greater than),
   * lt (lower than).
     
   Example -> (date eq '2016-05-01') AND ((distance gt 20) OR (distance lt 10)).
10. REST API. Make it possible to perform all user and admin actions via the API,
    including authentication.
11. In any case, you should be able to explain how a REST API works and demonstrate
    that by creating functional tests that use the REST Layer directly. Please be
    prepared to use REST clients like Postman, cURL, etc. for this purpose.
12. Write unit and e2e tests.


Implementation
--------------

The API is implemented as a Django project with one (Django) application. It uses
``Django REST framework``.


Testing
-------

In order to test the application the following steps are recommended (assuming that
``some/path`` is actually an existing path; the virtual environment will be created
in it):

1. Create a virtual environment::

     $ python3.8 -m venv some/path/JoggingStats-py38

2. Activate it::

     $ source some/path/JoggingStats-py38/bin/activate

3. Go to the directory where the repository has been cloned to::

     (JoggingStats-py38) $ cd local/path/to/repo/

4. Install the requirements::

     (JoggingStats-py38) $ pip install -r requirements.text

5. Run the functional tests (aka e2e tests) with::

     (JoggingStats-py38) $ python manage.py test functional_tests

6. The unit tests can be run with::

     (JoggingStats-py38) $ python manage.py test jogging

7. For manual exploratory tests::

     (JoggingStats-py38) $ python manage.py runserver

   and explore with your favourite tool (browser, httpie, curl, ...) using
   the url shown in the screen (typically ``http://127.0.0.1:8000/``).

