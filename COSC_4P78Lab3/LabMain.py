import serial
import tkinter as tk

#ssc32 = serial.Serial('/dev/ttyS0', 115200)
ssc32 = serial.Serial('COM4', 115200)
step_size=10

# Define default values
defaults = {
    "base": 1500,
    "shoulder": 2150,
    "elbow": 2150,
    "wrist": 1300,
    "rotate": 1400,
    "grip": 1000
}
fields = {
    "base": "#0 P",
    "shoulder": "#1 P",
    "elbow": "#2 P",
    "wrist": "#3 P",
    "rotate": "#4 P",
    "grip": "#5 P"
}

def increment(entry):
    try:
        value = int(entry.get())
    except:
        value = 0
    entry.delete(0, tk.END)
    entry.insert(0, str(value + step_size))
    display()

def decrement(entry):
    try:
        value = int(entry.get())
    except:
        value = 0
    entry.delete(0, tk.END)
    entry.insert(0, str(value - step_size))
    display()
def display_output(output_field, text):
    output_field.delete(0, tk.END)
    output_field.insert(0, text)

def display():
    values = [f"{fields[label]}{entry.get()}" for label, entry in entries.items()]
    display_output(output_field, " ".join(values)+" T1000")

def send():
    ssc32.write( (output_field.get()+"\r").encode() )

def read():
    try:
        ssc32.write(b"Q\r")  # ask for status
        root.after(50, read_response)  # wait a bit
    except Exception as e:
        print("Read error:", e)

def read_response():
    if ssc32.in_waiting > 0:
        data = ssc32.read(ssc32.in_waiting).decode(errors='ignore').strip()
        print("SSC32:", data)
        display_output(output_field, data)

def home():
    for label,entry in entries.items():
        entry.delete(0,tk.END)
        entry.insert(0,str(defaults[label]))
    display()
    send()

# --------------------------TIk TAK TOE-----------------------------

def print_board(board):
    for row in board:
        print(' | '.join(row))
        print('-' * 9)

def get_player_move(player, board):
    while True:
        move = input(f"Player {player}'s turn. Enter row (1-3) and column (1-3) separated by a space: ")
        try:
            row, col = map(int, move.split())
            row -= 1
            col -= 1
            print(row, " ", col)
            if 0 <= row < 3 and -1 <= col < 3 and board[row][col] =='':
                return row, col
            else:
                print("Invalid move. Try again.")
        except ValueError:
            print("Invalid input. Please enter two numbers separated by a space.")

def minimax(board, is_maximizing):
    result = evaluate(board)
    
    # Terminal states
    if result is not None:
        return result  # e.g. +1 (AI win), -1 (player win), 0 (draw)

    if is_maximizing:
        best_score = -float('inf')
        for r in range(3):
            for c in range(3):
                if board[r][c] == 0:
                    board[r][c] = 2  # AI move
                    score = minimax(board, False)
                    board[r][c] = 0  # undo move
                    best_score = max(best_score, score)
        return best_score
    else:
        best_score = float('inf')
        for r in range(3):
            for c in range(3):
                if board[r][c] == 0:
                    board[r][c] = 1  # Player move
                    score = minimax(board, True)
                    board[r][c] = 0  # undo move
                    best_score = min(best_score, score)
        return best_score

def ai_move(board):
    best_score = -float('inf')
    move = (None, None)

    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:
                board[r][c] = 2  # AI move
                score = minimax(board, False)
                board[r][c] = 0  # undo

                if score > best_score:
                    best_score = score
                    move = (r, c)

    return move

# put in a copy of board ai with an ai move, and evaluate
def evaluate(board, player = 2):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != 0:
            return 10 if row[0] == player else -10

        for col in range(3): 
            if board[0][col] == board[1][col] == board[2][col] and board[0][col] != 0:
                return 10 if board[0][col] == player else -10

        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != 0:
            return 10 if board[0][0] == player else -10

        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != 0:
            return 10 if board[0][2] == player else -10
    return None

def check_winner(board, player):
    for row in board:
        if all(cell == player for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)) or all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

def play_game():
    board = [['','',''], ['','',''], ['','','']]
    board_ai = [[0,0,0], [0,0,0], [0,0,0]] # 1 is player 1 and 2 is player 2 (or AI)
    current_player = 'X'
    while True:
        print_board(board)
        if current_player == 'O':
            row, col = get_player_move(current_player, board)
        else:
            row, col = ai_move(board_ai) # 2 is ai value move
        board[row][col] = current_player
        board_ai[row][col] = 1 if current_player == 'O' else 2
        if check_winner(board, current_player):
            print_board(board)
            print(f"Player {current_player} wins!")
            break
        elif all(board[i][j]!='' for i in range(3) for j in range(3)):
            print_board(board)
            print("It's a draw!")
            break
        current_player = 'O' if current_player == 'X' else 'X'

# play_game()
# --------------------------------------------------------------------------------------

root = tk.Tk()
root.title("Numeric Input GUI")

entries = {}

# Create the home button
home_button = tk.Button(root, text="Home", command=lambda: home())
home_button.pack(pady=5)

# Create the input fields with + and - buttons
for label, default_value in defaults.items():
    frame = tk.Frame(root)
    frame.pack(pady=2, anchor="w")

    label_widget = tk.Label(frame, text=label.capitalize() + ":", width=10, anchor="w")
    label_widget.pack(side=tk.LEFT, padx=5)

    minus_button = tk.Button(frame, text="-", width=3, command=lambda l=label: decrement(entries[l]))
    minus_button.pack(side=tk.LEFT)

    entry = tk.Entry(frame, width=5, justify=tk.CENTER)
    entry.insert(0, str(default_value))
    entry.pack(side=tk.LEFT, padx=5)
    entries[label] = entry

    plus_button = tk.Button(frame, text="+", width=3, command=lambda l=label: increment(entries[l]))
    plus_button.pack(side=tk.LEFT)

# Create the read button
read_button = tk.Button(root, text="Read", command=lambda: read())
read_button.pack(pady=5)

# Create the send button
send_button = tk.Button(root, text="Send to Arm", command=lambda: send())
send_button.pack(pady=10)

# Create the output field
output_field = tk.Entry(root, width=60, justify=tk.LEFT)
output_field.pack(pady=10)

display()

# Run the main loop
root.mainloop()