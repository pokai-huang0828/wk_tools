#!/bin/bash
#
# Set up and Start UDCluster Daemon Server locally on Linux.
# Usage: sudo ./setup_mh_local.sh <--options>
#
# If you are trying to connect to STAGING release server, please specify daemon
# server param --daemon_env=STAGING.

readonly USAGE="\
Usage: setup_mh_local.sh [SETUP_OPTIONS]

Please follow the order here to append SETUP_OPTIONS.

SETUP_OPTIONS
  --current_user=USER  The user account to run this script. Mainly use to run
                       non-root commands. Use the login user if not set.
  --run_as=USER:       [Optional]Start the UDCluster server as USER. This USER
                       will be created if inexistent on this lab. If not set,
                       the current user will be used.
  --daemon_env=ENV:    [Optional] ENV need to be one of PROD/STAGING/INTEGRATION
                       /DEV. Default value: PROD.
  --lab_type=TYPE:     [Optional] Lab type of this lab. Should be one of
                       MH_SATELLITE_LAB/MH_ATE_LAB/MH_SATELLITE_FACTORY_PROXIED.
                       Default value: MH_SATELLITE_LAB.
                       Please contact mobileharness-eng before specify this param.
"

readonly RES_DIR='/tmp/lab_setup'

if [[ "$1" == "-h" || "$1" == "--help" ]] ; then
  echo -n "$USAGE"
  exit 1
fi

current_user="$(logname)"
if [[ "$1" =~ ^-*current_user= ]]; then
  current_user="${1#*-current_user=}"
  shift
fi
echo "current_user: ${current_user}"

run_as="${current_user}"
if [[ "$1" =~ ^-*run_as= ]]; then
  run_as="${1#*-run_as=}"
  shift
fi
echo "run_as: ${run_as}"

daemon_env=PROD
if [[ "$1" =~ ^-*daemon_env= ]]; then
  daemon_env="${1#*-daemon_env=}"
  shift
fi
echo "daemon_env: ${daemon_env}"

lab_type=MH_SATELLITE_LAB
if [[ "$1" =~ ^-*lab_type= ]]; then
  lab_type="${1#*-lab_type=}"
  shift
fi
echo "lab_type: ${lab_type}"

if [[ ! -d  "${RES_DIR}" ]]; then
  echo "Directory - ${RES_DIR} doesn't exist. Fail to move forward. Exit!"
  exit 1
fi
cd "${RES_DIR}"

echo "================================"
echo "Add Execution Permission to Scripts"
chmod +x setup_udcluster_linux_server.sh

echo "================================"
echo "Prepare 70-android.rules"
mkdir -p /etc/udev/rules.d
cp -f 70-android.rules /etc/udev/rules.d/70-android.rules
chmod a+r /etc/udev/rules.d/70-android.rules
service udev restart
udevadm trigger

echo "================================"
echo "Remove previous udcluster directory for a clean start"
sudo rm -rf /usr/local/google/udcluster

echo "================================"
echo "Install Google JDK and GRTE"
sudo dpkg -i jdk21-google*.deb
sudo dpkg -i grtev5*.deb

# Create a symlink to jdk21
sudo rm -f /usr/local/buildtools/java/jdk
sudo ln -sfn /usr/local/buildtools/java/jdk21 /usr/local/buildtools/java/jdk

echo "================================"
echo "Dump Google JDK version"
/usr/local/buildtools/java/jdk/bin/java -version
if [[ $? != 0 ]]; then
  echo "Failed to print Google JDK version. Exit!"
  exit 1
fi

echo "================================"
echo "Configure NTP service"
sudo apt-get -y install ntp
if ! grep -q "time1.google.com" "/etc/ntp.conf"; then
  cat << EOF >> /etc/ntp.conf

# Extra NTP servers
server time.google.com
server time1.google.com
server time2.google.com
EOF
  sudo service ntp restart
  sudo ntpq -p
fi

echo "================================"
echo "Start Daemon Server"
sudo ./setup_udcluster_linux_server.sh setup --force_run_as="${run_as}" --daemon_env="${daemon_env}" --lab_type="${lab_type}"