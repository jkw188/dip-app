
if __name__ == "__main__":
    from dataclasses import dataclass
    @dataclass
    class MockUser:
        full_name: str = "Test Admin"
    
    app = BaseApp(MockUser())
    app.mainloop()