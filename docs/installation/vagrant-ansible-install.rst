==============================
Vagrant + Ansible Installation
==============================

Install Virtualbox
------------------

You can get the latest Virtualbox from http://virtualbox.org

Install Vagrant with plugin support
-----------------------------------

You can get the latest Vagrant at http://vagrantup.com

Install Ansible and it's dependencies
-------------------------------------

Create the virtualenv and install the Ansible requirements::

	$ virtualenv venv-discern
	$ source venv-discern/bin/activate
	(venv-discern)$ cd discern
	(venv-discern)$ pip install -r ansible-requirements.txt 

Install the vagrant-ansible plugin
----------------------------------

$ vagrant plugin install vagrant-ansible
Installing the 'vagrant-ansible' plugin. This can take a few minutes...
Installed the plugin 'vagrant-ansible (0.0.5)'!

Launch the Vagrant image
------------------------

To start up the Vagrant image, and bootstrap it using Ansible, run this command::

	$ vagrant up

Once the server is up and Ansible has finished executing the script, you can try to SSH into the server::

	$ vagrant ssh


Troubleshooting
---------------

If you need to run Ansible separately from vagrant for debugging, you can use this command::

	$ cd deployment/playbooks
	$ ansible-playbook -vvv discern-dev.yml -i hosts -c ssh --private-key=~/.vagrant.d/insecure_private_key 

If you get this error::

	The box 'precise' is still stored on disk in the Vagrant 1.0.x
	format. This box must be upgraded in order to work properly with
	this version of Vagrant.

You can then run this command::

	$ vagrant box repackage precise64 virtualbox
