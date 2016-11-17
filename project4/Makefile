all:
	@sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
	@chmod 0744 rawhttpget
