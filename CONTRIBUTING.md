# Contributing

Welcome to the Emulate Edge Diagnosos Platform FH-DO repository!

Before you start, please take a look to the labels created for issue definition.

Labels are defined as follows 

- `New_feature`: Use this label to request a new feature you think would be useful for your and other's work.
- `Bug`: As this is a work in progress, many bugs will appear as you test the platform. Please inform about them using this label.
- `Testing`: Use this label to create an issue that requires further testing. Some features might be developed but not tested yet. Therefore, you could contribute by testing them in your environment.
- `Enhacement`: Some features are already implemented but can be enhanced with new approaches or extra stuff.
- `Question`: Use this label only to request some assitance.
- `For-approval`: Use this label once all the tasks of an issue have been completed and you request for approval before a merge request.
- `Backlog`: Once the issue has been registered and validated by the mantainer, it will be labeled as backlog.
- `On-progress`: Use this label to mark that you have started to work in solving a certain issue. Please only work in one issue at the time.


## Creating a Request

Requests are created via issues but MUST be properly formated to be taken into consideration. To create a request follow these steps:

1. Create the request of a new feature with the keyword `REQ` before the name of the request. Name it with a proper and descriptive name. Do not exceeed 12 words. 

2. In the issue description follow this template:

-------------------------------------

**Feature Description**  
Describe the solution you'd like and for what you will use it. Add a detailed explanation of the context and any observation.



**Technologies Considered**  
Have you considered any technology that can help to achieve this?

-------------------------------------

3.  Add the `Request` label to the issue.


## Reporting a Bug

Bugs are reported via issues but MUST be properly formated to be taken into consideration. To report a bug follow these steps:

1. Create the bug report with the keyword `BUG` before the name of the request. Name it with a proper and descriptive name. Do not exceeed 12 words. 

2. In the issue description follow this template:

-------------------------------------

**Bug Description**  
Describe the bug you have found. Add a detailed explanation of the context and any observation.

**How to replicate**
Detail what you have done twhen the bug appeared. Provide instructions to be able to replicate it.

**Possible Solutions**  
Have you considered any solution can help to fix the bug?

-------------------------------------

3.  Add the `Bug` label to the issue.


## Contribution Methodology

Open and considered issues will be put in the backlog and labeled by the `Backlog` label.

Please select only one issue at the time and assign yourself to solve it. 

Depending on the complexity of the issue, several internal tasks can be created. The person solving the issue must create the tasks. As a guideline, try to calculate that each task does not take longer than 5 days to be solved.  Individual tasks must also be marked as completed.

1. Assign the label `On-progress` to your issue

2. Create a branch for the issue (keep the default name).

3. Before implementing the code consider that every single piece of code change/incorporation/optimization/etc. in this repo is to be done following the next steps:  

* While you implement your solution, comment important things you have tried to solve the issue (we will use these comments as a guide for other contributors to follow if they have to implement something similar or continue with your work)
* Make commits for small changes, dont make only one commit for the complete issue (unless it was extremely simple). Finally, make sure to commit your changes in the branch you have created.
* Once finished with the issue, assign the label `For-approval` to it. 
* Do not create the merge request until you have notified about it to the main developer (Iurii)
* Create the merge request 
* Implement all requested changes

_Important: DO NOT merge a branch without prior confirmation and approval of other members._



## Questions and Doubts

* Any question/doubt about SW architecture or implementation is to be written as an issue using the keyword `QST` before the name of the request. Remember to also label the issue with the `Question` label.

