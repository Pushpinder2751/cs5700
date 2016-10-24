# Create a Simulator object
set ns [new Simulator]

# TCP type
set tcp_var [lindex $argv 0]

# Queue type
set q_var [lindex $argv 1]

# open a trace file
set tf [open trace_files/3_exp/${tcp_var}_${q_var}_out.tr w]
$ns trace-all $tf

#Define a 'finish' procedure
proc finish {} {
        global ns tf
        $ns flush-trace
        # Close the trace file (after you finish the experiment!)
        close $tf
        exit 0
}

#Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

# create links between the nodes according to the q_var selected
if {$q_var eq "DropTail"} {
    $ns duplex-link $n1 $n2 10Mb 10ms DropTail
    $ns duplex-link $n2 $n3 10Mb 10ms DropTail
    $ns duplex-link $n5 $n2 10Mb 10ms DropTail
    $ns duplex-link $n3 $n4 10Mb 10ms DropTail
    $ns duplex-link $n3 $n6 10Mb 10ms DropTail
} elseif {$q_var eq "RED"} {
    $ns duplex-link $n1 $n2 10Mb 10ms RED
    $ns duplex-link $n2 $n3 10Mb 10ms RED
    $ns duplex-link $n5 $n2 10Mb 10ms RED
    $ns duplex-link $n3 $n4 10Mb 10ms RED
    $ns duplex-link $n3 $n6 10Mb 10ms RED
}

# Commenting this out for now, do not know if I need it
#Set Queue Size of link (n2-n3) to 10
# $ns queue-limit $n2 $n3 10

$ns queue-limit	$n1 $n2 10
$ns queue-limit	$n5 $n2 10
$ns queue-limit	$n2 $n3 10
$ns queue-limit	$n4 $n3 10
$ns queue-limit	$n6 $n3 10

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null
$udp set fid_ 3

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ 5mb
$cbr set random_ false
$cbr attach-agent $udp


# Setup a tcp connection
if {$tcp_var eq "Reno"} {
    set tcp [new Agent/TCP/Reno]
    set sink [new Agent/TCPSink]
} elseif {$tcp_var eq "SACK"} {
    set tcp [new Agent/TCP/Sack1]
    set sink [new Agent/TCPSink/Sack1]
}

$tcp set class_ 1
$ns attach-agent $n1 $tcp
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1

# setup an ftp applicatoin
set ftp [new Application/FTP]
$ftp attach-agent $tcp

#Schedule events for the CBR and FTP agents
$ns at 0.0 "$ftp start"
$ns at 4.0 "$cbr start"
$ns at 10.0 "$ftp stop"
$ns at 10.0 "$cbr stop"


#Call the finish procedure after  seconds of simulation time
$ns at 10.0 "finish"

#Run the simulation
$ns run
