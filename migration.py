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

target_zone_name = 'gcpHydroshareZone'

target_zone_name = 'otherZone'

############

delay_condition = '<PLUSET>{0}s</PLUSET><INST_NAME>irods_rule_engine_plugin-{1}-instance</INST_NAME>'

############

# Enqueue a sync for each file newer than X seconds
def migration_sync_all_files_newer_than_x_seconds(rule_args, callback, rei):
    global delay_condition
    global target_zone_name
    try:
        seconds_ago = rule_args[0]
    except IndexError:
        seconds_ago = 86400 # default, 1 day
    epoch_seconds_for_genquery = '0'+str(int(time.time() - int(seconds_ago)))
    callback.writeLine('serverLog', 'seconds_ago [{0}]'.format(seconds_ago))
    for result in row_iterator("COLL_NAME, DATA_NAME",
                               "DATA_MODIFY_TIME > '{0}' and DATA_NAME NOT LIKE '%.zip'".format(epoch_seconds_for_genquery),
                               AS_LIST,
                               callback):
        path_to_sync = '{0}/{1}'.format(result[0], result[1])
        parts = path_to_sync.split('/')
        parts[1] = target_zone_name
        target_path = '/'.join(parts)
        ruletext = 'callback.msiDataObjRsync("{0}", "IRODS_TO_IRODS", "null", "{1}", 0);'.format(path_to_sync, target_path)
        callback.writeLine('serverLog', 'queuing data object [{0}]'.format(ruletext))
        callback.delayExec(delay_condition.format('1', 'python'), ruletext, '')
