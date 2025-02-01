class ChatWindow:
    def __init__(self, master, model):
        self.master = master
        self.model = model
        self.master.title("Chat with LLM")
        
        self.chat_frame = Frame(self.master)
        self.chat_frame.pack(padx=10, pady=10)

        self.text_area = Text(self.chat_frame, wrap='word', state='disabled', width=50, height=20)
        self.text_area.pack(side=TOP, fill=BOTH, expand=True)

        self.entry = Entry(self.chat_frame, width=50)
        self.entry.pack(side=LEFT, padx=(0, 10), pady=(10, 0))
        self.entry.bind("<Return>", self.send_message)

        self.send_button = Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=RIGHT, pady=(10, 0))

    def send_message(self, event=None):
        user_input = self.entry.get()
        if user_input:
            self.display_message("You: " + user_input)
            self.entry.delete(0, END)
            response = self.get_model_response(user_input)
            self.display_message("Model: " + response)

    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(END, message + "\n")
        self.text_area.config(state='disabled')
        self.text_area.see(END)

    def get_model_response(self, user_input):
        # Placeholder for model interaction logic
        return "This is a response from the model."  # Replace with actual model response logic