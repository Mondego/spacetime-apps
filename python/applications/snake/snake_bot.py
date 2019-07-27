'''Runs the Bot Snakes.'''
# pylint: disable=duplicate-code
import time
import math
import argparse
from spacetime import Node
from snake_datamodel import Snake, Apple, Direction, FRAMETIME


def init_bot(df):  # pylint: disable=invalid-name
    '''Initializes Snake object and commits is to the dataframe.'''
    snake = Snake()
    df.add_one(Snake, snake)
    df.commit()
    df.push()
    return snake

def bot_execution(df):  # pylint: disable=invalid-name
    '''Executes loop to run the bot snake in the game.'''
    snake = init_bot(df)
    while not snake.start_game:
        df.pull_await()

    defeat_player(df, snake)

def set_key(key, snake):
    '''Sets the key direction of the bot snake.'''
    if key is not snake.direction:
        snake.set_direction(key)

def defeat_player(df, snake):  # pylint: disable=invalid-name
    '''Executes the loop for making the decision of direction and
        commits it to the dataframe.'''
    for key in make_decision(df, snake):
        set_key(key, snake)
        df.commit()
        df.push_await()
        df.pull_await()

def predict_snake_head(snake, p_direction):
    '''Predicts the next optimal direction for the bot snake.'''
    snake_head_local = snake.snake_head
    if p_direction == Direction.RIGHT:
        snake_head_local = (snake_head_local[0] + 1, snake_head_local[1])
    elif p_direction == Direction.LEFT:
        snake_head_local = (snake_head_local[0] - 1, snake_head_local[1])
    elif p_direction == Direction.DOWN:
        snake_head_local = (snake_head_local[0], snake_head_local[1] + 1)
    elif p_direction == Direction.UP:
        snake_head_local = (snake_head_local[0], snake_head_local[1] - 1)
    return snake_head_local

def make_decision(df, snake):  # pylint: disable=invalid-name
    '''Makes the decision of the next direction the snake should go in based
       on the minimum distance between the snake's head and the apple among all
       the possible directions/'''

    directions = {
        Direction.LEFT: [Direction.UP, Direction.DOWN, Direction.LEFT],
        Direction.RIGHT: [Direction.UP, Direction.DOWN, Direction.RIGHT],
        Direction.UP: [Direction.LEFT, Direction.RIGHT, Direction.UP],
        Direction.DOWN: [Direction.LEFT, Direction.RIGHT, Direction.DOWN],
    }

    apple = df.read_one(Apple, 0)
    final_direction = snake.direction  # setting the final direction to be

    # equal to existing direction by default

    while not snake.crashed:
        min_dist = 10000
        start_t = time.perf_counter()
        possible_directions = directions[snake.direction]

        # Now computing which direction to go to in order to reach the apple
        for direction in possible_directions:
            s_h_l = predict_snake_head(snake, direction)
            # 's_h_l' stands for snake head local position predicted by the
            # possible directions of the snake
            dist = math.sqrt(pow((apple.apple_position[0] - s_h_l[0]), 2) +
                             pow((apple.apple_position[1] - s_h_l[1]), 2))

            if min_dist > dist and s_h_l not in snake.snake_position[:-1]:
                min_dist = dist
                final_direction = direction

        yield final_direction

        end_t = time.perf_counter()
        if (end_t - start_t) < FRAMETIME:
            time.sleep(FRAMETIME - end_t + start_t)

def main(address, port, bcount):
    '''Main Function!'''
    for _ in range(bcount):
        bot = Node(bot_execution, dataframe=(address, port), Types=[Snake, Apple])
    bot.start_async()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name
    parser.add_argument("--port",
                        type=int,
                        default=8000,
                        help="The port of the remote dataframe (default: 8000)")
    parser.add_argument("--bots",
                        type=int,
                        default=1,
                        help="The number of Bot players playing the game.")
    parser.add_argument("--address",
                        type=str,
                        default="127.0.0.1",
                        help="The address of the server.")

    args = parser.parse_args()  # pylint: disable=invalid-name
    main(args.address, args.port, args.bots)
