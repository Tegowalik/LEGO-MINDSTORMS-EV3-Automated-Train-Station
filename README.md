# LEGO-MINDSTORMS-EV3-Automated-Train-Station
Implementation of an automated LEGO City Train Station. Automation in terms of that incoming trains are guided to the best free train station track. This track will be blocked until the train drives away. This requires three EV3s. 

The *detector* EV3 detects the incoming train as is used to estimate the train's length.
The *switch* EV3 detects the incoming trains and controls the switches such that the train is guided towards the best station track.
The *station* EV3 detects which station track is blocked or free.

This video demonstrates the usage: https://youtu.be/scJiWCuIgd4

A Powered Up version based on https://github.com/Tegowalik/LEGO-Switch-Controller is planned.
