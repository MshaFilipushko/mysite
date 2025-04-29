# ЗдоровыйВес - Health & Weight Management Platform

A Django-based web application for health and weight management, featuring blog posts, recipes, challenges, and a community forum.

## Features

- User Profiles with BMI Calculator and Weight Progress Tracking
- Blog System with Categories and Comments
- Recipe Management with Nutritional Information
- Community Forum with Threaded Comments
- Weight Loss Challenges
- Administrative Dashboard for Content Moderation

## Technical Stack

- Django 4.2.20
- Django CKEditor 5 for Rich Text Editing
- Bootstrap 5 for Frontend
- SQLite Database
- AJAX for Dynamic Interactions
- Responsive Design

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/MshaFilipushko/mysite.git
   cd mysite
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the site at http://127.0.0.1:8000/

## Project Structure

- `weightloss/` - Main application with models, views, and templates
- `djangoProject10/` - Project settings
- `templates/` - HTML templates
- `static/` - CSS, JS, and media files
- `media/` - User-uploaded content

## License

This project is licensed under the MIT License - see the LICENSE file for details. 