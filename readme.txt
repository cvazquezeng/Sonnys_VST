index.html: Provides the main interface for the stack light control system.
app.py: Sets up the Flask application and defines routes for controlling and fetching the status of the stack lights.
login.html: Provides a login interface for the user.
forms.py: Defines the login form using Flask-WTF.
models.py: Defines the User class for session management with Flask-Login.
script.js: Handles the dynamic functionality of the interface, such as fetching statuses, updating the image, and handling button clicks.
Key Points to Note:
The script.js is essential for the dynamic interaction on the front end, making the interface responsive and interactive.
The application ensures security and session management using Flask-Login.
The backend communicates with a stack light system using Modbus TCP, handling light control and status fetching.


docker-compose down && \
docker volume prune -f && \
docker image prune -f && \
docker-compose up --build -d

