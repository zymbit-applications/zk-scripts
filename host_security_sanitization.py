#!/usr/bin/python3

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Copyright (C) 2022 by copyright Zymbit
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without l> imitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

#This script needs to be run on python >= 3.7.9

#This script will help configure the Zymbit module and the host pi
#to be secure and production ready. This will put the Zymbit module in
#production mode, set self-destruct policy for tamper detect, and load the
#essential boot files for supervised boot process. This will also sanitize the
#host device by mounting read-only filesystem, gen random strong passwords using
#pwgen for all /bin/bash users, disable root account login, disable SSH, and
#remove remote applications: CURL, WGET, GCC, APT, DPKG.

import zymkey
import subprocess
import os
import time

#---------------Utility Functions-----------------------------------------------
def run_shell_cmd(cmd : str, supress_stdout : bool = False):
    cmd_list = cmd.split(' ')
    if not supress_stdout:
        subprocess.run(cmd_list)
    else:
        subprocess.run(cmd_list, stdout=subprocess.DEVNULL)

def return_shell_cmd_output(cmd : str):
    cmd_list = cmd.split(' ')
    return subprocess.run(cmd_list, check = True, capture_output = True, text = True).stdout

def get_user_input_bool(display_str : str):
    response = input(display_str + " (Y/n): ").rstrip()
    response = response.lower()
    if response == 'y':
        return True
    return False

#-------------------------------------------------------------------------------
#--------------Zymbit CFG APIs--------------------------------------------------

def populate_manifest():
    # populate manifest with /boot
    print("Adding /boot files to manifest...")
    zymkey.client.add_or_update_supervised_boot_file(0, "bcm2711-rpi-cm4.dtb")
    zymkey.client.add_or_update_supervised_boot_file(0, "bootcode.bin")
    zymkey.client.add_or_update_supervised_boot_file(0, "cmdline.txt")
    zymkey.client.add_or_update_supervised_boot_file(0, "config.txt")
    try:
       zymkey.client.add_or_update_supervised_boot_file(0, "initrd.img")
    except:
       print("Failed to add intird.img. Check if file exists.\n")
    zymkey.client.add_or_update_supervised_boot_file(0, "kernel7l.img")
    zymkey.client.add_or_update_supervised_boot_file(0, "start4.elf")
    zymkey.client.add_or_update_supervised_boot_file(0, "zymbit_mac_address")
    zymkey.client.add_or_update_supervised_boot_file(0, "overlays/vc4-kms-v3d.dtbo")
    print("Done!\n")

def return_manifest():
    manifest = zymkey.client.get_supervised_boot_file_manifest()
    print("Manifest returned: %s \n" % manifest)

def set_perimeter_events():
    # Set channels 0/1 to self destruct
    print("Setting perimeter channels to self_destruct...")
    zymkey.client.set_perimeter_event_actions(0, True, True)
    time.sleep(10)
    zymkey.client.set_perimeter_event_actions(1, True, True)
    time.sleep(10)
    print("Done!\n")

def set_bind_lock():
    # Set Bind Lock. Warning! permanent
    lock_root = get_user_input_bool("Warning! Are you sure you want to set bind-lock (Permanent)?")
    if lock_root:
        print("Setting bind lock...")
        zymkey.client.lock_binding()
        print("Done!\n")
#-------------------------------------------------------------------------------
#----------------Host cfg APIs--------------------------------------------------
def mount_ro_fs():
    #Modify fstab to mount root fs as read-only
    modify_fstab_root = get_user_input_bool("Warning! This will modify fstab to mount root partition to ro")
    if modify_fstab_root:
        print("Modifying fstab for readonly filesystem...")
        fstab_string = return_shell_cmd_output("grep -w / /etc/fstab")
        fstab_string = fstab_string.rstrip()
        column_word = subprocess.run(['awk', '{print $4}'], check = True, input=fstab_string, capture_output = True, text = True).stdout
        column_word = column_word.rstrip()
        new_fstab_string = fstab_string.replace(column_word, "defaults,ro")
        cmd = "s@%s@%s@" % (fstab_string, new_fstab_string)
        subprocess.run(['sudo', 'sed', '-i', cmd, '/etc/fstab'])
        print("Done!\n")

    modify_fstab_boot = get_user_input_bool("Warning! This will modify fstab to mount boot partition to ro")
    if modify_fstab_boot:
        print("Modifying fstab for readonly filesystem...")
        fstab_string = return_shell_cmd_output("grep -w /boot /etc/fstab")
        fstab_string = fstab_string.rstrip()
        column_word = subprocess.run(['awk', '{print $4}'], check = True, input=fstab_string, capture_output = True, text = True).stdout
        column_word = column_word.rstrip()
        new_fstab_string = fstab_string.replace(column_word, "defaults,ro")
        cmd = "s@%s@%s@" % (fstab_string, new_fstab_string)
        subprocess.run(['sudo', 'sed', '-i', cmd, '/etc/fstab'])
        print("Done!\n")

def disable_root_acct():
    #Lock root account
    print("Disabling root account...")
    lock_root = get_user_input_bool("Warning! Are you sure you want to disable root account?")
    if lock_root:
        run_shell_cmd("sudo passwd -l root")
        print("Done!\n")

def disable_ssh():
    #Disable ssh service
    stop_ssh = get_user_input_bool("Warning! Are you sure you want to disable SSH access?")
    if stop_ssh:
        print("Disabling SSH...")
        run_shell_cmd("/etc/init.d/ssh stop")
        run_shell_cmd("update-rc.d ssh disable")
        print("Done!\n")

def gen_strong_user_pwds():
    #Get all users with /home privelages and change their passwords to pwgen -s -n 16 1
    #This excludes the user group 'zymbit' for normal operations.
    chg_pwds = get_user_input_bool("Warning! Are you sure you want to change passwords for all users?")
    if chg_pwds:
        print("Changing user passwords to strong passwords...")
        install_pwgen = get_user_input_bool("Update/Install Pwgen?")
        if install_pwgen:
            run_shell_cmd("apt install pwgen -y")
        users_list = subprocess.run(['awk', '-F', ':', '/home/ {print $1}', '/etc/passwd'], check = True, capture_output = True, text = True).stdout
        users_list = users_list.rsplit()
        for user in users_list:
            if (user != 'zymbit'):
                pwd = return_shell_cmd_output("pwgen -s -n 16 1")
                cmd = "%s:%s" % (user, pwd)
                subprocess.run(['sudo', 'chpasswd'], input=cmd, text = True)
                print("%s password changed to : %s" % (user, pwd))
        print("Done!\n")

def remove_apps():
    #This uninstalls CURL, WGET, GCC, APT, DPKG from the host system.
    delete_curl = get_user_input_bool("Warning! Are you sure you want to uninstall CURL?")
    if delete_curl:
        print("Removing CURL...")
        run_shell_cmd("apt-get remove curl -y")
        print("Done!\n")

    delete_wget = get_user_input_bool("Warning! Are you sure you want to uninstall WGET?")
    if delete_wget:
        print("Removing WGET...")
        run_shell_cmd("apt-get remove wget -y --allow-remove-essential")
        print("Done!\n")

    delete_gcc = get_user_input_bool("Warning! Are you sure you want to uninstall GCC?")
    if delete_gcc:
        print("Removing GCC...")
        run_shell_cmd("apt-get purge gcc -y --allow-remove-essential")
        subprocess.run(['rm -rf /usr/bin/gcc*'], shell=True)
        print("Done!\n")

    delete_apt = get_user_input_bool("Warning! Are you sure you want to uninstall APT?")
    if delete_apt:
        print("Removing APT...")
        run_shell_cmd("apt-get purge apt -y --allow-remove-essential")
        print("Done!\n")

    delete_dpkg = get_user_input_bool("Warning! Are you sure you want to uninstall DPKG?")
    #If Apt is deleted before dpkg, delete all dpkg binaries from /usr/bin
    if delete_dpkg and delete_apt:
        print("Removing DPKG...")
        subprocess.run(['rm -rf /usr/bin/dpkg*'], shell=True)
        print("Done!\n")
    elif delete_dpkg:
        print("Removing DPKG...")
        run_shell_cmd("apt-get purge dpkg -y --allow-remove-essential")
        print("Done!\n")

#-------------------------------------------------------------------------------
#-------------------Main--------------------------------------------------------
if __name__ == "__main__":

    #Check if script has root privelages
    if os.geteuid() != 0:
        exit("You need to run this script as sudo")

    #Ask user for what features to set/sanitize
    load_manifest = get_user_input_bool("Load file manifest (Alpha edition)")
    set_perimeter_events = get_user_input_bool("Set perimeter events to self-destruct")
    set_bindlock = get_user_input_bool("Set bind lock? (Warning! permanent)")
    read_only_fs = get_user_input_bool("Mount filesystem persistently as read-only on next boot")
    gen_strong_pwds = get_user_input_bool("Generate random strong passwords for user accounts using pwgen")
    remove_remote_app_access = get_user_input_bool("Remove CURL, WGET, GCC, APT, DPKG?")
    disable_root = get_user_input_bool("Disable root account login?")
    disable_ssh = get_user_input_bool("Disable SSH")

    #Perform the operations
    if load_manifest:
        try:
            populate_manifest()
            return_manifest()
        except:
            print("Exception! Failed to load file manifest!")

    if set_perimeter_events:
        try:
            set_perimeter_events()
        except:
            print("Exception! Failed to set perimeter events")

    if set_bindlock:
        try:
            set_bind_lock()
        except:
            print("Exception! Failed to set bind lock")

    if read_only_fs:
        try:
            mount_ro_fs()
        except:
            print("Exception! Failed to modify fstab to read-only")

    if gen_strong_pwds:
        try:
            gen_strong_user_pwds()
        except:
            print("Exception! Failed to set strong passwords")

    if remove_remote_app_access:
        try:
            remove_apps()
        except:
            print("Exception! Failed to remove apps")

    if disable_root:
        try:
            disable_root_acct()
        except:
            print("Exception! Failed to disable root account")

    if disable_ssh:
        try:
            disable_ssh()
        except:
            print("Exception! Failed to disable SSH")
#-------------------------------------------------------------------------------
