# Library Booking System (Flask Web Application)

> **Note**
>
> This repository contains the original Flask version of my university internship project, which later became the practical basis for my Bachelor's thesis in Computer Science.
>
> The project is no longer actively developed. A complete redesign and modernization of the application is available in **BiblioAgent** (see my GitHub profile).

This repository contains a web application developed with Python and Flask for managing books, courses, and their bookings. The application includes user authentication, role-based access control (Member/Admin), a dashboard, and basic statistics.

Although this version successfully fulfilled the internship and thesis requirements, it was developed under strict time constraints and therefore prioritizes functionality over architecture and maintainability.

## 🛠️ Context & Technical Challenges

- **Original development:** The application was initially implemented in Laravel during my curricular internship.
- **Unexpected rewrite:** Due to infrastructure and platform constraints near the end of the internship, I had to completely rewrite the backend using Flask.
- **Time constraints:** The entire migration had to be completed in approximately **one month**, while preserving the original functionality.
- **Outcome:** The application was successfully completed, presented, and approved as part of my Bachelor's thesis.

## Features

- Secure authentication system
- Role-based access control (Member/Admin)
- Book and course management
- Booking system
- Basic dashboard with statistics

## Technologies Used

- **Backend:** Python 3 & Flask
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap, Font Awesome

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

## Lessons Learned

Developing this project under a tight deadline taught me the importance of:

- planning a scalable architecture from the beginning;
- separating application logic into reusable modules;
- using Flask Blueprints and a cleaner project structure;
- improving database design and code maintainability.

These lessons directly inspired the development of my later project, **BiblioAgent**, which redesigns the application with a more modular architecture, an improved user interface, and additional functionality.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
