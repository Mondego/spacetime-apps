'''Runs the Human Player Snakes.'''
# pylint: disable=duplicate-code
import argparse
import curses
from curses import wrapper
from threading import Thread
from spacetime import Node
from snake_datamodel import Snake, Apple, Direction
from snake_visualizer_node import draw_border, visualize_frames


def player_execution(df):  # pylint: disable=invalid-name
    '''Wraps the player client so that curses can be run.'''
    wrapper(player_client, df)

def init_player(df):  # pylint: disable=invalid-name
    ''' Initializes 'snake' object and commits and pushes it to the
        Dataframe. '''
    snake = Snake()
    df.add_one(Snake, snake)
    df.commit()
    df.push()
    return snake

def player_client(stdscr, df):  # pylint: disable=invalid-name
    ''' Waits for the player to start the game and sets the color
        combination of the borders.'''
    curses.start_color()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    draw_border(stdscr)
    snake = init_player(df)
    while not snake.start_game:
        df.pull_await()

    # Ask the player to press any key to continue
    input_thread = Thread(
        target=take_user_input, args=(stdscr, df, snake), daemon=True)
    vis_thread = Thread(
        target=visualize_frames, args=(stdscr, df), daemon=True)

    vis_thread.start()
    input_thread.start()

    input_thread.join()
    vis_thread.join()

def parse_key(key, snake):
    '''Takes in user input via UP, DOWN RIGHT, LEFT keys. '''
    if key == 27:  #if key is ESC
        snake.crashed = True
    elif key == 260 and snake.direction != Direction.RIGHT:
        # if key is LEFT Arrow
        snake.set_button_direction(Direction.LEFT)
    elif key == 261 and snake.direction != Direction.LEFT:
        # if key is RIGHT Arrow
        snake.set_button_direction(Direction.RIGHT)
    elif key == 259 and snake.direction != Direction.DOWN:
        # if key is UP Arrow
        snake.set_button_direction(Direction.UP)
    elif key == 258 and snake.direction != Direction.UP:
        # if key is DOWN Arrow
        snake.set_button_direction(Direction.DOWN)

def take_user_input(stdscr, df, snake):  # pylint: disable=invalid-name
    ''' Pushes pressed key number to the Dataframe. '''
    while snake.crashed is not True:
        key = stdscr.getch()
        parse_key(key, snake)
        df.commit()
        df.push()

def main(address, port):
    '''Main Function!'''
    player_node = Node(
        player_execution, dataframe=(address, port), Types=[Snake, Apple])
    player_node.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name
    parser.add_argument(
        "--port", type=int,
        default=8000, help="The port of the remote dataframe (default: 8000)")
    parser.add_argument(
        "--address", type=str,
        default="127.0.0.1", help="The address of the server.")

    args = parser.parse_args()  # pylint: disable=invalid-name
    main(args.address, args.port)
