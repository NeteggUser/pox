"""Custom topology example
Adding the 'topos' dict with a key/value pair to generate our newly defined 
topology enables one to pass in '--topo=mytopo' from the command line
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.util import pmonitor
from mininet.cli import CLI
from mininet.net import Mininet
from time import time
from signal import SIGINT
from mininet.node import Controller, RemoteController
import re 
import os

class MyTopo(Topo):
    "User Study"
    def __init__(self, n=2):
        Topo.__init__(self)

        #Add hosts and switches 
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        switch = self.addSwitch( 's3' )
        
        #Add links
        self.addLink( leftHost, switch ) 
        self.addLink( rightHost, switch )

def Test1():
    print "Beginning Test 1: Testing whether UDP packet from CS can go through"
    topo = MyTopo(2)
    net = Mininet(topo, controller=RemoteController)

    net.start()

    leftHost = net['h1']
    rightHost = net['h2']
    switch = net['s3']

    popens = {}
    popens[rightHost] = rightHost.popen('iperf -s -u')
    popens[leftHost] = leftHost.popen('iperf -c 10.0.0.2 -u')

    seconds = 20
    endTime = time() + seconds
    num = 0
    output_3 = ''
    
    for h, line in pmonitor(popens, timeoutms=1000 ):
        if h:
 	    output_3 += line
	    num = num + 1
  	    if num == 2:
		text = "Server listening on UDP port 5001\n"
		if text == line:
			value1 = 0
		else:
			value1 = 1
	   
 	    if num == 3:
		text = "Receiving 1470 byte datagrams\n"
		if text == line:
			value2 = 0
		else:
			value2 = 1
	    
	    if num == 4:
		text = "UDP buffer size:  208 KByte (default)\n"
		if text == line:
			value3 = 0
		else:
			value3 = 1

	    if num == 7:
		text = "Client connecting to 10.0.0.2, UDP port 5001\n"
		if text == line:
			value4 = 0
		else: 
			value4 = 1

	    if num == 8:
		text = "Sending 1470 byte datagrams\n"
		if text == line:
			value5 = 0
		else:
			value5 = 1

        if time() >= endTime:
            for p in popens.values():
                p.send_signal( SIGINT )


    if value1 == 1 or value2 == 1 or value3 == 1 or value4 == 1 or value5 == 1:
	print "Test 1 Failed"
    elif num < 16:
	print "Test 1 Failed"
    else:
        #print output_3
	k = _parseIperf(output_3)
	m = parse_iperf(output_3)
	if k != '' and m == []:
		print "Test 1 passed"
	else:
		print "Test 1 Failed"
 
    net.stop()	
    #print "Test 1 ends here-------------------------------------------------"
	
def Test2():
    print "Beginning Test 2: Testing whether UDP packets from Internet get dropped"
    topo = MyTopo(2)
    net = Mininet(topo, controller=RemoteController)

    net.start()

    leftHost = net['h1']
    rightHost = net['h2']
    switch = net['s3']

    popens = {}
    popens[leftHost] = leftHost.popen('iperf -s -u')
    popens[rightHost] = rightHost.popen('iperf -c 10.0.0.1 -u')

    seconds = 20
    endTime = time() + seconds
    num = 0
    output_3 = ''
    
    for h, line in pmonitor(popens, timeoutms=1000 ):
        if h:
 	    output_3 += line
 	  
        if time() >= endTime:
            for p in popens.values():
                p.send_signal( SIGINT )


    #print output_3
    if num > 15:
	print "Test 1 Failed"

#    if output_3.find('Server Report') != -1:
#            print "Test 2 Failed"
    else:
            print "Test 2 Passed"
 
    net.stop()	

	
def Test3():
    print "Beginning Test 3: Testing whether TCP traffic initiated from Internet gets dropped"    
    topo = MyTopo(2)
    net = Mininet(topo, controller=RemoteController)

    net.start()
    leftHost = net['h1']
    rightHost = net['h2']
    switch = net['s3']

    popens = {}

    popens[leftHost] = leftHost.popen('iperf -s -p 80')
    popens[rightHost] = rightHost.popen('iperf -c 10.0.0.1 -p 80')    

    seconds = 20
 
    endTime = time() + seconds   
    num = 0
    value = 0
    output_1 = '' 
	
    # line contains the results of executions
    for h, line in pmonitor(popens, timeoutms=1000 ):
       if h:
       	  output_1 += line 
          num = num + 1
   
       if num == 2:
       	   text = "Server listening on TCP port 80\n"
     	   if text == line:
	      value = 1
	   else:
	      value = 0 	    
		   	

       if time() >= endTime:
	    for p in popens.values():
		 p.send_signal( SIGINT )

    out = _parseIperf(output_1)
		 
    #print output_1
    if num > 4 or value == 0:
		print "Test 3 Failed"
    else:
		if out == '':
			print "Test 3 Passed"
		else:
			print "Test 3 Failed"

    #print "------------------------------------------------------"
    net.stop()


def _parseIperf( iperfOutput ):
        """Parse iperf output and return bandwidth.
           iperfOutput: string
           returns: result string"""
        r = r'([\d\.]+ \w+/sec)'
        m = re.findall( r, iperfOutput )

        if m:
            return m[-1]
        else:
            # was: raise Exception(...)
            #print  'could not parse iperf output: ' + iperfOutput
            return ''
	
	
def parse_iperf( iperfOutput ): 
	p = 'read failed: Connection refused'
	n = re.findall( p, iperfOutput )
	if n == []:
		return n
	else:	
		return "false"

def Test4():
    print "Beginning Test 4: Testing whether TCP connection initiated from CS can go through"
    topo = MyTopo(2)
    net = Mininet(topo, controller=RemoteController)

    net.start()
    leftHost = net['h1']
    rightHost = net['h2']
    switch = net['s3']
	
    popens = {}

    popens[rightHost] = rightHost.popen('iperf -s -p 80')
    popens[leftHost] = leftHost.popen('iperf -c 10.0.0.2 -p 80')    

    seconds = 20
    endTime = time() + seconds   
    
    output_2 = ''
    for h, line in pmonitor(popens, timeoutms=1000 ):
        if h:
	  output_2 += line 
		  
        if time() >= endTime:
		for p in popens.values():
			p.send_signal( SIGINT )

    
    #print output_2
    k = _parseIperf(output_2)
    m = parse_iperf(output_2)
    if k != '' and m == [] :
		print "Test 4 passed"
    else:
		print "Test 4 failed"

    #print "Test 4 ends here----------------------------------------------------"
    net.stop()
	

# Check UDP from the internal is allowed

def Test5():
    print "Beginning Test 5: Testing whether SSH packets from Internet get dropped"
    topo = MyTopo(2)
    net = Mininet(topo, controller=RemoteController)
    #, controller=RemoteController)

    net.start()
    leftHost = net['h1']
    rightHost = net['h2']
    switch = net['s3']
	
    popens = {}

    popens[leftHost] = leftHost.popen('iperf -s -p 22')
    popens[rightHost] = rightHost.popen('iperf -c 10.0.0.2 -p 22')

    seconds = 20
    endTime = time() + seconds   
    output_4 = ''
    
    for h, line in pmonitor(popens, timeoutms=10000 ):
        if h:
 	  output_4 += line 
		  
        if time() >= endTime:
		for p in popens.values():
			p.send_signal( SIGINT )

    
    #print output_4 
    k = _parseIperf(output_4)
    if k == '':
        print "Test 5 Passed"
    else:
        print "Test 5 Failed"
    net.stop()


	
if __name__ == '__main__':
        os.system("mn -c")
	Test1()
	Test2()   	
        Test3()
	Test4()	
	Test5()	
	
