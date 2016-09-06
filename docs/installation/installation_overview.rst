=================================
Installation Overview
=================================

There are three ways to install the Discern project:

1) Manually using the following instructions
2) Automatically to a VirtualBox using Vagrant and the Ansible-dev playbook. See :doc:`vagrant-ansible-install`
3) Automatically to an Amazon EC2 instance using the Ansible AWS playbooks. See the configuration_ repo and ml-api branch.

.. _configuration: https://github.com/edx/configuration/tree/vik/ml-api 

This assumes that you already have git installed on your computer. The main steps are::

	$ git clone git://github.com/edx/discern.git

or if you are working with a forked copy::

	$ git clone git@github.com:<your_user_account>/discern.git
	$ xargs -a discern/apt-packages.txt apt-get install
	$ virtualenv /path/to/edx
	$ source /path/to/edx/bin/activate
	$ cd discern
	$ pip install -r pre-requirements.txt
	$ pip install -r requirements.txt
	$ python manage.py syncdb --settings=discern.settings --noinput --pythonpath=DIR WHERE YOU CLONED REPO
	Choose "no" for create superuser if syncdb prompts you for it.
	
	$ python manage.py migrate --settings=discern.settings --noinput --pythonpath=DIR WHERE YOU CLONED REPO
	$ python manage.py collectstatic -c --noinput --settings=discern.settings --pythonpath=DIR WHERE YOU CLONED REPO

See :doc:`usage` for how to run this.  You will both need to run the server and the celery tasks.

You can skip the virtualenv commands if you like, but they will be a major help in keeping the packages for this repo separate from the rest of your system.

If you get errors using the above, you may need to create a database directory one level up from where you cloned the git repo (folder named "db")

You will need to install the ease repo (https://github.com/edx/ease) in the same base directory that you installed discern in order to get all functionality.  Follow the install instructions in that repo.

If all has gone well, you see a database directory called db. An sqlite3 database was created in it. The sqlite3 command can be used to inspect the tables which Django generated::

	$ sqlite3 db/service-api-db.db 
	SQLite version 3.7.9 2011-11-01 00:52:41
	Enter ".help" for instructions
	Enter SQL statements terminated with a ";"
	sqlite> .tables
	account_emailaddress                freeform_data_course              
	account_emailconfirmation           freeform_data_course_organizations
	auth_group                          freeform_data_course_users        
	auth_group_permissions              freeform_data_essay               
	auth_permission                     freeform_data_essaygrade          
	auth_user                           freeform_data_membership          
	auth_user_groups                    freeform_data_organization        
	auth_user_user_permissions          freeform_data_problem             
	celery_taskmeta                     freeform_data_problem_courses     
	celery_tasksetmeta                  freeform_data_userprofile         
	django_admin_log                    guardian_groupobjectpermission    
	django_content_type                 guardian_userobjectpermission     
	django_session                      ml_grading_createdmodel           
	django_site                         socialaccount_socialaccount       
	djcelery_crontabschedule            socialaccount_socialapp           
	djcelery_intervalschedule           socialaccount_socialapp_sites     
	djcelery_periodictask               socialaccount_socialtoken         
	djcelery_periodictasks              south_migrationhistory            
	djcelery_taskstate                  tastypie_apiaccess                
	djcelery_workerstate                tastypie_apikey    
