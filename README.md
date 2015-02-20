# gerrit-latency
Use gerrit REST API in order to mesure latency of commits, and do some statiscal analysis

# Dependencies
* Workdays ( http://pypi.python.org/pypi/workdays/ )
* Requests ( http://docs.python-requests.org/ )
* MatPlotlib ( http://matplotlib.org/ )
* Numpy ( http://www.numpy.org/ )

# Configuration
You need to edit conf.py with all informations from your gerrit server and your user profile.

# Examples
Within python interpreter:

```
> execfile("gerrit_latency.py")
> analyse_details(get_change_details("owner:self+status:merged"))
```