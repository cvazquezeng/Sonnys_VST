import os
from dotenv import load_dotenv
from app import create_app
from config_app import DevConfig, ProdConfig

load_dotenv()  # Load environment variables from .env file

config_class = DevConfig if os.environ.get('FLASK_ENV') == 'development' else ProdConfig

app = create_app(config_class)

if __name__ == '__main__':
    app.run(debug=True, port=5008)