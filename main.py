
from dqn import *
from atari import Atari

T = 10000
UPDATE_TIME = 100

if __name__ == '__main__':
    atari = Atari('breakout.bin')
    actions = atari.legal_actions
    dqn = DQN(actions)
    state = atari.newGame()
    state = np.stack((state,state, state, state), axis=2).reshape((84,84,4))
    sess = tf.InteractiveSession()
    sess.run(tf.initialize_all_variables())
    for _ in range(T):
        action = dqn.selectAction(state)

        next_state, reward, game_over = atari.next(action)
        next_state = np.append(next_state, state, axis=2)[:,:,1:]
        dqn.storeExperience(state, action, reward, next_state, game_over)

        minibatch = dqn.sampleExperiences()
        state_batch = [experience[0] for experience in minibatch]
        nextState_batch = [experience[3] for experience in minibatch]
        action_batch = [experience[1] for experience in minibatch]
        terminal_batch = [experience[4] for experience in minibatch]
        reward_batch = [experience[2] for experience in minibatch]

        y_batch = []
        Q_batch = sess.run(dqn.targetQNet.QValue, feed_dict = {dqn.targetQNet.stateInput: nextState_batch} )
        for i in range(len(minibatch)):
            terminal = terminal_batch[i]
            if terminal:
                y_batch.append(reward_batch[i])
            else:
                y_batch.append(reward_batch[i] + GAMMA * np.max(Q_batch[i]))
        
        currentQ_batch = sess.run(dqn.currentQNet.QValue,
                                  feed_dict = {dqn.currentQNet.stateInput: state_batch })

        sess.run(dqn.trainStep, feed_dict = {dqn.yInput: y_batch, dqn.actionInput: action_batch, dqn.currentQNet.stateInput: state_batch})
 
        state = next_state

        print "Time Step %s Reward %s" % (_, reward) 

        if T % UPDATE_TIME == 0:
            sess.run(dqn.copyCurrentToTargetOperation())

