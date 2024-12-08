# con4XD

This is our base game layer without AI implementation. This game requires 2 human players. This is the code for the following YouTube video: https://www.youtube.com/watch?v=8392NJjj8s0

There is also a 2nd video that includes an AI version that might be helpful: https://youtu.be/8392NJjj8s0?si=9tT9Itp7-PbWoK-n

We made 2 bomb versions:
con4XDv1 - bomb removes pieces left, right, and directly below
con4XDv2 - bomb removes pieces left, right, diagonal right, diagonal left, and directly below

#Update

The group decided to move forward with the con4XDv2 version (to include exploding diagonal pieces). Con4XDv2 became our foundation for the AI versions we created of this game:
- con4XDv2 was upgraded to a minimax A/b pruning functionality
- con4XDv2MCTS is the version that contains the MCTS search algorithm
