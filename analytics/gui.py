import wx
from summarise import pre_process()

class MyFrame(wx.Frame):    
    def __init__(self):
        super().__init__(
            parent=None,
            title='Rugby Analytics Tool v0.1',
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), # Prevent resizing
            size=(500,500) # Set overall frame size
        )
        panel = wx.Panel(self) # Create background panel
        
        # Add process data button
        process_data_btn = wx.Button(panel, label='Process Data', pos=(5,5)) 
        process_data_btn.Bind(wx.EVT_BUTTON, self.process_data)

        run_btn = wx.Button(panel, label='Run') # Add process data button
        run_btn.Bind(wx.EVT_BUTTON, self.run_calc)

        self.Show()


    def process_data(self, event):
        
    

    def run_calc(self, event):
        value = self.text_ctrl.GetValue()
        if not value:
            print("You didn't enter anything!")
        else:
            print(f'You typed: "{value}"')

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()