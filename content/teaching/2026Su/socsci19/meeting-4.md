---
title: "Meeting 4"
term: "Summer 2026"
description: "AI Literacy meeting 4 — bias in hiring algorithms and the neural net playground."
---

## Meeting 4

Get a virtual background.

Do the activities in groups of 3-5.

## Virtual Background

These images each represent one aspect of AI classification or recommendation
systems

![Adversarial images](/teaching/2026Su/socsci19/adversarial.jpg)

"Adversarial images" that fool AI but are unnoticeable to humans

![Deep Dream](/teaching/2026Su/socsci19/deepdream.jpg)

"Deep Dream"'s interpretation of how neural nets process images

![Doctor and nurse images](/teaching/2026Su/socsci19/genderbias.jpg)

Humans and AI can both pick up the wrong cues from training data (e.g., gender
rather than uniform, to distinguish nurses and doctors)

![Recommendation feed](/teaching/2026Su/socsci19/recommendations.jpg)

Recommendation algorithms quickly learn a human's preferences by seeing how long
they watch

## First activity: AI bias

Each of you should the activity at this site:
<https://www.survivalofthebestfit.com/game/>

After you are done, talk with your group about what happened, and how things
might have gone differently

When you're ready, move on to the second activity

## Second activity: Neural net playground

Go to the
[neural net playground](https://playground.tensorflow.org/#activation=sigmoid&batchSize=10&dataset=xor&regDataset=reg-gauss&learningRate=0.03&regularizationRate=0&noise=0&networkShape=8,7&seed=0.16126&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false&regularization_hide=true&batchSize_hide=true&learningRate_hide=true&regularizationRate_hide=true&discretize_hide=true&problem_hide=true&percTrainData_hide=true).
This page shows an untrained neural net. You can see how many layers there are,
and how many neurons in each layer, and what the random weights are connecting
the neurons (the orange and blue lines). Hit play, and watch the weights change
as the neural net learns to identify the training data (the bright colored dots
in the square on the right). The background of that square identifies what the
neural net "thinks" at any point in the training, and each neuron shows what it
"represents".

Try adding and subtracting neurons and layers, or switching between the four
training datasets (the orange and blue bullseye, two separate circles, four
squares, and spirals, on the left) and then run it again. Talk to each other
about what is working and what isn't working.

Which datasets does it learn well (get the "Training loss" down below 0.01)?
Which datasets need more neurons or more layers? Are there any datasets it can
learn with 0 hidden layers? Are there any datasets that do better with fewer
layers than with more layers? What happens when you replace the Sigmoid
activation with ReLU?

## Third activity: Discuss this module's ideas

Open up the Canvas page for module 4 *(link removed)* to remind yourselves of the
videos for this module. Discuss these videos with each other.

Were there any ideas from any of them that you found particularly surprising, or
interesting? Were there things you didn't understand?

Look at the list of "Further watching/reading" links below the actual
assignments. Are there some that look interesting to dig into further? Are there
any you already looked at that some of the other people in your group might want
to check out?

Previous meetings: [1](/teaching/2026Su/socsci19/meeting-1/)
[2](/teaching/2026Su/socsci19/meeting-2/)
[3](/teaching/2026Su/socsci19/meeting-3/)

[Back to AI Literacy](/teaching/2026Su/socsci19/){: .button }
