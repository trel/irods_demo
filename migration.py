#################################
# add this one line to core.py
#################################
#
# from migration import *
#
#################################

import time
from genquery import *

############

renci_collection = '/hydroshareZone/home/public'
gcp_collection = '/gcpHydroshareZone/home/public'

renci_collection = '/tempZone/home/public'
gcp_collection = '/otherZone/home/public'

############

delay_condition = '<PLUSET>{0}s</PLUSET><INST_NAME>irods_rule_engine_plugin-{1}-instance</INST_NAME>'

############

# Add one rule to the delay queue, and run it periodically, forever
def migration_add_sweeper_to_queue(rule_args, callback, rei):
    global delay_condition
    ruletext = 'callback.migration_sync_all_hydroshare_resources();'
    print('queuing sweeper', ruletext)
    callback.delayExec(delay_condition.format('86400', 'python')+'<EF>REPEAT FOR EVER</EF>', ruletext, '')

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
        callback.delayExec(delay_condition.format('1', 'python'), ruletext, '')

# Enqueue the sync of a single resource upon request
def migration_sync_single_hydroshare_resource(rule_args, callback, rei):
    global delay_condition
    global gcp_collection
    path_to_sync = rule_args[0]
    hydroshare_resource_name = path_to_sync.split('/')[-1]
    ruletext = 'callback.msiCollRsync("{0}", "{1}", "null", "IRODS_TO_IRODS", 0);'.format(path_to_sync, gcp_collection+"/"+hydroshare_resource_name)
    print('queuing single resource', ruletext)
    callback.delayExec(delay_condition.format('1', 'python'), ruletext, '')

# Enqueue a sync for each file newer than X seconds
def migration_sync_all_files_newer_than_x_seconds(rule_args, callback, rei):
    global delay_condition
    global gcp_collection
    try:
        seconds_ago = rule_args[0]
    except IndexError:
        seconds_ago = 86400 # default, 1 day
    epoch_seconds_for_genquery = '0'+str(int(time.time() - int(seconds_ago)))
    callback.writeLine('serverLog', 'seconds_ago [{0}]'.format(seconds_ago))
    for result in row_iterator("COLL_NAME, DATA_NAME",
                               "DATA_MODIFY_TIME > '{0}'".format(epoch_seconds_for_genquery),
                               AS_LIST,
                               callback):
        path_to_sync = '{0}/{1}'.format(result[0], result[1])
        parts = path_to_sync.split('/')
        parts[1] = gcp_collection.split('/')[1]
        target_path = '/'.join(parts)
        ruletext = 'callback.msiDataObjRsync("{0}", "IRODS_TO_IRODS", "null", "{1}", 0);'.format(path_to_sync, target_path)
        callback.writeLine('serverLog', 'queuing data object [{0}]'.format(ruletext))
        callback.delayExec(delay_condition.format('1', 'python'), ruletext, '')
