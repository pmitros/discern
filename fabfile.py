"""
This fabfile currently works to deploy this repo and ease to a new server.
A lot of settings and names will need to be changed around for your specific config, so
look through carefully.
"""

from __future__ import with_statement
import sys
import os
import logging

from fabric.api import local, lcd, run, env, cd, settings, prefix, sudo, shell_env, task
from fabric.contrib.console import confirm
from fabric.operations import put
from fabric.contrib.files import exists
from fabric.contrib import django
from path import path

#Overall usage is fab sandbox deploy or fab vagrant deploy.
#Add in your own task instead of sandbox or vagrant to specify your own settings.

# Deploy to Vagrant with:
# fab  -i /Users/nateaune/.rvm/gems/ruby-1.9.3-p374/gems/vagrant-1.0.7/keys/vagrant deploy

# Usage:
# MacOSX: 
# fab -i /Applications/Vagrant/embedded/gems/gems/vagrant-1.0.3/keys/vagrant deploy
# On Nate's Mac using Homebrew:
# fab  -i /Users/nateaune/.rvm/gems/ruby-1.9.3-p374/gems/vagrant-1.0.7/keys/vagrant deploy         
# Debian/Ubuntu: 
# fab -i /opt/vagrant/embedded/gems/gems/vagrant-1.0.3/keys/vagrant deploy

#Define this path so that we can import the django settings
ROOT_PATH = path(__file__).dirname()
ENV_ROOT = ROOT_PATH.dirname()
sys.path.append(ROOT_PATH)
sys.path.append(ENV_ROOT)

#Disable annoyting log messages.
logging.basicConfig(level=logging.ERROR)

# Environment settings
env.forward_agent = True

#This makes the paramiko logger less verbose
para_log=logging.getLogger('paramiko.transport')
para_log.setLevel(logging.ERROR)

#Use the below setting to pick the remote host that you want to deploy to.

@task
def vagrant(debug=True):
    env.environment = 'vagrant'
    env.hosts = ['vagrant@33.33.33.10', ]
    env.branch = 'dev'
    env.remote_user = 'vagrant'
    env.debug = debug


@task
def sandbox():
    env.environment = 'sandbox'
    env.hosts = ['vik@sandbox-service-api-001.m.edx.org', ]
    env.branch = 'master'
    env.remote_user = 'vik'

@task
def prepare_deployment():
    """
    Make a commit and push it to github
    """
    #Make a local commit with latest changes if needed.
    local('git add -p && git commit')
    local("git push")

@task
def check_paths():
    """
    Ensure that the paths are correct.
    """
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    log.info(ROOT_PATH)
    log.info(ENV_ROOT)

@task
def deploy():
    """
    Deploy to a server.
    """

    #Setup needed directory paths
    #May need to edit if you are using this for deployment
    up_one_level_dir = '/opt/wwc'
    code_dir = os.path.join(up_one_level_dir, "discern")
    ml_code_dir = os.path.join(up_one_level_dir, 'ease')
    database_dir = os.path.join(code_dir, "db")
    nltk_data_dir = '/usr/share/nltk_data'
    static_dir = os.path.join(code_dir, 'staticfiles')
    deployment_config_dir = os.path.join(ROOT_PATH, "deployment/configuration/")
    discern_repo_url = 'git@github.com:edx/discern.git'
    ease_repo_url = 'git@github.com:edx/ease.git'

    #this is needed for redis-server to function properly
    sudo('sysctl vm.overcommit_memory=1')

    with settings(warn_only=True):
        #Stop services
        sudo('service celery stop')
        sudo('service discern stop')
        static_dir_exists = exists(static_dir, use_sudo=True)
        if not static_dir_exists:
            sudo('mkdir -p {0}'.format(static_dir))
        repo_exists = exists(code_dir, use_sudo=True)
        #If the repo does not exist, then it needs to be cloned
        if not repo_exists:
            sudo('apt-get install git python')
            up_one_level_exists = exists(up_one_level_dir, use_sudo=True)
            if not up_one_level_exists:
                sudo('mkdir -p {0}'.format(up_one_level_dir))
            with cd(up_one_level_dir):
                #TODO: Insert repo name here
                run('git clone {0}'.format(discern_repo_url))

        sudo('chmod -R g+w {0}'.format(code_dir))

        #Check for the existence of the machine learning repo
        ml_repo_exists = exists(ml_code_dir, use_sudo=True)
        if not ml_repo_exists:
            with cd(up_one_level_dir):
                run('git clone {0}'.format(ease_repo_url))

        db_exists = exists(database_dir, use_sudo=True)
        if not db_exists:
            sudo('mkdir -p {0}'.format(database_dir))

        # TODO: should not be hardcoded to vik. For now, change to vagrant
        sudo('chown -R {0} {1}'.format(env.remote_user, up_one_level_dir))
        sudo('chmod -R g+w {0}'.format(ml_code_dir))

    with cd(ml_code_dir), settings(warn_only=True):
        #Update the ml repo
        run('git pull')

    with cd(code_dir), settings(warn_only=True):
        # With git...
        run('git pull')
        #Ensure that files are fixed
        run('sudo apt-get update')
        #This fixes an intermittent issue with compiling numpy
        run('sudo apt-get upgrade gcc')
        sudo('xargs -a apt-packages.txt apt-get install')
        #Activate your virtualenv for python
        result = run('source /opt/edx/bin/activate')
        if result.failed:
            #If you cannot activate the virtualenv, one does not exist, so make it
            sudo('apt-get install python-pip')
            sudo('pip install virtualenv')
            sudo('mkdir -p /opt/edx')
            sudo('virtualenv "/opt/edx"')
            sudo('chown -R {0} /opt/edx'.format(env.remote_user))

    with prefix('source /opt/edx/bin/activate'), settings(warn_only=True):
        with cd(code_dir):
            #Numpy and scipy are a bit special in terms of how they install, so we need pre-requirements.
            run('pip install -r pre-requirements.txt')
            run('pip install -r requirements.txt')
            # Sync django db and migrate it using south migrations
            run('python manage.py syncdb --noinput --settings=discern.aws --pythonpath={0}'.format(code_dir))
            run('python manage.py migrate --settings=discern.aws --pythonpath={0}'.format(code_dir))
            # TODO: check to see if there is a superuser already, and don't try to create it again
            #Comment this line out to avoid prompts when deploying
            #run('python manage.py createsuperuser --settings=discern.aws --pythonpath={0}'.format(code_dir))

            run('python manage.py collectstatic -c --noinput --settings=discern.aws --pythonpath={0}'.format(code_dir))
            run('python manage.py update_index --settings=discern.aws --pythonpath={0}'.format(code_dir))
            sudo('chown -R www-data {0}'.format(up_one_level_dir))

        with cd(ml_code_dir):
            sudo('xargs -a apt-packages.txt apt-get install')
            run('pip install -r pre-requirements.txt')
            run('pip install -r requirements.txt')

            #This is needed to support the ml algorithm
            sudo('mkdir -p {0}'.format(nltk_data_dir))
            if not exists(nltk_data_dir):
                sudo('python -m nltk.downloader -d {0} all'.format(nltk_data_dir))
                sudo('chown -R {0} {1}'.format(env.remote_user, nltk_data_dir))
            run('python setup.py install')

    with lcd(deployment_config_dir), settings(warn_only=True):
        sudo('mkdir -p /etc/nginx/sites-available')
        with cd(up_one_level_dir):
            #Move env and auth.json (read by aws.py if using it instead of settings)
            put('service-auth.json', 'auth.json', use_sudo=True)
            put('service-env.json', 'env.json', use_sudo=True)
        with cd('/etc/init'):
            #Upstart tasks that start and stop the needed services
            put('service-celery.conf', 'celery.conf', use_sudo=True)
            put('service-discern.conf', 'discern.conf', use_sudo=True)
        with cd('/etc/nginx/sites-available'):
            #Modify nginx settings to pass through discern
            put('service-nginx', 'default', use_sudo=True)

    with settings(warn_only=True):
        #Start all services back up
        sudo('service celery start')
        sudo('service discern start')
        sudo('service nginx restart')