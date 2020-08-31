### Roadmap


### Nice-to-haves
Additional features, improvements, or desires for consideration for this project:
- Look into extending the custom `ros_comm` including `roscore` api
  - In addition to current parameter read/set information
  - Handle parameter subscriptions
  - to add warnings for race conditions for parameter reads / subscriptions
  - to enable / disable the debugging / probing features (for runtime performance)
  - store process exe information (so available after process quits)
  - store exe information when loading Nodelet-specific plugin executable instead of just plugin loader info
- Change `Node` class `executable` method to remove system path, thus revealing just the relative executable or Type

### Recently Completed
