==================================
Usage
==================================

This page walks you through lauching discern and exploring its APIs. Before we begin, let's sanity check for ease module installation. Simply import the ease.grade module.::

	$ python manage.py shell 
	Python 2.7.3 (default, Aug  1 2012, 05:16:07) 
	[GCC 4.6.3] on linux2
	Type "help", "copyright", "credits" or "license" for more information.
	(InteractiveConsole)
	>>> import ease.grade
	>>> 

On success, it should simply return you to the python prompt. If it throws an exception, there is a problem with the ease installation. 

Now let's run discern. You will need to run both the API server and the celery backend to process tasks.

1. ``python manage.py runserver 127.0.0.1:7999 --nostatic --settings=discern.settings --pythonpath=. &``
2. ``python manage.py celeryd -B --settings=discern.settings --pythonpath=. --loglevel=debug --logfile=/tmp/celery$$.out &``

Frontend User Interface
------------------------------
There is an easy to use frontend.  In order to use it, just navigate to 127.0.0.1:7999.  After that, you will be able to register using the links at the top.  After you register, you will see links to the API models.  Each model will allow you to get a list of existing models, add new ones, delete existing ones, and update them.  See the :ref:`api_models` section for more details on the models.

Getting started - the plan
------------------------------

Discern allows anyone to use machine learning based automated textual classification as an API service. You would generally want text that is associated with one or more *scores*. These *scores* can be anything. One example would be a corpus of essays that are scored. Another example would be `reddit <http://www.reddit.com/>`_ comments/posts, which are associated with upvotes/downvotes, which are a *score*. Another example would be news articles and stock prices before/after the news articles were released.  This tutorial will use reddit. 

Once you create a user, you will be able to interact with the various API resources.  I will get into how they are organized below.
We will use the python `request module <http://docs.python-requests.org/en/latest/>`_ to interact with our Discern server. For our examples,the response will be in `JSON <http://en.wikipedia.org/wiki/JSON>`_. To access reddit, the examples use `PRAW: The Python Reddit Api Wrapper <https://github.com/praw-dev/praw>`_.

The example code is broken down into small programs. Each will include this python module. 

.. literalinclude:: ../examples/common_settings.py
   :language: python
   :linenos:

The basic outline for this tutorial is:

#. Becoming familiar with the API and logging into Discern. 
#. Created an organization object and a course object
#. Add 10 essay objects and associate them with the problem. (note that although we are using 10 essay objects, higher accuracy will be achieved by using more)
#. Add 10 essay grade objects that are instructor scored and associate each one with an essay.
#. A model will now be created, and from now on, each additional essay you add will automatically have an essay grade object associated with it that contains the machine score.

Getting started - the API
--------------------------------------------------

As configured in this tutorial, the main end point for discern is `http://127.0.0.1:7999/essay_site/api/v1`. 
Consider the following code segment which enumerates the endpoints offered by Discern.

.. literalinclude:: ../examples/connect_to_api.py
   :language: python
   :linenos:

and here is the resulting output.::

	$ python connect_to_api.py 
	Status Code: 200
	{u'essay': {u'list_endpoint': u'/essay_site/api/v1/essay/', u'schema': u'/essay_site/api/v1/essay/schema/'}, u'essaygrade': {u'list_endpoint': u'/essay_site/api/v1/essaygrade/', u'schema': u'/essay_site/api/v1/essaygrade/schema/'}, u'course': {u'list_endpoint': u'/essay_site/api/v1/course/', u'schema': u'/essay_site/api/v1/course/schema/'}, u'membership': {u'list_endpoint': u'/essay_site/api/v1/membership/', u'schema': u'/essay_site/api/v1/membership/schema/'}, u'user': {u'list_endpoint': u'/essay_site/api/v1/user/', u'schema': u'/essay_site/api/v1/user/schema/'}, u'createuser': {u'list_endpoint': u'/essay_site/api/v1/createuser/', u'schema': u'/essay_site/api/v1/createuser/schema/'}, u'organization': {u'list_endpoint': u'/essay_site/api/v1/organization/', u'schema': u'/essay_site/api/v1/organization/schema/'}, u'problem': {u'list_endpoint': u'/essay_site/api/v1/problem/', u'schema': u'/essay_site/api/v1/problem/schema/'}, u'userprofile': {u'list_endpoint': u'/essay_site/api/v1/userprofile/', u'schema': u'/essay_site/api/v1/userprofile/schema/'}}
	Model: essay Endpoint: /essay_site/api/v1/essay/ Schema: /essay_site/api/v1/essay/schema/
	Model: essaygrade Endpoint: /essay_site/api/v1/essaygrade/ Schema: /essay_site/api/v1/essaygrade/schema/
	Model: course Endpoint: /essay_site/api/v1/course/ Schema: /essay_site/api/v1/course/schema/
	Model: membership Endpoint: /essay_site/api/v1/membership/ Schema: /essay_site/api/v1/membership/schema/
	Model: user Endpoint: /essay_site/api/v1/user/ Schema: /essay_site/api/v1/user/schema/
	Model: createuser Endpoint: /essay_site/api/v1/createuser/ Schema: /essay_site/api/v1/createuser/schema/
	Model: organization Endpoint: /essay_site/api/v1/organization/ Schema: /essay_site/api/v1/organization/schema/
	Model: problem Endpoint: /essay_site/api/v1/problem/ Schema: /essay_site/api/v1/problem/schema/
	Model: userprofile Endpoint: /essay_site/api/v1/userprofile/ Schema: /essay_site/api/v1/userprofile/schema/
	Status Code: 401

These endpoints map directly to the discern models. `HTTP verbs <http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods>`_ are used to perform operations on these objects. This tutorial will mainly use two verbs. POST and the associated data will create objects. GET will retrive it. You might find DELETE handy to clean up while you exploring this API. 

The last status code from the output was 401 because we aren't logged in. To proceed, we will have to create a user. Here is the code to create a user called *test*. Let's create one. 

.. literalinclude:: ../examples/create_user.py
   :language: python
   :linenos:

Alternatively, if you want a UI to interactively play around with these APIs, the POSTMAN add-on for Chrome is highly recommended. The endpoint is http://127.0.0.1:7999/essay_site/api/v1/createuser/. Just POST a JSON data dictionary containing the keys username and password (i.e., *{"username" : "test", "password" : "test"}* ).

Later in this tutorial, we will need to establish relationships between a course and its organization. This code segment enumerates the schema for course.

.. literalinclude:: ../examples/enumerate_schema.py
   :language: python
   :linenos:

The resulting output is...::

	$ python enumerate_schema.py
	Name: course_name 
		 Can be blank: False 
		 Type: string 
		 Help Text: Unicode string data. Ex: "Hello World"

	Name: created 
		 Can be blank: False 
		 Type: datetime 
		 Help Text: A date & time as a string. Ex: "2010-11-10T03:07:43"

	Name: id 
		 Can be blank: False 
		 Type: integer 
		 Help Text: Integer data. Ex: 2673

	Name: modified 
		 Can be blank: False 
		 Type: datetime 
		 Help Text: A date & time as a string. Ex: "2010-11-10T03:07:43"

	Name: organizations 
		 Can be blank: True 
		 Type: related 
		 Help Text: Many related resources. Can be either a list of URIs or list of individually nested resource data.

	Name: problems 
		 Can be blank: True 
		 Type: related 
		 Help Text: Many related resources. Can be either a list of URIs or list of individually nested resource data.

	Name: resource_uri 
		 Can be blank: False 
		 Type: string 
		 Help Text: Unicode string data. Ex: "Hello World"

	Name: users 
		 Can be blank: True 
		 Type: related 
		 Help Text: Many related resources. Can be either a list of URIs or list of individually nested resource data.

The fields **id**, **created**, and **modified** are automatically generated and we do not need to provide them. Given this, we only need to provide the non-blank field **course_name**. In the next section, we use the **organizations** key to link a course to our organization.

Getting started - creating objects 
---------------------------------------

When interacting with the Discern Server, you'll want to create an organization object and a course object. This script creates them for this tutorial. 

.. literalinclude:: ../examples/create_objects_for_tutorial.py
   :language: python
   :linenos:

As mentioned above we will be using reddit.  The heart of the matter is to have responses to a questions which have a score associated with them. With the reddit data, the title is used as the problem statement. The associated comments are the essays. The sum of up and down votes is the score. 

.. literalinclude:: ../examples/populate_essays.py
   :language: python
   :linenos:

No further action is required, the Discern Server will use the Enhanced AI Scoring Engine (or ease) to create a machine learning model. As the Discern Server processes the training essays, we will see more EssayGrades. Here is a script which queries discern about the essays and associcated scores. 

.. literalinclude:: ../examples/monitor_essay_processing.py
   :language: python
   :linenos:

Here is the output:: 

	$ python monitor_essay_processing.py 
	Scores for essay /essay_site/api/v1/essay/1/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [874], type: IN 
		 confidence: 0.93996137, score: [910], type: ML 
	Scores for essay /essay_site/api/v1/essay/2/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [151], type: IN 
		 confidence: 0.809622138, score: [234], type: ML 
	Scores for essay /essay_site/api/v1/essay/3/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [325], type: IN 
		 confidence: 0.953485473, score: [354], type: ML 
	Scores for essay /essay_site/api/v1/essay/4/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [98], type: IN 
		 confidence: 0.908300741, score: [92], type: ML 
	Scores for essay /essay_site/api/v1/essay/5/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [1404], type: IN 
		 confidence: 0.980497863, score: [1115], type: ML 
	Scores for essay /essay_site/api/v1/essay/6/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [539], type: IN 
		 confidence: 0.993892782, score: [485], type: ML 
	Scores for essay /essay_site/api/v1/essay/7/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [160], type: IN 
		 confidence: 0.774079147, score: [200], type: ML 
	Scores for essay /essay_site/api/v1/essay/8/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [29], type: IN 
		 confidence: 0.939284534, score: [18], type: ML 
	Scores for essay /essay_site/api/v1/essay/9/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [27], type: IN 
		 confidence: 0.622490266, score: [106], type: ML 
	Scores for essay /essay_site/api/v1/essay/10/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [25], type: IN 
		 confidence: 0.530272811, score: [61], type: ML 
	Scores for essay /essay_site/api/v1/essay/11/, problem /essay_site/api/v1/problem/1/
		 confidence: 1, score: [43], type: IN 
		 confidence: 0.586504779, score: [72], type: ML

The *IN* type is the score we provided to the Discern Server. The *ML* type is the score provided by ease. 

Next Steps
---------------------------------------

We now know how to add essays to a problem object and score some, after which automatic scoring is enabled.

Some things that we can try next are:

#. Adding more essays with **essay_type** "train" and scoring them by adding essaygrades.  This will make our models more accurate.
#. Add in essays with **essay_type** "test" in order for the machine to automatically score them. ("test" indicates that the essays will not be used as data to train the machine learning model).
#. Evaluate the accuracy of the scoring by comparing the *ML* scores to the *IN* scores.
#. Get the essays re-scored by setting the **has_been_ml_graded** field on the essays to false.  This will cause the system to add a new essaygrade object to them that is *ML* scored.
#. And, most importantly, try this with an alternative data source, and see what happens! We will be very interested to hear your results.
