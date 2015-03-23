# Introduction #

We are moving AmCAT to use debian (apt) repositories for updating, both internally (for our 'stable' version) and externally (for any interested party). These repositories are located on launchpad under

This document describes how to build and update the debian repositories.

# Account information (launchpad and PGP) #

We are using the launchpad account https://launchpad.net/~amcat registered using the gmail account vanatteveldt@gmail.com. The passphrase for this account is in the file ~amcat/password.txt on amcat-sql2.vu.nl.

The key used for signing the PPA is key 557F5874 which is in the keyring of the amcat user on amcat-sql2.vu.nl with the same passphrase as the account itself. The fingerprint of this key is `70ED 4F2B 2804 4977 C888  77A6 9A8A 6F87 557F 5874`.

# Build server #

To make it easy to build updates, we created a virtual server on the AmCAT virtual host. Due to NAT, this server is only available by ssh'ing to `sw-server.labs.vu.nl` and then going to `192.168.122.26` (or using virt-manager to open a direct terminal on the machine).

To facilitate cloning the build server, the volume named 'buildclone' is created on the disk. For reference, this was created using the command:

```
lvcreate -L 20G -n buildclone vg_swserver
```

If you wish to create a second clone, first create a new volume using this commend (but with a different volume name!)

# Steps for building a new version #
  1. Pause `amcat-build` so it can be cloned. Use the `virt-manager` GUI or the virsh command:
```
[wva@sw-server ~]$ sudo virsh suspend amcat-build
Domain amcat-build suspended
[wva@sw-server ~]$ sudo virsh list
 Id Name                 State
----------------------------------
  4 amcat-build          paused
```
  1. Clone the build server to make sure that we can get back to the correct state.
```
[wva@sw-server ~]$ sudo virt-clone --original amcat-build --name "buildclone" --file /dev/vg_swserver/buildclone
Clone 'buildclone' created successfully.
[wva@sw-server ~]$ sudo virsh start buildclone
Domain buildclone started
```
  1. Find out the IP Address of the newly cloned machine and connect. I currently don't know a better way to do this than using `arp -a` . If there are ever too many machines on the network, we can specify the MAC address in the clone stage and use that to filter the arp results. The new guest should be in the arp as after the `start` command it used DHCP to get an IP address.
```
[wva@sw-server ~]$ arp -a | grep 192.168
? (192.168.122.125) at 00:16:3e:cc:56:7a [ether] on virbr0
[wva@sw-server ~]$ ssh 192.168.122.125
[...]
wva@amcat-build:~$     
```
> > Note that the new clone still has the 'wrong' name, but we can be sure that it is not amcat-build because we suspended that in the previous step.
  1. TODO: the actual work!
  1. Delete the clone
```
[wva@sw-server ~]$ sudo virsh shutdown buildclone
Domain buildclone is being shutdown
[wva@sw-server ~]$ sudo virsh destroy buildclone
Domain buildclone destroyed
[wva@sw-server ~]$ sudo virsh list | grep buildclone
[wva@sw-server ~]$
```