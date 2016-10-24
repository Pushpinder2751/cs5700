# os.system("python nstrace.py")
import os
import sys
import nstrace
import csv

# name the nodes correctly to remove confusion
n1 = 0
n2 = 1
n3 = 2
n4 = 3
n5 = 4
n6 = 5

# n1                              n4
#   \                            /
#     \                        /
#       \                    /
#         n2 - - - - - - - n3
#       /                     \
#     /                         \
#   /                             \
# n5                               n5

# trace events and their meanings :
# r : received
# d : dropped
# + : enqueued
# - : dropped

# to make code readable
class Trace_event:
    def __init__(self, my_tuple):
        (event_1, time_2, send_node_3, dest_node_4, pkt_type_5, pkt_size_6,
        flags_7, fid_8, src_addr_9, dst_addr_10, seq_num_11, pkt_id_12) = my_tuple
        self.event_1 = event_1
        self.time_2 = time_2
        self.send_node_3 = send_node_3
        self.dest_node_4 = dest_node_4
        self.pkt_type_5 = pkt_type_5
        self.pkt_size_6 = pkt_size_6
        self.flags_7 = flags_7
        self.fid_8 = fid_8
        self.src_addr_9 = src_addr_9
        self.dst_addr_10 = dst_addr_10
        self.seq_num_11 = seq_num_11
        self.pkt_id_12 = pkt_id_12


class Trace_var:
    def __init__(self, my_tuple):
        (time_1, send_node_2, send_port_3, dest_node_4, dest_port_5,
        tr_var_name_6, tr_var_value_7) = my_tuple
        self.time_1 = time_1
        self.send_node_2 = send_node_2
        self.send_port_3 = send_port_3
        self.dest_node_4 = dest_node_4
        self.dest_port_5 = dest_port_5
        self.tr_var_name_6 = tr_var_name_6
        self.tr_var_value_7 = tr_var_value_7



print "this works"

# network throughput is the amount of data moved successfully
# from one place to another in a given time period, and typically
# measured in bits per second (bps), as in megabits per second (Mbps)
# or gigabits per second (Gbps)
def get_throughput(TCP_variant, CBR_rate):
    FLOW = 1 # fid assumed to start at 1
    pkt_count_sent_n1 = 0
    pkt_count_recvd_n4 = 0
    pkt_count_recvd_size = 0
    # this will change when we find a lower start time
    start_time = 10.0;
    # this will change when we find a higher end time
    end_time = 0.0

    recvd_size = 0


    filename = "trace_files/1_exp/" + TCP_variant + "_output_at_" + CBR_rate + ".tr"
    print filename
    nstrace.nsopen(filename)
    while not nstrace.isEOF():
        if nstrace.isEvent():

            # (event_1, time_2, send_node_3, dest_node_4, pkt_type_5, pkt_size_6,
            # flags_7, fid_8, src_addr_9, dst_addr_10, seq_num_11, pkt_id_12) = nstrace.getEvent()

            # get the tuple and send it to class
            trace = Trace_event(nstrace.getEvent())

            # since this is the only flow we care about in this experiment
            if trace.fid_8 == FLOW:
                if trace.event_1 == "+" and trace.send_node_3 == n1:
                    pkt_count_sent_n1 = pkt_count_sent_n1 + 1
                    # set start time for the tcp data, should happen only once
                    if trace.time_2 < start_time:
                        start_time = trace.time_2

                elif trace.event_1 == "r" and trace.dest_node_4 == n4:
                    pkt_count_recvd_n4 = pkt_count_recvd_n4 + 1
                    pkt_count_recvd_size = pkt_count_recvd_size + trace.pkt_size_6

                # to Calculate the end time
                elif trace.event_1 == "r" and trace.dest_node_4 == n1:
                    if trace.time_2 > end_time:
                        end_time = trace.time_2

        # # will do this later if needed
        # # can check cwnd, maxswq, ack etc
        # else if nstrace.isVar():
        #     # (time_1, send_node_2, send_port_3, dest_node_4, dest_port_5,
        #     # tr_var_name_6, tr_var_value_7) = nstrace.getVar()
        #
        #     # get the tuple and send to class
        #     var = Trace_var(nstrace.getVar())
        #
        #
        else:
            nstrace.skipline()

    nstrace.nsclose()

    # can and should use Trace_var ack_
    # print "packets sent by n1 : ", pkt_count_sent_n1
    # print "packets recvd by n4 : ", pkt_count_recvd_n4
    # print "total size recvd at n4: ", pkt_count_recvd_size
    # # size is usually in bits/s etc
    # print "precieved throughput in Mbps: ", ((pkt_count_recvd_size * 8 )/ (end_time - start_time)) / (1000 * 1000)
    return ((pkt_count_recvd_size * 8 )/ (end_time - start_time)) / (1000 * 1000)


# measured as the time required for a packet to be returned to its sender
# Here I will measure it by time the paket was sent from node1 to the time n1
# receives it acknowledgement

# It is possible to calculate the latency in the throughput function itself
# However, It will make the function very messy and unclean
# can also be refered to as avg. delay in the system
def get_latency(TCP_variant, CBR_rate):
    FLOW = 1 # fid assumed to start at 1

    start_time = {}
    end_time = {}

    # avg. delay / latency = totaly_duration / total_packets * 1000 (millisesonds)
    total_duration = 0.0
    total_packets = 0

    max_delay = 0;
    min_delay = 1000;

    filename = "trace_files/1_exp/" + TCP_variant + "_output_at_" + CBR_rate + ".tr"
    nstrace.nsopen(filename)

    while not nstrace.isEOF():
        if nstrace.isEvent():


            # get the tuple and send it to class
            trace = Trace_event(nstrace.getEvent())
            # since we have only one flow we care about
            if trace.fid_8 == FLOW:
                if trace.event_1 == "+" and trace.send_node_3 == n1:
                    seq_stamp = {trace.seq_num_11 : trace.time_2}
                    start_time.update(seq_stamp)

                # end to end latency is a synonym for RTT
                elif trace.event_1 == "r" and trace.dest_node_4 == n1:
                    seq_stamp = {trace.seq_num_11 : trace.time_2}
                    end_time.update(seq_stamp)

        else:
            nstrace.skipline()

    nstrace.nsclose()


    # print "start_time", start_time
    # print "end_time", end_time

    # calculate latency here
    for seq_stamp in start_time:
        if seq_stamp in end_time:
            latency = end_time[seq_stamp] - start_time[seq_stamp]
            # checking for false data
            if latency > 0:
                total_duration += latency
                total_packets += 1
                if latency > max_delay:
                    max_delay = latency
                if latency < min_delay:
                    min_delay = latency

    # print "total_packets : ", total_packets
    # print "start_time length : ", len(start_time)
    # print "end_time length : ", len(end_time)
    # print "latency in ms : ", ((float)(total_duration) / (float)( total_packets )) * 1000
    # print "max latency in ms", max_delay * 1000
    # print "min latency in ms", min_delay * 1000
    return ((float)(total_duration) / (float)( total_packets )) * 1000

def get_drop_rate(TCP_variant, CBR_rate):
    FLOW = 1
    pkt_sent = 0;
    pkt_recvd = 0;
    # Calculate from rate here :
    # loss % = (pkt_sent - pkt_recvd) / pkt_sent * 100
    filename = "trace_files/1_exp/" + TCP_variant + "_output_at_" + CBR_rate + ".tr"
    nstrace.nsopen(filename)

    while not nstrace.isEOF():
        if nstrace.isEvent():

            # get the tuple and send it to class
            trace = Trace_event(nstrace.getEvent())
            # since we have only one flow we care about
            if trace.fid_8 == FLOW:
                if trace.event_1 == "+" and trace.send_node_3 == n1:
                    pkt_sent += 1
                if trace.event_1 == "r" and trace.dest_node_4 == n4:
                    pkt_recvd += 1

        else:
            nstrace.skipline()

    nstrace.nsclose()

    # print "packet_loss_ratio : ", float(pkt_sent - pkt_recvd) / float(pkt_sent)
    return float(pkt_sent - pkt_recvd) / float(pkt_sent)



# get_throughput()
# get_latency()
# get_drop_rate()

TCP_variant = ['Tahoe', 'Reno', 'NewReno', 'Vegas']
ns_command_ccis = "/course/cs4700f12/ns-allinone-2.35/bin/ns "
ns_command_home = "ns "

# Generate trace files
for var in TCP_variant:
    for rate in range(1, 11):
        os.system(ns_command_home + "exp1.tcl " + var + " " + str(rate))

# t = get_throughput('Tahoe', '1')
# l = get_latency('Tahoe', '1')
# d = get_drop_rate('Tahoe', '1')
# #
# print t, "  ", l, "  ", d

# writing data into respective files

file1 = open("csv_files/1_exp/throughput.csv", 'wt')
file2 = open("csv_files/1_exp/latency.csv", 'wt')
file3 = open("csv_files/1_exp/drop_rate.csv", 'wt')
writer1 = csv.writer(file1)
writer2 = csv.writer(file2)
writer3 = csv.writer(file3)

writer1.writerow(('CBR_rate', 'Tahoe', 'Reno', 'NewReno', 'Vegas'))
writer2.writerow(('CBR_rate', 'Tahoe', 'Reno', 'NewReno', 'Vegas'))
writer3.writerow(('CBR_rate', 'Tahoe', 'Reno', 'NewReno', 'Vegas'))
for rate in range(1, 11):
    temp_t = []
    temp_l = []
    temp_d = []
    for variant in TCP_variant:
        temp_t.append(get_throughput(variant, str(rate)))
        temp_l.append(get_latency(variant, str(rate)))
        temp_d.append(get_drop_rate(variant, str(rate)))
    temp_t.insert(0, rate)
    temp_l.insert(0, rate)
    temp_d.insert(0, rate)
    # print l_t
    writer1.writerow(( temp_t ))
    writer2.writerow(( temp_l ))
    writer3.writerow(( temp_d ))
file1.close()
file2.close()
file3.close()
