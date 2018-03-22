ps aux | grep torrc | grep -v grep | awk '{ print "sudo kill -9", $2 }' | sh > /dev/null 2>&1
