# Install Python and Selenium packages in Ubuntu for headless mode

apt install python-minimal python-pip firefox xvfb
pip install selenium
pip install bs4

# Download gecko driver and move it to the PATH location
wget https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-linux64.tar.gz
tar -zxvf geckodriver-v0.14.0-linux64.tar.gz
mv geckodriver /usr/bin/

# Create Xvfb start/stop script
vim /etc/init.d/xvfb

XVFB=/usr/bin/Xvfb
XVFBARGS=":99 -screen 0 1024x768x24 -fbdir /var/run -ac"
PIDFILE=/var/run/xvfb.pid
case "$1" in
  start)
    echo -n "Starting virtual X frame buffer: Xvfb"
    start-stop-daemon --start --quiet --pidfile $PIDFILE --make-pidfile --background --exec $XVFB -- $XVFBARGS
    echo "."
    ;;
  stop)
    echo -n "Stopping virtual X frame buffer: Xvfb"
    start-stop-daemon --stop --quiet --pidfile $PIDFILE
    echo "."
    ;;
  restart)
    $0 stop
    $0 start
    ;;
  *)
        echo "Usage: /etc/init.d/xvfb {start|stop|restart}"
        exit 1
esac

exit 0

# Make it executable
chmod +x /etc/init.d/xvfb

# Edit crontab
crontab -e

# m h  dom mon dow   command
00 19 * * 1-5 /home/dimka/mos.ru/check_sad.sh > /dev/null 2>&1


