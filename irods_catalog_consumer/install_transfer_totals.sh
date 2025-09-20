#! /bin/bash -e

######
# 1. chmod +x msiExecCmd_bin/add_transfer.sh

cat << 'EOF' > /var/lib/irods/msiExecCmd_bin/add_transfer.sh
#!/bin/bash

USER_ID="$1"
ACTION="$2"
BYTES="$3"

# this does not yet handle the rollover at each exbibyte
PGPASSWORD=testpassword psql ICAT -h irods-catalog -c " \
  INSERT INTO R_TRANSFER_TOTALS (user_id, action, exbibytes, bytes) \
  VALUES (${USER_ID}, '${ACTION}', 0, ${BYTES}) \
  ON CONFLICT (user_id, action) DO UPDATE SET \
    exbibytes = R_TRANSFER_TOTALS.exbibytes + EXCLUDED.exbibytes, \
    bytes = R_TRANSFER_TOTALS.bytes + EXCLUDED.bytes; \
"
EOF
chmod +x /var/lib/irods/msiExecCmd_bin/add_transfer.sh

######
# 2. add PEPs to core.re

ed -s /etc/irods/core.re << EOF
0a
add_transfer(*user, *direction, *bytes){
  *query = "select USER_ID where USER_NAME = '*user'";
  msiExecStrCondQuery(*query, *res);
  foreach(*res) {*userid = *res.USER_ID};
  *theargs = "*userid *direction *bytes";
  msiExecCmd("add_transfer.sh", *theargs, "null", "null", "null", *result);
}

pep_api_data_obj_write_post(*INSTANCE_NAME, *COMM, *DATAOBJWRITEINP, *BUFFER) {
  add_transfer(*COMM.user_user_name, 'in', *DATAOBJWRITEINP.len);
}

pep_api_data_obj_read_post(*INSTANCE_NAME, *COMM, *DATAOBJREADINP, *BUFFER) {
  add_transfer(*COMM.user_user_name, 'out', *DATAOBJREADINP.len);
}

pep_api_data_obj_put_post(*INSTANCE_NAME, *COMM, *DATAOBJINP, *BUFFER, *PORTAL_OPR_OUT) {
  add_transfer(*COMM.user_user_name, 'in', *DATAOBJINP.data_size);
}

pep_api_data_obj_get_post(*INSTANCE_NAME, *COMM, *DATAOBJINP, *BUFFER, *PORTAL_OPR_OUT) {
  add_transfer(*COMM.user_user_name, 'out', *DATAOBJINP.data_size);
}

.
w
q
EOF
