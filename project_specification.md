Part B. Beamforming Simulator
Beamforming and direction of arrival (DOA) are fundamental concepts in modern technologies starting from wireless
communications, 5G, radar, sonar to biomedical applications like ultrasound and tumor ablations. The core ideas of
beamforming are delays/ phase-shifts and constructive/destructive interference. Do your own research and/or check
the tutorials below (tutorial 1, tutorial 2, tutorial 3) to grasp the idea and inspired by the relevant available toolboxes
(e.g., Matlab’s and others) develop your own 2D beamforming simulator where the user can:
- Customize the parameters below to be able to steer the beam direction in real time.
o Different system parameters like number of transmitters/receivers, applied delays/shifts, number of
operating frequencies along with their values in real time.
o The geometry of the phased array in terms of linear or curved (the curvature parameters should be
customizable).
- Visualize the constructive/destructive map along with the beam profile in different synchronized viewers.
- Add multiple phased array units to the system and customize the location and parameters of each of them.
Equip your simulator with at least three different scenarios through parameter settings files that the user can directly
open, visualize and customize or fine-tune. Your scenarios should be inspired by ideas from 5G, Ultrasound, tumor
ablation.
Code Practice:
-
-
Same practices from previous tasks (i.e. No code repetition) will continue in this task.
Apply OOP Concepts:
➢ Think of in terms of OOP. If you start implementing each image and its components, or each phased
array, the code will have a lot of repetitions.
➢ Apply the encapsulation concepts of OOP. Do not create a class for the image and its display and then
start implementing everything outside! A very few codes in expected to show in your main function.
Most of the code should be inside the image/display class or the phased array class! No mathematical
manipulation for the image or the phased array should be handled outside the image class!