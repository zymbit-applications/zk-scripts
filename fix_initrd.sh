#!/usr/bin/bash

# Script to update SCM Alpha initrd.img to make sure salt file matches rootfs salt file.
# Mis-match caused by updating MAC address in rootfs but not in updateinitramfs process.
# Updating salt file, adding MAC address and hooks to zk_get_key to make consistent.
# If salt files differed, once bind locked initrd could not unlock LUKS encryption.

ORIG_IMG="/boot/initrd.img"
DST_DIR="/tmp/initrd_dir"

echo "Save a copy of $ORIG_IMG ..."
cp $ORIG_IMG $ORIG_IMG.save

echo "Unpack $ORIG_IMG to $DST_DIR ..."
unmkinitramfs $ORIG_IMG $DST_DIR

echo "Copy zymbit_mac_address to image..."
cp /boot/zymbit_mac_address $DST_DIR/etc

echo "Update zk_get_key..."
cat > $DST_DIR/usr/lib/cryptsetup/scripts/zk_get_key << "EOF"
        #!/bin/sh

        num_times=30
        while [ ${num_times} -gt 0 ]
        do
                ls /sys/class/net/eth* 1>/dev/null 2>&1
                eth=$?
                ls /sys/class/net/enx* 1>/dev/null 2>&1
                enx=$?
                if [ ${eth} -ne 0 ] && [ ${enx} -ne 0 ]
                then
                        num_times=$((num_times-1))
                        sleep 0.1
                else
                        break
                fi
        done

        if [ -e "/etc/zymbit_mac_address" ]
        then
                eth_mac=$(head -n 1 /etc/zymbit_mac_address)
                wlan_mac=$(tail -n 1 /etc/zymbit_mac_address)
                ip link set eth0 down 1>/dev/null 2>&1
                ip link set eth0 address $eth_mac 1>/dev/null 2>&1
                ip link set eth0 up 1>/dev/null 2>&1
                ip link set wlan0 down 1>/dev/null 2>&1
                ip link set wlan0 address $wlan_mac 1>/dev/null 2>&1
                ip link set wlan0 up 1>/dev/null 2>&1
        else
                break
        fi

        while [ 1 ]
        do
                if [ -d "/var/lib/zymbit" ]
                then
                        break
                else
                        sleep 0.1
                fi
        done

        if [ -e /var/lib/zymbit/zkenv.conf ]
        then
                export $(cat /var/lib/zymbit/zkenv.conf)
        fi
        /sbin/zkunlockifs /var/lib/zymbit/key.bin.lock
EOF

echo "Copy salt file from rootfs to image..."
salt_file=`find /var/lib/zymbit -name s1_fp_salt.bin`
echo "md5sum of orig salt file on rootfs: "
md5sum ${salt_file}
echo "md5sum of orig salt file in image: "
md5sum ${DST_DIR}${salt_file}

cp $salt_file ${DST_DIR}${salt_file}
echo "md5sum of updated salt file in image: "
md5sum ${DST_DIR}${salt_file}

echo "Repack $ORIG_IMG ..."
cd $DST_DIR; find . | cpio --quiet -H newc -o | gzip -9 -n > /boot/initrd.img

echo "Update $ORIG_IMG in manifest ..."
python3 -c "import zymkey; zymkey.client.add_or_update_supervised_boot_file('initrd.img')"

echo "Done."

