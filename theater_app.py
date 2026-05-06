'''main application file for the theater control app'''
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
