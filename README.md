# Library Booking System (Flask Web Application)

This repository contains a web application developed with Python and Flask for managing books, courses, and their bookings. The application includes user authentication, role-based access control (Member/Admin), a dashboard, and basic statistics.

This project was originally developed during a curricular internship and later served as the practical basis for my Bachelor's thesis in Computer Science.

## 🛠️ Context & Technical Challenges
* **The Challenge:** The original application was fully developed in Laravel. Due to unexpected infrastructure and platform constraints at the end of the internship, I had to completely refactor and rewrite the entire backend using Flask.
* **The Constraints:** I had a hard deadline of **only one month** to complete the rewrite while ensuring all core features remained stable.
* **The Result:** To respect the tight academic deadline, some structural compromises were made. However, the application was successfully delivered, fully functional, and approved for the final thesis.

## Features
* **Authentication:** Secure user login and registration system.
* **Role-Based Access Control:** Separate interfaces and permissions for Members and Admins.
* **Book & Course Management:** Full CRUD operations for library resources.
* **Booking System:** Interactive system for members to reserve books and courses.
* **Statistics:** A simple dashboard showing top visited and downloaded items.

## Technologies Used
* **Backend:** Python (3.8+) & Flask
* **Database:** MySQL
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap, Font Awesome

## Project Structure
```text
Application/  
├── static/  
│   ├── styles.css  
│   └── img_logo.png  
├── templates/  
│   ├── index.html  
│   ├── ...  
│   └── welcome.html  
├── app.py  
├── requirements.txt  
└── Procfile
```

## Future Improvements
* Refactor the project architecture to implement better design patterns (e.g., Blueprints in Flask).
* Optimize database queries and error handling.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
