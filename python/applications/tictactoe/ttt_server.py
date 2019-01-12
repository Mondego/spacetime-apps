import time, sys, ast
import spacetime
from rtypes import pcc_set, dimension, primarykey
from spacetime import Application
from datamodel import Player, Mark, Board, GameMaster
from crypto import generate_key, get_public_key, serialize_public_key, decrypt_message

def my_print(*args):
    print(*args)
    sys.stdout.flush()

WAIT_FOR_START = 5

class Game(GameMaster):
    def __init__(self, df):
        self.dataframe = df
        self.board = Board()
        self.current_players = {}
        self.turn = 0

        GameMaster.__init__(self)
        self.dataframe.add_one(GameMaster, self)
        self.dataframe.commit()

    def wait_for_players(self):
        # Delete the previous players and left over marks
        for p in self.current_players:
            self.dataframe.delete_one(Player, p)
        my_print("Marks left over: %d" % len(self.dataframe.read_all(Mark)))
        self.dataframe.delete_all(Mark)
        self.dataframe.commit()

        no_players = True
        while no_players:
            self.dataframe.checkout()
            players = self.dataframe.read_all(Player)
            if len(players) < 2:
                time.sleep(1)
                continue
            # take just the first 2
            my_print("%d players joined. Taking the first 2." % len(players))
            self.current_players = [players[0], players[1]]
            for pid, player in enumerate(self.current_players):
                player.player_id = pid
            self.current_players[self.turn].ready = True
            self.dataframe.commit()

            no_players = False
            self.board.reset()

    def wait_for_marks(self):
        ITERS_TO_QUIT = 10
        n_tries = 0
        while True:
            marks = self.dataframe.read_all(Mark)
            if (len(marks) == 0):
                n_tries = n_tries + 1
                if n_tries < ITERS_TO_QUIT:
                    yield None
                else:
                    yield marks
            else:
                n_tries = 0
                yield marks

    def play(self):
        # Players joined, start the game
        game_over = False
        wait_step = self.wait_for_marks()

        while not game_over:
            self.dataframe.checkout()

            marks = next(wait_step)
            if marks == None:
                time.sleep(1)
                continue
            elif len(marks) == 0:
                # Game over, no one placed a mark
                self.stop_game(-1)
                self.dataframe.commit()
                break

            # Take only the valid mark(s)
            marks = [m for m in marks if not m.rejected and m.player_id == self.turn]
            if (len(marks) > 0):
                mark = marks[0]
                self.decrypt_mark(mark)
                self.board.enforce(mark)
                self.board.render()
                game_over, winner = self.board.check_game_over()

                if game_over:
                    self.stop_game(winner)
                else:
                    self.current_players[self.turn].ready = False
                    self.turn = (self.turn + 1) % len(self.current_players)
                    self.current_players[self.turn].ready = True
                    my_print("It's {0}'s turn".format(self.turn))

                    if not mark.rejected: # Hide its x, y again
                        mark.x, mark.y = [-1, -1]
                    # else, mark was rejected, which means it can go public

                self.dataframe.commit()

            time.sleep(1)

    def decrypt_mark(self, mark):
        ciphertext_bytes = mark.secret_position
        pos = decrypt_message(ciphertext_bytes, self.private_key)
        my_print("position is {0}".format(pos))
        pos_list = ast.literal_eval(pos)
        mark.x, mark.y = pos_list

    def stop_game(self, winner):
        for player in self.current_players:
            player.done = True
        if winner >= 0:
            self.current_players[winner].winner = True


def ttt_server(dataframe):
    game = Game(dataframe)
    while True:
        my_print ("READY FOR NEW GAME")
        game.wait_for_players()
        game.play()
        my_print ("GAME OVER")
        time.sleep(WAIT_FOR_START)


def main(port):
    server = Application(ttt_server, server_port=port, Types=[GameMaster, Player, Mark], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    server.start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    main(port)
