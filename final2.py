import wx
import random

class NumberWordleGame(wx.Frame):
    def __init__(self): 
        super().__init__(parent=None, title='Code Guesser Game (4 Digits)')
        self.max_guesses = 6
        self.init_vars()
        self.init_ui()
        self.Center()
        self.Show()

    def init_vars(self):
        # fresh game
        self.code = self.generate_code()      
        self.current_guess_row = 0
        self.current_guess_text = []

    def generate_code(self):
        digits = list('0123456789')
        random.shuffle(digits)
        return "".join(digits[:4])

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        instructions = wx.StaticText(
            panel,
            label="Guess the 4-digit code in 6 tries (unique digits)."
        )
        instructions.Wrap(400)
        vbox.Add(instructions, flag=wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, border=15)
        
        self.game_font = wx.Font(
            16, wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )

        # Grid (6x4) 
        grid_panel = wx.Panel(panel)
        grid_sizer = wx.GridSizer(rows=self.max_guesses, cols=4, hgap=5, vgap=5)
        
        self.grid_buttons = []
        for r in range(self.max_guesses):
            row_buttons = []
            for c in range(4):
                btn = wx.Button(grid_panel, label="", size=(60, 60))
                btn.Disable()
                btn.SetFont(self.game_font)
                row_buttons.append(btn)
                grid_sizer.Add(btn, 0, wx.EXPAND)
            self.grid_buttons.append(row_buttons)
        
        grid_panel.SetSizer(grid_sizer)
        vbox.Add(grid_panel, flag=wx.CENTER | wx.TOP | wx.BOTTOM, border=10)

        # Enable first row for the initial game
        for btn in self.grid_buttons[0]:
            btn.Enable()

        # Keyboard 0–9 
        keyboard_panel = wx.Panel(panel)
        keyboard_sizer = wx.GridSizer(rows=2, cols=5, hgap=5, vgap=5)
        self.keyboard_buttons = {}

        for i in range(10):
            btn = wx.Button(keyboard_panel, label=str(i))
            btn.Bind(wx.EVT_BUTTON, self.on_number_button)
            btn.SetFont(self.game_font)
            self.keyboard_buttons[str(i)] = btn
            keyboard_sizer.Add(btn, 0, wx.EXPAND)
        
        keyboard_panel.SetSizer(keyboard_sizer)
        vbox.Add(keyboard_panel, flag=wx.CENTER | wx.TOP | wx.BOTTOM, border=10)

        # Action buttons + Help (all same size, help beside New Game)
        hbox_actions = wx.BoxSizer(wx.HORIZONTAL)

        btn_size = (110, 40)  # common size for all bottom buttons

        self.clear_button = wx.Button(panel, label='Clear', size=btn_size)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear)

        self.submit_button = wx.Button(panel, label='Submit', size=btn_size)
        self.submit_button.Bind(wx.EVT_BUTTON, self.on_submit)

        self.newgame_button = wx.Button(panel, label='New Game', size=btn_size)
        self.newgame_button.Bind(wx.EVT_BUTTON, self.on_new_game)

        self.help_button = wx.Button(panel, label='?', size=btn_size)
        self.help_button.SetFont(wx.Font(
            18, wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))
        self.help_button.Bind(wx.EVT_BUTTON, self.on_help)

        hbox_actions.Add(self.clear_button, 0, wx.ALL, 5)
        hbox_actions.Add(self.submit_button, 0, wx.ALL, 5)
        hbox_actions.Add(self.newgame_button, 0, wx.ALL, 5)
        hbox_actions.Add(self.help_button, 0, wx.ALL, 5)

        vbox.Add(hbox_actions, flag=wx.CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.statusbar = self.CreateStatusBar()
        self.update_status()

        panel.SetSizer(vbox)
        self.Layout()

    def on_help(self, event):
        """Show rules popup"""
        rules = (
            "Code Guesser Rules:\n\n"
            "• Guess a 4-digit code using digits 0-9 (unique digits only)\n"
            "• You have 6 attempts\n"
            "• After each guess:\n"
            "  • GREEN = correct digit in correct position\n"
            "  • YELLOW = correct digit in wrong position\n"
            "  • GREY = digit not in code\n"
            "• Keyboard colors update to show which digits are available\n"
            "• Good luck!"
        )
        
        dlg = wx.MessageDialog(
            self, 
            rules, 
            "Game Rules", 
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()

    def update_status(self):
        self.statusbar.SetStatusText(f"Guess {self.current_guess_row + 1} of {self.max_guesses}")

    def on_number_button(self, event):
        if len(self.current_guess_text) < 4:
            digit = event.GetEventObject().GetLabel()
            if digit not in self.current_guess_text:
                self.current_guess_text.append(digit)
                self.update_current_row_display()
            else:
                wx.MessageBox("Digits must be unique.", "Invalid Input",
                              wx.OK | wx.ICON_WARNING)

    def on_clear(self, event):
        if self.current_guess_text:
            self.current_guess_text.pop()
            self.update_current_row_display()

    def update_current_row_display(self):
        row_buttons = self.grid_buttons[self.current_guess_row]
        for i in range(4):
            if i < len(self.current_guess_text):
                row_buttons[i].SetLabel(self.current_guess_text[i])
            else:
                row_buttons[i].SetLabel("")

    def on_submit(self, event):
        if len(self.current_guess_text) != 4:
            wx.MessageBox("Please enter 4 digits.", "Invalid Input",
                          wx.OK | wx.ICON_WARNING)
            return
        guess_str = "".join(self.current_guess_text)
        self.evaluate_guess(guess_str)

    def evaluate_guess(self, guess):
        row_buttons = self.grid_buttons[self.current_guess_row]
        green_count = 0

        # greens
        for i in range(4):
            if guess[i] == self.code[i]:
                color = wx.GREEN
                row_buttons[i].SetBackgroundColour(color)
                row_buttons[i].SetForegroundColour(wx.BLACK)
                self.update_keyboard_color(guess[i], color)
                green_count += 1

        # yellows / greys
        for i in range(4):
            if row_buttons[i].GetBackgroundColour() == wx.GREEN:
                continue
            if guess[i] in self.code:
                color = wx.YELLOW
            else:
                color = wx.LIGHT_GREY
            row_buttons[i].SetBackgroundColour(color)
            row_buttons[i].SetForegroundColour(wx.BLACK)
            self.update_keyboard_color(guess[i], color)

        self.Layout()
        self.Refresh()
        self.Update()

        if green_count == 4:
            self.game_over(True)
        else:
            self.next_turn()

    def update_keyboard_color(self, digit, new_color):
        btn = self.keyboard_buttons[digit]
        current_color = btn.GetBackgroundColour()

        if new_color == wx.GREEN:
            btn.SetBackgroundColour(wx.GREEN)
            btn.SetForegroundColour(wx.BLACK)
        elif new_color == wx.YELLOW and current_color != wx.GREEN:
            btn.SetBackgroundColour(wx.YELLOW)
            btn.SetForegroundColour(wx.BLACK)
        elif new_color == wx.LIGHT_GREY and current_color == wx.NullColour:
            btn.SetBackgroundColour(wx.LIGHT_GREY)
            btn.SetForegroundColour(wx.BLACK)

        btn.Refresh()
        btn.Update()

    def next_turn(self):
        self.current_guess_row += 1
        self.current_guess_text = []
        if self.current_guess_row >= self.max_guesses:
            self.game_over(False)
        else:
            for btn in self.grid_buttons[self.current_guess_row]:
                btn.Enable()
            self.update_status()

    def game_over(self, won):
        # Disable input
        self.submit_button.Disable()
        self.clear_button.Disable()
        for btn in self.keyboard_buttons.values():
            btn.Disable()

        # Congratulations box
        if won:
            self.statusbar.SetStatusText("You won the game!")
            title = "You Win!"
            text = f"🎉 Congratulations! 🎉\n\nYou cracked the code:\n\n    {self.code}\n"
        else:
            self.statusbar.SetStatusText("Game Over.")
            title = "You Lose"
            text = f"Game Over.\n\nThe code was:\n\n    {self.code}"

        dlg = wx.Dialog(self, title=title, style=wx.DEFAULT_DIALOG_STYLE & ~wx.RESIZE_BORDER)

        vbox = wx.BoxSizer(wx.VERTICAL)

        msg = wx.StaticText(dlg, label=text)
        msg.Wrap(300)
        vbox.Add(msg, flag=wx.ALL | wx.ALIGN_CENTER, border=15)

        btn_ok = wx.Button(dlg, wx.ID_OK, "OK")
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_ok, flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        vbox.Add(btn_sizer, flag=wx.ALIGN_CENTER)

        dlg.SetSizer(vbox)
        dlg.Fit()
        dlg.CentreOnParent()

        dlg.ShowModal()
        dlg.Destroy()

    def on_new_game(self, event):
        # 1) Fresh state (new code + reset counters)
        self.init_vars()

        # 2) Reset grid: labels, colours, disable all
        for row_buttons in self.grid_buttons:
            for btn in row_buttons:
                btn.SetLabel("")
                btn.SetBackgroundColour(wx.NullColour)
                btn.SetForegroundColour(wx.BLACK)
                btn.Disable()

        # 3) Enable first row for the new round
        for btn in self.grid_buttons[0]:
            btn.Enable()

        # 4) Reset keyboard (colours + enable)
        for btn in self.keyboard_buttons.values():
            btn.SetBackgroundColour(wx.NullColour)
            btn.SetForegroundColour(wx.BLACK)
            btn.Enable()

        # 5) Reset controls and status
        self.submit_button.Enable()
        self.clear_button.Enable()
        self.current_guess_text = []
        self.update_status()

        self.Layout()
        self.Refresh()
        self.Update()

if __name__ == '__main__':
    app = wx.App(False)
    frame = NumberWordleGame()
    app.MainLoop()
