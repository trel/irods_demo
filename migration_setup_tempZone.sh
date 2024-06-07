cd
jq '.federation += [
    {
        "catalog_provider_hosts": ["other-catalog-provider"],
        "negotiation_key": "_____32_byte_pre_shared_key_____",
        "zone_key": "TEMPORARY_ZONE_KEY",
        "zone_name": "otherZone",
        "zone_port": 1247
    }
]
' /etc/irods/server_config.json > new.json
cp new.json /etc/irods/server_config.json
iadmin mkzone otherZone remote other-catalog-provider:1247
jq '.plugin_configuration.rule_engines |= [
    {
        "instance_name": "irods_rule_engine_plugin-python-instance",
        "plugin_name": "irods_rule_engine_plugin-python",
        "plugin_specific_configuration": {}
    }
] + .
' /etc/irods/server_config.json > new.json
cp new.json /etc/irods/server_config.json
irule -r irods_rule_engine_plugin-python-instance migration_add_sweeper_to_queue null null
