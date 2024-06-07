cd
jq '.federation += [
    {
        "catalog_provider_hosts": ["irods-catalog-provider"],
        "negotiation_key": "_____32_byte_pre_shared_key_____",
        "zone_key": "TEMPORARY_ZONE_KEY",
        "zone_name": "tempZone",
        "zone_port": 1247
    }
]
' /etc/irods/server_config.json > new.json
cp new.json /etc/irods/server_config.json
iadmin mkzone tempZone remote irods-catalog-provider:1247
iadmin mkuser rods#tempZone rodsuser
