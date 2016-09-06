This is an example project for discern.


Running the example
---------------------------------

If you are running discern at 127.0.0.1:7999 and you have performed all setup instructions, do the following from the discern top level directory to run the example::

    $ cd /examples/problem_grader (this directory)
    $ pip install -r requirements.txt
    $ python manage.py syncdb --noinput
    $ python manage.py migrate --noinput
    $ python manage.py collectstatic --noinput
    $ python manage.py runserver 127.0.0.1:7998 --nostatic

You should now be able to navigate to 127.0.0.1:7998 and use the frontend.  You will be able to create a course.  After creation, clicking on the course will let you view the problems.  You can then add problems to the course.  You will then be able to use the write essays and grade essays actions.

Pointing the example to another API endpoint
------------------------------------

If you want to point the example application to another API endpoint (ie a hosted instance), change `API_URL_BASE` in the `problem_grader/settings.py` file to point to the hosted API server you want to use.