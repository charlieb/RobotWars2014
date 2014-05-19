RobotWars2014
=============

Sample and Shared Code for RobotWars2014
----------------------------------------

**Fluffy White Unicorns**

See FluffyWhiteUnicorns directory

Here is the video recorder code I used to capture the hand driven track avi along with the video I captured. To use it change the VideoCapture parameter from 0 to the file name. 

Cv2.VideoCapture(0) captures from the camera. cv2.VideoCapture(‘track_320x240.avi’) captures from the file.

I also included snapshots from the video that I used for initial detection algorithm development.

The PID class is also included. Something I didn't elaborate on is 1) What are we wanting to detect (error) and 2) What is it we wish the PID to produce (control)? For me the answers were angular deviation and motor differential.

Tuning the PID
--------------
1. Start with I & D at zero. 
2. Increase P to point of oscillation. 
3. Backoff P till stable. (Note bot will not turn sharp enough.)
4. Now increase D till corner can be made. If oscillation occurs then back P off a little more. 
5. I is for any steady state offset you might have.

** You want stability in the straight away with enough impulse to make the corners **

P - proportional (error * P)
D - differential (error-lastError * D)
I - integral (error+lastError * I)