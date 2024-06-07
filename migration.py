from genquery import *

############

renci_collection = '/hydroshareZone/home/public'
gcp_collection = '/gcpHydroshareZone/home/public'

renci_collection = '/tempZone/home/public'
gcp_collection = '/otherZone/home/public'

############

delay_condition = '<PLUSET>1s</PLUSET><INST_NAME>irods_rule_engine_plugin-{0}-instance</INST_NAME>'

############

# Add one rule to the delay queue, and run it periodically, forever
def migration_add_sweeper_to_queue(rule_args, callback, rei):
    global delay_condition
    ruletext = 'callback.migration_sync_all_hydroshare_resources();'
    print('queuing sweeper', ruletext)
    callback.delayExec(delay_condition.format('python')+'<EF>REPEAT FOR EVER</EF>', ruletext, '')

# Enqueue a sync for each hydroshare resource (all of them)
def migration_sync_all_hydroshare_resources(rule_args, callback, rei):
    global delay_condition
    global renci_collection
    global gcp_collection
    for result in row_iterator("COLL_NAME",
                               "COLL_NAME like '{0}/%'".format(renci_collection),
                               AS_LIST,
                               callback):
        path_to_sync = result[0]
        hydroshare_resource_name = path_to_sync.split('/')[-1]
        ruletext = 'callback.msiCollRsync("{0}", "{1}", "null", "IRODS_TO_IRODS", 0);'.format(path_to_sync, gcp_collection+"/"+hydroshare_resource_name)
        print('queuing resource', ruletext)
        callback.delayExec(delay_condition.format('python'), ruletext, '')

# Enqueue the sync of a single resource upon request
def migration_sync_single_hydroshare_resource(rule_args, callback, rei):
    global delay_condition
    global gcp_collection
    path_to_sync = rule_args[0]
    hydroshare_resource_name = path_to_sync.split('/')[-1]
    ruletext = 'callback.msiCollRsync("{0}", "{1}", "null", "IRODS_TO_IRODS", 0);'.format(path_to_sync, gcp_collection+"/"+hydroshare_resource_name)
    print('queuing single resource', ruletext)
    callback.delayExec(delay_condition.format('python'), ruletext, '')

