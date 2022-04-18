# Reinforcement-Learning_(ML)_PPO_Microwave Filter-Tuning
Brief Description: _Apply Proximal Policy Optimization (PPO) algorithm to tune microwave filter automatically_.<br />

---


## **_About The Project_**<br />
- Manufactured RF filter will need to go through the filter tuning process to guarantee the performance without compromising
- There are many factors such as tedious / difficult manual tuning process and filter characteristics that harden the filter tuning process
- Machine learning approach is used to shorten the time taken of filter tuning process and boost the accuracy of tuning outcome
- Proximal Policy Optimization (PPO) among reinforcement learning algorithm is chosen as its continuous action space and prominent divergence speed in continuous control tasks

---


## **_Built With_**<br />
- ANSYS-HFSS (Filter Simulation Software, 21.1)
- Stable Baseline 3 (PPO Agent)
- Pytorch (1.10.1)
- Python (3.8) by PyCharm IDE (2021.2.2)
- IronPython (2.7)


---

Type of microwave filter used in this project:<br />
4th Order Chebyshev Filter (simulated in HFSS)
![image](https://user-images.githubusercontent.com/85819871/163743277-a6b01aca-9e78-46f6-b757-9c993da2f295.png)
Filter Parameters To Be Tuned:
As the internal filter structure is symmetric, the specifications of resonator 1 is same with resonator 4 (the same goes to resonator 2 and 3). 
The filter parameters involved is the length of resonator 1 (4), and resonator 2 (3) as shown as below:
![image](https://user-images.githubusercontent.com/85819871/163744956-437fcb52-0f7c-441d-bb73-362e39a1a2c0.png)



--- 


 ## _**Project Framework** <br />_
 
 Reinforcement Learning Environment: HFSS (automated by Python and IronPython scripts in PyCharm)<br />_
 Reinforcement Learning Learning Agent: PPO agent (modified based on stable baseline 3 documentation source code)

