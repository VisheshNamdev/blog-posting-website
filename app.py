from website import create_app

if __name__ == "__main__":
    # Create the Flask app instance
    app = create_app()
    # Run the Flasṇk app with debug mode enabled
    app.run(debug=True)
