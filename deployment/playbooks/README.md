	Install ansible:

	$ pip install ansible

Install Vagrant 1.1 and vagrant-ansible plugin:

	$ vagrant plugin install vagrant-ansible

From the root directory, run this command:

	$ ansible-playbook -vvv discern-dev.yml -i hosts -c ssh --private-key=~/.vagrant.d/insecure_private_key
