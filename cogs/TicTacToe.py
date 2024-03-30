import discord
from discord.ext import commands
import asyncio

class TicTacToe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games = {}

    @commands.command()
    async def ttt(self, ctx, opponent: discord.Member):
        if ctx.author == opponent:
            await ctx.send("You can't play against yourself!")
            return

        if opponent.id in self.games:
            await ctx.send("This player is already in a game.")
            return

        # Initialize a new game
        self.games = {
            'player1': ctx.author,
            'player2': opponent,
            'board': [' ' for _ in range(9)],
            'turn': ctx.author,
            'winner': None
        }

        await ctx.send(f"Game started between {ctx.author.mention} and {opponent.mention}! Use `$move <position>`(from 1~9) to make your move.")
        await ctx.send(f"{ctx.author}'s turn! ")

    @commands.command()
    async def move(self, ctx, position: int):
        game = self.games

        
        # if ctx.author != game['turn']:
        #     await ctx.send("It's not your turn.")
        #     return
        if position < 1 or position > 9 or game['board'][position - 1] != ' ':
            await ctx.send("Invalid move. Please choose an empty position between 1 and 9.")
            return

        if game['turn'] == game['player1']:
            symbol = 'X'
        else:
            symbol = 'O'

        game['board'][position - 1] = symbol

        winner = self.check_winner(game['board'])
        
        if winner:
            await ctx.send(winner)
            game['winner'] =game['player1'] if winner == 'X' else game['player2']
            await ctx.send(f"{self.display_board(game['board'])}")
            await ctx.send(f"{game['winner'].mention} wins!")
            return

        if ' ' not in game['board']:
            await ctx.send("It's a tie!\n" + self.display_board(game['board']))
            return

        game['turn'] = game['player2'] if game['turn'] == game['player1'] else game['player1']
        await ctx.send(f"{game['turn'].mention}'s turn.\n{self.display_board(game['board'])}")

    def check_winner(self, board):
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for combo in winning_combinations:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
                return board[combo[0]]
        return None

    def display_board(self, board):
        return f"```{board[0]} | {board[1]} | {board[2]}\n---------\n{board[3]} | {board[4]} | {board[5]}\n---------\n{board[6]} | {board[7]} | {board[8]}```"
    

async def setup(bot: commands.Bot):
    await bot.add_cog(TicTacToe(bot))