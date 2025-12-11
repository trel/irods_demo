import os
from irods.session import iRODSSession
with iRODSSession(host='localhost', port=2247, user='rods', password='rods', zone='tempZone') as session:
    # create large file
    localfile = "bigfile"
    with open(localfile, "ab") as f:
      f.truncate(35 * 1024 * 1024)

    # confirm connectivity
    home_collection = "/tempZone/home/rods"
    coll = session.collections.get(home_collection)
    print(coll.id)

    # send it
    remotefile = f"{home_collection}/{localfile}"
    session.data_objects.put(localfile, remotefile)

    # get it
    localfile2 = f"{localfile}2"
    session.data_objects.get(remotefile, localfile2)

    # clean up
    session.data_objects.unlink(remotefile)
    os.unlink(localfile)
    os.unlink(localfile2)
