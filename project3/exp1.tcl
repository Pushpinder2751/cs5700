#Create a simulator object
set ns [new Simulator]

# TCP variant
set variant [lindex $argv 0]
# CBR Rate
set rate [lindex $argv 1]


#Open the trace file (before you start the experiment!)
# important to name the file properly

set tf [open trace_files/1_exp/${variant}_output_at_${rate}.tr w]
$ns trace-all $tf


#Define a 'finish' procedure
proc finish {} {
        global ns tf
        $ns flush-trace
        # Close the trace file (after you finish the experiment!)
        close $tf
        exit 0
}

# Question : can i number them 1-5?
#Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between the nodes
# This is how it looks, check if I need to use duplex or not
# duplex-link node node b/w delay queue
#$ns duplex-link $n0 $n2 2Mb 10ms DropTail


$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

# Commenting this out for now, do not know if I need it
#Set Queue Size of link (n2-n3) to 10
# $ns queue-limit $n2 $n3 10



# Commenting it out right now, do not know how to use it.
#Monitor the queue for link (n2-n3). (for NAM)
# $ns duplex-link-op $n2 $n3 queuePos 0.5




#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null
$udp set fid_ 2

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ ${rate}mb
$cbr set random_ false
$cbr attach-agent $udp


#Setup a TCP connection
if {$variant eq "Tahoe"} {
    set tcp [new Agent/TCP]
} elseif {$variant eq "Reno"} {
    set tcp [new Agent/TCP/Reno]
} elseif {$variant eq "NewReno"} {
    set tcp [new Agent/TCP/Newreno]
} elseif {$variant eq "Vegas"} {
    set tcp [new Agent/TCP/Vegas]
}

$tcp set class_ 1
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1


#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP

# Let's trace some variables
$tcp attach $tf
$tcp tracevar cwnd_
$tcp tracevar ssthresh_
$tcp tracevar ack_
$tcp tracevar maxseq_
$tcp tracevar nrexmitpack_



#Schedule events for the CBR and FTP agents
$ns at 0.0 "$cbr start"
$ns at 0.0 "$ftp start"
$ns at 10.0 "$ftp stop"
$ns at 10.0 "$cbr stop"

#Detach tcp and sink agents (not really necessary)
#$ns at 4.5 "$ns detach-agent $n1 $tcp ; $ns detach-agent $n4 $sink"



#Call the finish procedure after 5 seconds of simulation time
$ns at 10.0 "finish"


#Run the simulation
$ns run
