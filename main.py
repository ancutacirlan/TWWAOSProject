from app import create_app
from app.import_professors import fetch_and_store_data

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        fetch_and_store_data()
    app.run(debug=True)
