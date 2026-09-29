# Introduction to LED Signage

A 2hr workshop for novice creative computing students where students program an LED Sign using LED Matrix Panels (128x64 and 64x64) and the Pimoroni Interstate 75W LED matrix driver.

The learning objectives are:
- Using niche tools to prepare media for low-resource platforms like microcontrollers.
- Creatively working within the hard limitations of low-resource platforms.
- Embracing play and experimentation when faced with intimidating technology.

[This workshop should be broken down into sections and parts outlined below, please expand upon sections and parts, using my language and style as reference. Keep in mind many of these students have no programming expertise and must by guided through every operation. Figures and diagrams may be required especially when using thonny, leave placeholder that I can replace. https://github.com/pimoroni/interstate75/tree/main should be used as the main source of truth. The folder/repo this readme is in will be cloned to each of the students computers]

Section 1: Technology Overview and Getting Started.

Part 1.1: Hardware
What do we mean by low-resource platforms in this context. These LED Panels are usually part of giant video walls made up of 100s of these panels driven by multiple GPUs in powerful media servers, which can be seen at the IVSL at the Institute of Creative Technology down the road at Havers Road. In this workshop we are using a hardware platform many orders of magnitude less powerful; the RP2350 microcontroller which is at the heart of the Pimoroni Interstate 75W Matrix Driver. Low resource hardware like this is usually called "embedded" hardware and is deployed when using a full computer with an operating system is overkill with unnecessary technical overhead, power requirements and a high economical cost especially with the current price of computer memory! [Show hardware comparison table between a high end rendering computer and the RP2350]
Usually when displaying media on displays you are working with large resolutions like HD (1280x720), FHD (1920x1080) and even UHD (3840 x 2160), here we have 64x64... such a limitation requires us to think hard about making images and text legible. 

Part 1.2: Software
The RP2350 is programmed with a programming language called micropython. This is a subset of the Python programming language targeting low-resource hardware such as microcontrollers. To transfer files and write our code we are using a text editor "Thonny". We are using a few software tools that are preinstalled on your computers to, these are command line tools and are accessed by using the terminal application on your computer. That is 'ffmpeg' for converting gifs to low-res individual frames and 'alright-fonts' (https://github.com/lowfatcode/alright-fonts , the feature/port-to-c17 branch to be precise) to convert fonts to the lighter af font. [These to be available in the environment of the students computer and be able to be invoked anywhere in the CLI]

Part 1.3: Getting started
[Explain how to get the example running that is in the example folder of the repo, transferring files to the microcontroller, running it, saving it .etc. Please make this example folder that contains a main.py, fonts folder and a gif folder and write the code for this example. The example is what is going to be changed by the student and should include a looping gif with pink scrolling text saying the liturgy against fear from dune. I shall supply the gif frames and converted af font (remember I am using a custom font so use the vector method from the docs and examples). It should be deeply commented with every line explaining what it does. 

Section 2: Background Animation

[Explain that first we are going to change the background animation. There are two options. Firstly To use a downscaled gif like the main example. Give suggestions and advise on gifs that will produce a good effect when heavily downscaled then explain how they use ffmpeg (breifly explain the importance and power of ffmpeg as an open-source project) to make the downscaled png frames and upload to the matrix driver. Secondly they could programmatically create a background animation, provide a whole other example called "alternative-example" that uses Voronoi noise to make a background]

Section 3: Text and Typography
[Explain that next we are going to change the text. They must find a ttf font from the internet, suggesting google fonts and use afinate to convert it to af. They then need to dial in the position on the screen, the size of it and what the text actually says. Suggest that they could have another line of text and how to do that]


Section 4: Further reading and references.
[List links to all the documentation this draws upon including the tools and give suggestions on where to go from here]



