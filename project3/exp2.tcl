# Create a Simulator
set ns [new Simulator]

# TCP type
set tcp_var1 [lindex $argv 0]
set tcp_var2 [lindex $argv 1]

# CBR rate
set rate [lindex $argv 2]

# open the trace file
set tf [open trace_files/2_exp/${tcp_var1}_${tcp_var2}_output_at_${rate}.tr w]
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
$udp set fid_ 3

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ ${rate}mb
$cbr set random_ false
$cbr attach-agent $udp

# Setup a TCP1 connection
if {$tcp_var1 eq "Reno"} {
    set tcp1 [new Agent/TCP/Reno]
} elseif {$tcp_var1 eq "NewReno"} {
    set tcp1 [new Agent/TCP/Newreno]
} elseif {$tcp_var1 eq "Vegas"} {
    set tcp1 [new Agent/TCP/Vegas]
}

$tcp1 set class_ 1
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 1


# Setup a TCP2 connection
if {$tcp_var2 eq "Reno"} {
    set tcp2 [new Agent/TCP/Reno]
} elseif {$tcp_var2 eq "Vegas"} {
    set tcp2 [new Agent/TCP/Vegas]
}

$tcp2 set class_ 2
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
$tcp2 set fid_ 2

# setup a FTP1 Application
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1

# setup an FTP2 Application
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2

#Schedule events for the CBR and FTP agents
$ns at 0.0 "$cbr start"
$ns at 0.0 "$ftp1 start"
$ns at 0.0 "$ftp2 start"
$ns at 10.0 "$ftp2 stop"
$ns at 10.0 "$ftp1 stop"
$ns at 10.0 "$cbr stop"

#Call the finish procedure after  seconds of simulation time
$ns at 10.0 "finish"

#Run the simulation
$ns run
