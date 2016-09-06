Vagrant.configure("2") do |config|
    config.vm.box     = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"
#    config.vm.box_url = "https://s3.amazonaws.com/gsc-vagrant-boxes/ubuntu-12.04.2-i386-chef-11-omnibus.box"

    config.vm.network :forwarded_port, guest: 80, host: 8080, auto_correct: true
    config.vm.network :forwarded_port, guest: 7999, host: 7999, auto_correct: true    
    config.vm.network :private_network, ip: "33.33.33.10"

    # https://github.com/pypa/virtualenv/issues/209#issuecomment-11016919
#    config.vm.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root", "1"]
    
    config.vm.synced_folder ".", "/home/vagrant/discern", :nfs => true
    config.ssh.forward_agent

    config.vm.provision :ansible do |ansible|
        ansible.playbook = "deployment/playbooks/discern-dev.yml"
        ansible.inventory_file = "deployment/playbooks/hosts"
    end
end