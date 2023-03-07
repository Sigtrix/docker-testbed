# Dumbbell topology
Launches containers c1, c2 r1, r2, s1 and s2 where r1 and r2 act as routers and
forward traffic between the clients c1 and c2, and the servers s1 and s2. The
configuration is shown in the figure below.

![liner-setup](documentation/dumbbell.png)

## Run locally
To launch the containers in the configuration above run
the script *dumbbell.sh* from the *dumbell* directory i.e.
the current working directory.
```
./dumbbell.sh
```