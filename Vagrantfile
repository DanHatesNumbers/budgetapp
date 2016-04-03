# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
    # Base box from https://github.com/terrywang/vagrantboxes/blob/master/archlinux-x86_64.md
    config.vm.box = "archlinux-x86_64"
    if Vagrant.has_plugin?("vagrant-cachier")
        config.cache.scope = :box
        config.cache.enable :pacman
    end

    config.vm.network "private_network", ip: "192.168.56.102"
    config.vm.network "forwarded_port", guest: 80, host:8080
    config.vm.network "forwarded_port", guest: 8080, host:8888

    config.vm.provider "virtualbox" do |vb|
        # Customize the amount of memory on the VM:
        vb.memory = "1024"
    end

    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "playbook.yml"
    end
end
