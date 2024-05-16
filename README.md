# ch9329
Human interface device system using ch9329 emulator.

Kumamoto University graduation research project.


CH9329interfacesystem folder contains 6 versions of interface system, which the 5th is final touchless gesture mouse emulator interface system.

  CH9329ver0 : CH9329 emulator's functions based on sample code of みんなのラボ (URL: http://minnanolab.net/product/pro_keyboardmouse/pro_keyboardmouse.html)

  CH9329ver1 : get AR marker's coordinates and use as inputs of move function
  
  CH9329ver2 : control mapping between controller device and control destination device
  
  CH9329ver3 : using keyboards as additional inputs, implements click, drag and scroll functions
  
  CH9329ver4 : make 2 threads and implements simultanous AR marker tracking(coordinates extracting) and mouse functions
  
  CH9329ver5 : increasing accuracy of mouse emulation using mutual exclusion between threads


camera calibration folder contains python code for camera calibration of controller.
