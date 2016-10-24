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
    FLOW_1 = 1 # fid for variant 1
    FLOW_2 = 2 # fid for variant 2
    pkt_count_sent_n1 = pkt_count_sent_n5 = 0
    pkt_count_recvd_n4 = pkt_count_recvd_n6 = 0
    pkt_count_recvd_size1 = pkt_count_recvd_size2 = 0
    # this will change when we find a lower start time
    start_time1 = start_time2 = 10.0;
    # this will change when we find a higher end time
    end_time1 = end_time2 = 0.0

    recvd_size1 = recvd_size2 = 0

    filename = "trace_files/2_exp/" + TCP_variant + "_output_at_" + CBR_rate + ".tr"
    print filename
    nstrace.nsopen(filename)
    while not nstrace.isEOF():
        if nstrace.isEvent():

            # (event_1, time_2, send_node_3, dest_node_4, pkt_type_5, pkt_size_6,
            # flags_7, fid_8, src_addr_9, dst_addr_10, seq_num_11, pkt_id_12) = nstrace.getEvent()

            # get the tuple and send it to class
            trace = Trace_event(nstrace.getEvent())

            # for flow 1
            if trace.fid_8 == FLOW_1:
                if trace.event_1 == "+" and trace.send_node_3 == n1:
                    pkt_count_sent_n1 = pkt_count_sent_n1 + 1
                    # set start time for the tcp data, should happen only once
                    if trace.time_2 < start_time1:
                        start_time1 = trace.time_2

                elif trace.event_1 == "r" and trace.dest_node_4 == n4:
                    pkt_count_recvd_n4 = pkt_count_recvd_n4 + 1
                    pkt_count_recvd_size1 = pkt_count_recvd_size1 + trace.pkt_size_6

                # to Calculate the end time
                elif trace.event_1 == "r" and trace.dest_node_4 == n1:
                    if trace.time_2 > end_time1:
                        end_time1 = trace.time_2

            # for flow 2
            elif trace.fid_8 == FLOW_2:
                if trace.event_1 == "+" and trace.send_node_3 == n5:
                    pkt_count_sent_n5 = pkt_count_sent_n5 + 1
                    # set start time for the tcp data, should happen only once
                    if trace.time_2 < start_time2:
                        start_time2 = trace.time_2

                elif trace.event_1 == "r" and trace.dest_node_4 == n6:
                    pkt_count_recvd_n6 = pkt_count_recvd_n6 + 1
                    pkt_count_recvd_size2 = pkt_count_recvd_size2 + trace.pkt_size_6

                # to Calculate the end time
                elif trace.event_1 == "r" and trace.dest_node_4 == n5:
                    if trace.time_2 > end_time2:
                        end_time2 = trace.time_2

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
    # print "packets sent by n1 : ", pkt_count_sent_n1, " packets sent by n5 : ", pkt_count_sent_n5
    # print "packets recvd by n4 : ", pkt_count_recvd_n4, " packets recvd by n6 : ", pkt_count_recvd_n6
    # print "total size recvd at n4: ", pkt_count_recvd_size1, " total size recvd at n6: ", pkt_count_recvd_size2
    # size is usually in bits/s etc
    # print "precieved throughput_1 in Mbps: ", ((pkt_count_recvd_size1 * 8 )/ (end_time1 - start_time1)) / (1000 * 1000)
    # print "precieved throughput_2 in Mbps: ", ((pkt_count_recvd_size2 * 8 )/ (end_time2 - start_time2)) / (1000 * 1000)
    # return ((pkt_count_recvd_size * 8 )/ (end_time - start_time)) / (1000 * 1000)
    th_put_1 = ((pkt_count_recvd_size1 * 8 )/ (end_time1 - start_time1)) / (1000 * 1000)
    th_put_2 = ((pkt_count_recvd_size2 * 8 )/ (end_time2 - start_time2)) / (1000 * 1000)
    return [th_put_1, th_put_2]
# measured as the time required for a packet to be returned to its sender
# Here I will measure it by time the paket was sent from node1 to the time n1
# receives it acknowledgement

# It is possible to calculate the latency in the throughput function itself
# However, It will make the function very messy and unclean
# can also be refered to as avg. delay in the system
def get_latency(TCP_variant, CBR_rate):
    FLOW_1 = 1 # fid for variant 1
    FLOW_2 = 2 # fid for variant 2

    start_time1 = {}
    end_time1 = {}
    start_time2 = {}
    end_time2 = {}

    # avg. delay / latency = totaly_duration / total_packets * 1000 (millisesonds)
    total_duration1 = total_duration2 = 0.0
    total_packets1 = total_packets2 = 0

    max_delay1 = max_delay2 = 0;
    min_delay1 = min_delay2 = 1000;

    filename = "trace_files/2_exp/" + TCP_variant + "_output_at_" + CBR_rate + ".tr"
    nstrace.nsopen(filename)

    while not nstrace.isEOF():
        if nstrace.isEvent():


            # get the tuple and send it to class
            trace = Trace_event(nstrace.getEvent())
            # since we have only one flow we care about
            if trace.fid_8 == FLOW_1:
                if trace.event_1 == "+" and trace.send_node_3 == n1:
                    seq_stamp1 = {trace.seq_num_11 : trace.time_2}
                    start_time1.update(seq_stamp1)
                # ask TA if latency is calculated when packet ack arrives at n1
                # or packet received at n4
                elif trace.event_1 == "r" and trace.dest_node_4 == n1:
                    seq_stamp1 = {trace.seq_num_11 : trace.time_2}
                    end_time1.update(seq_stamp1)

            elif trace.fid_8 == FLOW_2:
                if trace.event_1 == "+" and trace.send_node_3 == n5:
                    seq_stamp2 = {trace.seq_num_11 : trace.time_2}
                    start_time2.update(seq_stamp2)
                # ask TA if latency is calculated when packet ack arrives at n1
                # or packet received at n4
                elif trace.event_1 == "r" and trace.dest_node_4 == n5:
                    seq_stamp2 = {trace.seq_num_11 : trace.time_2}
                    end_time2.update(seq_stamp2)

        else:
            nstrace.skipline()

    nstrace.nsclose()


    # print "start_time", start_time
    # print "end_time", end_time

    # calculate latency1 here
    for seq_stamp in start_time1:
        if seq_stamp in end_time1:
            latency = end_time1[seq_stamp] - start_time1[seq_stamp]
            # checking for false data
            if latency > 0:
                total_duration1 += latency
                total_packets1 += 1
                if latency > max_delay1:
                    max_delay1 = latency
                if latency < min_delay1:
                    min_delay1 = latency


    # calculate latency2 here
    for seq_stamp in start_time2:
        if seq_stamp in end_time2:
            latency = end_time2[seq_stamp] - start_time2[seq_stamp]
            # checking for false data
            if latency > 0:
                total_duration2 += latency
                total_packets2 += 1
                if latency > max_delay2:
                    max_delay2 = latency
                if latency < min_delay2:
                    min_delay2 = latency


    # print "total_packets1 : ", total_packets1, " total_packets2 : ", total_packets2
    # print "start_time1 length : ", len(start_time1), " start_time2 length : ", len(start_time2)
    # print "end_time length1 : ", len(end_time1), " end_time length2 : ", len(end_time2)
    # print "latency_1 in ms : ", ((float)(total_duration1) / (float)( total_packets1 )) * 1000
    # print "latency_2 in ms : ", ((float)(total_duration2) / (float)( total_packets2 )) * 1000
    # print "max latency_1 in ms", max_delay1 * 1000, " max latency_2 in ms", max_delay2 * 1000
    # print "min latency_1 in ms", min_delay1 * 1000, " min latency_2 in ms", min_delay2 * 1000
    l1 = ((float)(total_duration1) / (float)( total_packets1 )) * 1000
    l2 = ((float)(total_duration2) / (float)( total_packets2 )) * 1000
    return [l1, l2]


def get_drop_rate(TCP_variant, CBR_rate):
    FLOW_1 = 1 # fid for variant 1
    FLOW_2 = 2 # fid for variant 2

    pkt_sent1 = pkt_sent2 = 0;
    pkt_recvd1 = pkt_recvd2 = 0;
    # Calculate from rate here :
    # loss % = (pkt_sent - pkt_recvd) / pkt_sent * 100
    filename = "trace_files/2_exp/" + TCP_variant + "_output_at_" + CBR_rate + ".tr"
    nstrace.nsopen(filename)

    while not nstrace.isEOF():
        if nstrace.isEvent():

            # get the tuple and send it to class
            trace = Trace_event(nstrace.getEvent())
            # since we have 2 flows
            if trace.fid_8 == FLOW_1:
                if trace.event_1 == "+" and trace.send_node_3 == n1:
                    pkt_sent1 += 1
                if trace.event_1 == "r" and trace.dest_node_4 == n4:
                    pkt_recvd1 += 1

            elif trace.fid_8 == FLOW_2:
                if trace.event_1 == "+" and trace.send_node_3 == n5:
                    pkt_sent2 += 1
                if trace.event_1 == "r" and trace.dest_node_4 == n6:
                    pkt_recvd2 += 1

        else:
            nstrace.skipline()

    nstrace.nsclose()

    # print "packet_loss_ratio1 : ", float(pkt_sent1 - pkt_recvd1) / float(pkt_sent1)
    # print "packet_loss_ratio2 : ", float(pkt_sent2 - pkt_recvd2) / float(pkt_sent2)
    d1 = float(pkt_sent1 - pkt_recvd1) / float(pkt_sent1)
    d2 = float(pkt_sent2 - pkt_recvd2) / float(pkt_sent2)
    return [d1, d2]



# get_throughput()
# get_latency()
# get_drop_rate()

TCP_variant = ['Reno_Reno', 'NewReno_Reno', 'Vegas_Vegas', 'NewReno_Vegas']
ns_command_ccis = "/course/cs4700f12/ns-allinone-2.35/bin/ns "
ns_command_home = "ns "

# # Generate trace files
for var in TCP_variant:
    for rate in range(1, 11):
        TCPs = var.split('_')
        os.system(ns_command_home + "exp2.tcl " + TCPs[0] + " " + TCPs[1] + " " + str(rate))


# t = get_throughput('Reno_Reno', '10')
# l = get_latency('Reno_Reno', '10')
# d = get_drop_rate('Reno_Reno', '10')

# print d
# print t, "  ", l, "  ", d

# writing data into respective files

file1 = open("csv_files/2_exp/throughput.csv", 'wt')
file2 = open("csv_files/2_exp/latency.csv", 'wt')
file3 = open("csv_files/2_exp/drop_rate.csv", 'wt')
writer1 = csv.writer(file1)
writer2 = csv.writer(file2)
writer3 = csv.writer(file3)

writer1.writerow(('CBR_rate', '1_Reno1', '1_Reno2', '2_NewReno', '2_Reno',
                    '3_Vegas1', '3_Vegas2', '4_NewReno', '4_Vegas'))
writer2.writerow(('CBR_rate', '1_Reno1', '1_Reno2', '2_NewReno', '2_Reno',
                    '3_Vegas1', '3_Vegas2', '4_NewReno', '4_Vegas'))
writer3.writerow(('CBR_rate', '1_Reno1', '1_Reno2', '2_NewReno', '2_Reno',
                    '3_Vegas1', '3_Vegas2', '4_NewReno', '4_Vegas'))
for rate in range(1, 11):
    temp_t = []
    temp_l = []
    temp_d = []
    for variant in TCP_variant:
        temp_t += get_throughput(variant, str(rate))
        temp_l += get_latency(variant, str(rate))
        temp_d += get_drop_rate(variant, str(rate))
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
