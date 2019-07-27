'''The Physics Node of the Game that governs the rules of the
    game and executes it smoothly.'''
# pylint: disable=duplicate-code
import time
import random
import argparse
from multiprocessing import freeze_support
from spacetime import Node
from snake_datamodel import Snake, Apple, World, Direction, FRAMETIME
from snake_bot import bot_execution
from snake_visualizer_node import visualize


WAIT_FOR_START = 5

def accepting_players(dataframe, player_count):
    ''' Accept Players and makes a lilst of them.'''
    #function for completing phase 1 of 'game_physics' function
    #Deleting all the previous snakes:
    # print("There are {} snakes.".format(len(dataframe.read_all(Snake))))
    #dataframe.delete_all(Snake)

    no_players = True
    while no_players:
        dataframe.checkout_await()
        players = dataframe.read_all(Snake)
        print(len(players))
        if len(players) >= player_count:
            return True

def initializing_apple(dataframe):
    '''Initializes Apple object and comnits it it to the Dataframe.'''
    dataframe.add_one(Apple, Apple())
    dataframe.commit()

def collision_with_boundaries(snake_head):
    '''Checks for collision with Boundaries.'''
    return (snake_head[0] >= World.display_width
            or snake_head[0] <= 0
            or snake_head[1] >= World.display_height
            or snake_head[1] <= 0)

def collision_with_snake(snakes, c_snake):
    '''Checks for collision with self, or with any other bot or player snake.'''
    if c_snake.snake_position[0] in c_snake.snake_position[1:]:
        return True
    # return any(c_snake.snake_head in snake.snake_position for snake in snakes
    # if c_snake.oid != snakes[i].oid)
    for o_snake in snakes:
        if (c_snake.oid != o_snake.oid and
                c_snake.snake_head in o_snake.snake_position):
            return True
    return False

def is_direction_blocked(c_snake, snakes):
    ''' Checks if the direction of the snake is blocked.'''
    return (collision_with_boundaries(c_snake.snake_position[0])
            or collision_with_snake(snakes, c_snake))

def generate_snake(snake, apple):
    '''Generates snake as per the assigned direction of the snake's head.'''
    if snake.direction == Direction.RIGHT:
        snake.snake_head = (snake.snake_head[0] + 1, snake.snake_head[1])
    elif snake.direction == Direction.LEFT:
        snake.snake_head = (snake.snake_head[0] - 1, snake.snake_head[1])
    elif snake.direction == Direction.DOWN:
        snake.snake_head = (snake.snake_head[0], snake.snake_head[1] + 1)
    elif snake.direction == Direction.UP:
        snake.snake_head = (snake.snake_head[0], snake.snake_head[1] - 1)

    if snake.snake_head == apple.apple_position:
        apple.reset_position()
        snake.score += 1
        snake.snake_position = [snake.snake_head] + snake.snake_position
    else:
        snake.snake_position = [snake.snake_head] + snake.snake_position
        snake.snake_position = snake.snake_position[:-1]

def play_game(dataframe):
    '''Reads Snake and Apple object from Dataframe, applies the game's running
       logic and commits the changes to the objects to the dataframe.'''
    # look at what the frame has done
    # put in dataframe checkout at the beginning and commit at the end
    # read the command dring dataframe checkout
    # once read, the command needs to be committed

    snakes = dataframe.read_all(Snake)
    apple = dataframe.read_one(Apple, 0)

    while any(not snake.crashed for snake in snakes):
        start_t = time.perf_counter()
        dataframe.checkout()
        for snake in snakes:
            if snake.crashed:
                continue
            generate_snake(snake, apple)
            snake.crashed = is_direction_blocked(snake, snakes)
        dataframe.commit()
        end_t = time.perf_counter()
        if end_t - start_t < FRAMETIME:
            time.sleep(FRAMETIME - end_t + start_t)

def game_physics(df, num_players):  # pylint: disable=invalid-name
    ''' Checkouts and commits all the players to the dataframe,
        sets up the game initially, executes each frame of the , and calls
        the 'play_game()' function to run the game in continuity.'''
    # checkout and commit
    # phase 1: accepting players
    accepting_players(df, num_players)

    # phase 2: execute each frame of the game - the first frame must set up the
    # game by placing the apple in the world and adding it to the dataframe
    initializing_apple(df)
    for i, snake in enumerate(df.read_all(Snake)):
        x_pos, y_pos = (
            random.randint(4, World.display_width - 1),
            random.randint(1, World.display_height - 1))
        snake.snake_head = (x_pos, y_pos)
        snake.snake_position = [snake.snake_head,
                                (x_pos - 1, y_pos),
                                (x_pos - 2, y_pos)]
        snake.start_game = True
        snake.assigned_player = i + 1
    df.commit()

    # print ("Ready to play the game.")
    # phase 3: when the game concludes/ends, finish it
    play_game(df)  #removed 'apple_image' parameter because that is part of the
    # 'Visualizer' Node
    # print("The Score is {}.".format(final_score))

def main(port, pcount, bcount):
    ''' Main Function!'''
    # pserver
    physics_node = Node(game_physics, server_port=port, Types=[Snake, Apple])
    physics_node.start_async(pcount + bcount)

    for _ in range(bcount):
        bot = Node(bot_execution,
                   dataframe=("127.0.0.1", port),
                   Types=[Snake, Apple])
        bot.start_async()

    visualize_node = Node(visualize,
                          dataframe=("127.0.0.1", port),
                          Types=[Snake, Apple])
    visualize_node.start_async()
    physics_node.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name
    parser.add_argument("--port",
                        type=int,
                        default=8000,
                        help="The port of the remote dataframe (default: 8000)")
    parser.add_argument("--players",
                        type=int,
                        default=1,
                        help="The number of human players playing the game.")
    parser.add_argument("--bots",
                        type=int,
                        default=1,
                        help="The number of Bot players playing the game.")
    args = parser.parse_args()  # pylint: disable=invalid-name
    freeze_support()
    main(args.port, args.players, args.bots)
