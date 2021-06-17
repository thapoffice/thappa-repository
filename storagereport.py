# seed.py
import random
import json
import yaml
import sys
from tabulate import tabulate

from datetime import datetime, timezone

from bm4gcpStatedbClient.models import *


def printUsage():
    print("cliShowStorageUsage datacenter")

if len(sys.argv) !=2 :
    printUsage()
    exit()

datacenter = sys.argv[1]

dc = DataCenter.get_by_attr("code", datacenter)[0]
netappclusters = (NetAppCluster.get_collection('where=dataCenter=="{}"'.format(dc._id)) or [])
workorders = WorkOrder.all()
accounts = Account.all()

for netappcluster in netappclusters:
    print("Netapp Cluster: " + netappcluster.name)
    
    netappnodes = (NetAppNode.get_collection('where=netappCluster=="{}"'.format(netappcluster._id)) or [])
    for node in netappnodes:
        netappaggregates = (NetAppAggregate.get_collection('where=netappNode=="{}"'.format(node._id)) or [])
        for aggr in netappaggregates:

            print("\tAggregate " + aggr.name + " on node " + node.name)
            svs = (StorageVolume.get_collection('where=netappAggregate=="{}"'.format(aggr._id)) or [])
            totalAllocated = 0
            totalReserved = 0
            
            data = []
            for sv in svs:
                wo = [x for x in workorders if x._id == sv.provisionedByWorkOrder]
                if len(wo)>0:
                    workorder = wo[0].name
                else:
                    workorder = ""
                account = [x for x in accounts if x._id == sv.accountId][0].accountId
                d = { "Name" : sv.name, "Status" : sv.status, "SizeGB" : sv.sizeGb, "ReservedSizeGB" : sv.reservedSizeGb, "Workorder" : workorder, "accountID" : account }
                data.append(d)
                totalAllocated = totalAllocated + sv.sizeGb
                totalReserved = totalReserved + sv.reservedSizeGb

            print("\t" + tabulate(data, headers="keys").replace("\n", "\n\t"))

            print("\tTOTAL: Size: " + str(aggr.sizeGb) + " Allocated: " + str(totalAllocated) + "GB Reserved: " + str(totalReserved) + "GB Remaining:" + str(aggr.sizeGb - totalReserved) + "GB")
            print()

