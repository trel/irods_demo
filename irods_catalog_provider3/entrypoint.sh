#! /bin/bash -e

catalog_db_hostname=irods-catalog

echo "Waiting for iRODS catalog database to be ready"

until pg_isready -h ${catalog_db_hostname} -d ICAT -U irods -q
do
    sleep 1
done

echo "iRODS catalog database is ready"

unattended_install_file=/unattended_install.json
if [ -e "${unattended_install_file}" ]; then
    echo "Running iRODS setup"
    sed -i "s/THE_HOSTNAME/${HOSTNAME}/g" ${unattended_install_file}

    python3 /var/lib/irods/scripts/setup_irods.py --json_configuration_file ${unattended_install_file}
    rm ${unattended_install_file}

    echo "Installing transfer totals script"
    su - irods -c 'bash /install_transfer_totals.sh'

    echo "Initializing server"
    su - irods -c 'irodsServer -d'

    # wait for server to respond
    until nc -z irods-catalog-provider 1247
    do
        sleep 1
    done

    # kill server and wait for it to stop
    kill $(cat /var/run/irods/irods-server.pid)
    while ps -p $(cat /var/run/irods/irods-server.pid) ; do
        sleep 1
    done
fi

echo "Starting server"
cd /usr/sbin
su irods -c 'irodsServer --stdout'
