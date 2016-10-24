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

# In this expreiment, we have to get throughput over time. Since I have simulation
# runtime of 10 seconds, I will calculate throughput over a duration of 0.5 seconds


def get_throughput(TCP_variant, Q_var, duration=0.5):
    FLOW_1 = 1 # for tcp
    FLOW_3 = 3 # for udp
    # pkt_count_sent_n1 = pkt_count_sent_n5 = 0
    # pkt_count_recvd_n4 = pkt_count_recvd_n6 = 0
    pkt_size_recvd_tcp = pkt_size_recvd_udp = 0

    overall_time = 0.0

    file_to_read = "trace_files/3_exp/" + TCP_variant + "_" +  Q_var + "_out" + ".tr"

    file_to_write = open("csv_files/3_exp/" + TCP_variant + "_" + Q_var + "_throughput.csv", 'wt')
    writer = csv.writer(file_to_write)
    writer.writerow(('time', 'throughput_tcp', 'throughput_udp'))
    print file_to_read
    nstrace.nsopen(file_to_read)

    while not nstrace.isEOF():
        if nstrace.isEvent():

            # get the tuple and send it to class
            trace = Trace_event(nstrace.getEvent())
            # when tcp packet is received at n4
            if trace.fid_8 == FLOW_1 and trace.event_1 == "r" and trace.dest_node_4 == n4:
                pkt_size_recvd_tcp += trace.pkt_size_6

            # when udp packet is received at n6
            if trace.fid_8 == FLOW_3 and trace.event_1 == "r" and trace.dest_node_4 == n6:
                pkt_size_recvd_udp += trace.pkt_size_6

            # calculate throughput and reset packet size after 0.5 seconds
            if trace.time_2 - overall_time < duration:
                # print trace.time_2 - overall_time
                pass
            else:
                overall_time += duration
                # size in Mbps
                throughput_tcp = (pkt_size_recvd_tcp * 8) / duration / (1024*1024)
                throughput_udp = (pkt_size_recvd_udp * 8) / duration / (1024*1024)

                # print "tcp : ", throughput_tcp, " udp : ", throughput_udp, " at ", overall_time
                writer.writerow((overall_time, throughput_tcp, throughput_udp))

                # reset size and add time

                pkt_size_recvd_udp = pkt_size_recvd_tcp = 0
                # print overall_time
        else:
            print "skip"
            nstrace.skipline()

    # print "done"
    nstrace.nsclose()
    file_to_write.close()

# we only Calculate end to end latency(RTT) for tcp flow as UDP has no such thing.
def get_latency(TCP_variant, Q_var, duration = 0.5):
    FLOW_1 = 1 # for tcp
    # FLOW_3 = 3 # for udp

    start_time_tcp = {}
    end_time_tcp = {}

    # avg. delay / latency = totaly_duration / total_packets * 1000 (millisesonds)
    overall_time = 0.0
    total_packets1 =  0
    total_duration1 = 0.0

    file_to_read = "trace_files/3_exp/" + TCP_variant + "_" +  Q_var + "_out" + ".tr"

    file_to_write = open("csv_files/3_exp/" + TCP_variant + "_" + Q_var + "_latency.csv", 'wt')
    writer = csv.writer(file_to_write)
    writer.writerow(('time', 'latency_tcp'))
    print file_to_read
    nstrace.nsopen(file_to_read)

    while not nstrace.isEOF():
        if nstrace.isEvent():

            # get the tuple and send it to class
            trace = Trace_event(nstrace.getEvent())

            if trace.fid_8 == FLOW_1:
                if trace.event_1 == "+" and trace.send_node_3 == n1:
                    seq_stamp1 = {trace.seq_num_11 : trace.time_2}
                    start_time_tcp.update(seq_stamp1)
                # ask TA if latency is calculated when packet ack arrives at n1
                # or packet received at n4
                elif trace.event_1 == "r" and trace.dest_node_4 == n1:
                    seq_stamp1 = {trace.seq_num_11 : trace.time_2}
                    end_time_tcp.update(seq_stamp1)

            if trace.time_2 - overall_time < duration:
                pass
            else:
                overall_time += duration


                # calculate latency1 here
                for seq_stamp in start_time_tcp:
                    if seq_stamp in end_time_tcp:
                        latency = end_time_tcp[seq_stamp] - start_time_tcp[seq_stamp]
                        # checking for false data
                        if latency > 0:
                            total_duration1 += latency
                            total_packets1 += 1
                # print TCP_variant, Q_var
                # print total_duration1
                # print total_packets1
                l1 = ((float)(total_duration1) / (float)( total_packets1 )) * 1000

                print "latency  : ", l1, " at time : ", overall_time
                writer.writerow((overall_time, l1))
                start_time_tcp = {}
                end_time_tcp = {}

        else:
            print "skip"
            nstrace.skipline()


    # print "done"
    nstrace.nsclose()
    file_to_write.close()





TCP_variant = ['Reno', 'SACK']
Q_var = ['DropTail', 'RED']
# get_throughput('Reno', 'RED')
# get_latency('Reno', 'RED')
# depending upon where you are running the file,
ns_command_ccis = "/course/cs4700f12/ns-allinone-2.35/bin/ns "
ns_command_home = "ns "


# Generate trace_files
for var in TCP_variant:
    for q in Q_var:
        os.system(ns_command_home + "exp3.tcl " + var + " " + q)

# Calculate throughput and latency
for var in TCP_variant:
    for q in Q_var:
        get_throughput(var, q)
        get_latency(var, q)
