#!/bin/python2
import gc
import itertools
import random
import timeit
from multiprocessing import Pool
from random import random
from random import seed

from osmdata import GraphBuilder
from persistence import persist_write
from settings import settings
from simulation import Simulation
from tripgenerator import TripGenerator

global MasterStreets4MultiProcessing

core_count = settings["cpu_count"]


# create Street4Serial objects for each process to use
class Streets4MultiProcessing(object):

    def __init__(self, proc_id=None, num_residents=100):
        self.proc_id = proc_id
        self.log("Setting number_of_residents to {}".format(num_residents))
        self.number_of_residents = num_residents
        random_seed = settings["random_seed"] + (37)
        seed(random_seed)

        self.log("Reading OpenStreetMap data...")
        data = GraphBuilder(settings["osm_file"])

        self.log("Building street network...")
        street_network = data.build_street_network()

        self.log("Locating area types...")
        data.find_node_categories()

        self.log("Generating trips...")
        trip_generator = TripGenerator()

        if settings["use_residential_origins"]:
            potential_origins = data.connected_residential_nodes
        else:
            potential_origins = street_network.get_nodes()
        potential_goals = data.connected_commercial_nodes | data.connected_industrial_nodes
        trips = trip_generator.generate_trips(self.number_of_residents, potential_origins, potential_goals)
        self.log("Number of trips is " + str(len(trips)))

        #         # print("Number of trips is {}".len(trips))
        # set traffic jam tolerance for this process and its trips
        jam_tolerance = random()
        self.log("Setting traffic jam tolerance to", str(round(jam_tolerance, 2)) + "...")

        # run simulation
        self.simulation = Simulation(street_network, trips, jam_tolerance, self.log_indent)

    def log(*output):
        pass
        # if settings["logging"] == "stdout":

    #         #     print "[ %s ]" % (datetime.now()),
    #     for o in output:
    #         #         print o,
    #         #     print ""

    def log_indent(*output):
        pass
        # if settings["logging"] == "stdout":


#         #     print "[ %s ]" % (datetime.now()),
#     for o in output:
#         #         print o,
#         #     print ""


# slave function
ProcessObjects = []
residents = settings["number_of_residents"]
process_chunks = []
residents = settings["number_of_residents"]
if residents % core_count != 0:
    remainder = residents % core_count
    proc_chunk_count = residents / core_count
    for x in range(core_count):
        process_chunks.append(proc_chunk_count)
    process_chunks[-1] = proc_chunk_count + remainder
else:
    # evenly divisible
    proc_chunk_count = residents / core_count
    for x in range(core_count):
        process_chunks.append(proc_chunk_count)

for core in range(core_count):
    # print("Creating global obj {}".format(core))
    test = Streets4MultiProcessing(num_residents=process_chunks[core])
    ProcessObjects.append(test)


def process_job(num_residents):
    global ProcessObjects
    # print "Processing {} residents in process {}".format(num_residents[0], num_residents[1])
    # retrieve global object from array
    try:
        #         # print "Retrieving object from global array"
        #         # print("Num processobjects = {}".format(len(ProcessObjects)))
        local_streets4multi = ProcessObjects[num_residents[1] - 1]
        #         # print "Setting number of residents"
        #         # print(num_residents)
        local_streets4multi.number_of_residents = int(num_residents[0])
        local_streets4multi.log("Running simulation step", num_residents[2] + 1, "of",
                                str(settings["max_simulation_steps"]) + "...")

        local_streets4multi.simulation.step()
        # print("Traffic load after step = {}".format(len(local_streets4multi.simulation.traffic_load)))
        return len(local_streets4multi.simulation.traffic_load)
    except Exception as e:
        #         # print "{}".format(str(e))
        return num_residents[0]


def log(*output):
    pass
    # if settings["logging"] == "stdout":


#     #     print "[ %s ]" % (datetime.now()),
#     for o in output:
#     #         print o,
#     #     print ""


def log_indent(*output):
    pass
    # if settings["logging"] == "stdout":


#     #     print "[ %s ]" % (datetime.now()),
#     for o in output:
#     #         print o,
#     #     print ""


def generate_base_street_network():
    # set random seed based on process rank
    log("Generating base street network file")
    random_seed = settings["random_seed"] + (37)
    seed(random_seed)
    data = GraphBuilder(settings["osm_file"])
    street_network = data.build_street_network()
    persist_write("street_network_1.s4multiprocessing", street_network)
    log("Done generating base street network file")


def main():
    # Check to see if persist_traffic_load
    if settings["persist_traffic_load"]:
        generate_base_street_network()

    global MasterStreets4MultiProcessing
    # Set master object reference for each process to deep copy
    MasterStreets4MultiProcessing = Streets4MultiProcessing()

    # Only set as large as many real cores on system (hyper-threaded in intel)
    pool = Pool(processes=core_count)
    proc_chunks = []
    residents = settings["number_of_residents"]
    if residents % core_count != 0:
        remainder = residents % core_count
        proc_chunk_count = residents / core_count
        for x in range(core_count):
            proc_chunks.append(proc_chunk_count)
        proc_chunks[-1] = proc_chunk_count + remainder
    else:
        # evenly divisible
        proc_chunk_count = residents / core_count
        for x in range(core_count):
            proc_chunks.append(proc_chunk_count)
    # print "Each process will process {} residents".format(proc_chunks)

    # calculate chunks to process
    for step in range(settings["max_simulation_steps"]):
        # process a chunk on a process
        # returns an array
        results = pool.map(process_job, itertools.izip(proc_chunks, range(len(proc_chunks)), itertools.repeat(step)))
        # results = pool.map(process_job, proc_chunks)
    #         # print "Step {} resulted -> {}".format(step, results)

    total = 0
    for obj in gc.get_objects():
        if isinstance(obj, Streets4MultiProcessing):
            total += 1


#     # print "Simulation object instances left: {}".format(total)


# master process entry logic
if __name__ == '__main__':
    print "Running . . ."
    print "Time was {} with {} residents and {} sub-processes".format(timeit.timeit(stmt=main, number=1),settings["number_of_residents"], core_count)
