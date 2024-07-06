#  Display Data from a Web API + Cloud Deployment Demo

<img width="1438" alt="Screenshot 2024-07-06 at 7 24 22 PM" src="https://github.com/aaryamaster/Online-BookStore/assets/75297750/98ad73ee-fad3-46c2-a050-83473cfe72bf">

## Open Visual Studio Code and select Create a new project

1. Select **Python Application** and click **Next**.
2. Configure your new project:
   - **Project name**: `OnlineBookStore`
   - **Location**: Choose your desired directory
   - Click **Create**

## Set Up Flask Application

### Create a Virtual Environment

1. Open your terminal and navigate to your project directory.
2. Run the following command to create a virtual environment:

    ```bash
    python -m venv venv
    ```
3. Activate the virtual environment:

    **Windows:**

    ```bash
    .\venv\Scripts\activate
    ```

    **macOS/Linux:**

    ```bash
    source venv/bin/activate
    ```

4. Install Flask within the virtual environment:

    ```bash
    pip install flask
    ```



### Create the Flask App

1. In `app.py`, add the following code:
 
  
```
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://aarya:aarya123@/book?unix_socket=/cloudsql/online-bookstore-428523:us-central1:bookstore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Set your secret key for sessions
db = SQLAlchemy(app)


```

# Define the Book model
```
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)  # DECIMAL type for precise monetary values

    def __repr__(self):
        return f'<Book {self.id}, {self.title}>'
```

# Create all tables based on defined models
```
with app.app_context():
    db.create_all()

```

# Routes
```
@app.route('/')
def index():
    try:
        books = Book.query.all()
        return render_template('index.html', books=books)
    except Exception as e:
        flash(f"Error retrieving books: {str(e)}", 'error')
        return render_template('index.html', books=[])

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        price_str = request.form['price']
        
        try:
            price = Decimal(price_str.strip('$'))
        except ValueError:
            flash('Invalid price format. Please enter a valid price.', 'error')
            return redirect(url_for('add_book'))
        
        new_book = Book(title=title, author=author, description=description, price=price)

        try:
            db.session.add(new_book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding book: {str(e)}", 'error')

    return render_template('add_book.html')


@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    try:
        book = Book.query.get_or_404(id)
        return render_template('book_detail.html', book=book)
    except Exception as e:
        flash(f"Error retrieving book details: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/books/<int:id>/edit', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)

    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.description = request.form['description']
        
        try:
            price_str = request.form['price']
            book.price = Decimal(price_str.strip('$'))
        except ValueError:
            flash('Invalid price format. Please enter a valid price.', 'error')
            return redirect(url_for('edit_book', id=id))
        
        try:
            db.session.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('get_book', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating book: {str(e)}", 'error')

    return render_template('edit_book.html', book=book)

@app.route('/books/<int:id>/delete', methods=['POST'])
def delete_book(id):
    try:
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting book: {str(e)}", 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


```




### Create Template Folder

1. In the project directory, create a folder named `templates`.
2. Inside `templates`, create five files: `index.html` `add_book.html` `base.html` `book_detail.html` and `edit_book.html`.

## Create index.html
```
{% extends "base.html" %}

{% block content %}
    <h1 class="text-center mb-4">Bookstore</h1>
    <a href="{{ url_for('add_book', id=-1) }}" class="btn btn-success mb-4">Add Book</a>
    <table class="table table-striped table-responsive">
        <thead>
            <tr>
                <th>Title</th>
                <th>Author</th>
                <th>Description</th>
                <th>Price</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for book in books %}
            <tr>
                <td>{{ book.title }}</td>
                <td>{{ book.author }}</td>
                <td>{{ book.description }}</td>
                <td>{{ book.price }}</td>
                <td>
                    <a href="{{ url_for('edit_book', id=book.id) }}" class="btn btn-warning btn-sm mr-2">Edit</a>
                    <form action="{{ url_for('delete_book', id=book.id) }}" method="post" style="display:inline;">
                        <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
{% endblock %}

```

## Create add_book.html

```
{% extends "base.html" %}

{% block title %}Add Book{% endblock %}

{% block content %}
    <h1>Add Book</h1>
    <form action="{{ url_for('add_book') }}" method="post">
        <div class="mb-3">
            <label for="title" class="form-label">Title</label>
            <input type="text" class="form-control" id="title" name="title" required>
        </div>
        <div class="mb-3">
            <label for="author" class="form-label">Author</label>
            <input type="text" class="form-control" id="author" name="author" required>
        </div>
        <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <textarea class="form-control" id="description" name="description"></textarea>
        </div>
        <div class="mb-3">
            <label for="price" class="form-label">Price</label>
            <input type="text" class="form-control" id="price" name="price" required>
        </div>
        <button type="submit" class="btn btn-primary">Add Book</button>
        <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancel</a>
    </form>
{% endblock %}

```

## Create base.html

```

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bookstore</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <link rel="stylesheet" href="path/to/your/custom/styles.css"> <!-- Include your custom styles file -->
    <style>
        /* Additional styles specific to this page */
        .table {
            width: 100%;
            max-width: 100%;
            margin-bottom: 1rem;
            background-color: transparent;
            table-layout: fixed; /* Change to fixed layout */
        }

        .table th,
        .table td {
            padding: 0.75rem;
            vertical-align: top;
            border-top: 1px solid #dee2e6;
            word-wrap: break-word; /* Ensure text wraps */
            overflow-wrap: break-word; /* Ensure text wraps */
        }

        .table th:nth-child(1),
        .table td:nth-child(1) {
            width: 10%; /* Adjust width of Title column */
        }

        .table th:nth-child(2),
        .table td:nth-child(2) {
            width: 10%; /* Adjust width of Author column */
        }

        .table th:nth-child(3),
        .table td:nth-child(3) {
            width: 50%; /* Adjust width of Description column */
        }

        .table th:nth-child(4),
        .table td:nth-child(4) {
            width: 10%; /* Adjust width of Price column */
        }

        .table th:nth-child(5),
        .table td:nth-child(5) {
            width: 20%; /* Adjust width of Actions column */
        }
        
        /* Adjust margin between buttons */
        .btn-edit {
            margin-right: 10px; /* Adjust the amount of space as needed */
        }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>


```

## Create book_detail.html

```
{% extends "base.html" %}

{% block title %}{{ book.title }} - Bookstore{% endblock %}

{% block content %}
    <h1>{{ book.title }}</h1>
    <p><strong>Author:</strong> {{ book.author }}</p>
    <p><strong>Description:</strong> {{ book.description }}</p>
    <p><strong>Price:</strong> {{ book.price }}</p>
    <a href="{{ url_for('edit_book', id=book.id) }}" class="btn btn-warning">Edit</a>
    <form action="{{ url_for('delete_book', id=book.id) }}" method="POST" style="display:inline-block;">
        <button type="submit" class="btn btn-danger">Delete</button>
    </form>
    <a href="{{ url_for('index') }}" class="btn btn-secondary">Back to List</a>
{% endblock %}

```


## Create edit_book.html

```
{% extends "base.html" %}

{% block title %}Edit Book{% endblock %}

{% block content %}
    <h1>Edit Book</h1>
    <form action="{{ url_for('edit_book', id=book.id) }}" method="post">
        <div class="mb-3">
            <label for="title" class="form-label">Title</label>
            <input type="text" class="form-control" id="title" name="title" value="{{ book.title }}" required>
        </div>
        <div class="mb-3">
            <label for="author" class="form-label">Author</label>
            <input type="text" class="form-control" id="author" name="author" value="{{ book.author }}" required>
        </div>
        <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <textarea class="form-control" id="description" name="description">{{ book.description }}</textarea>
        </div>
        <div class="mb-3">
            <label for="price" class="form-label">Price</label>
            <input type="text" class="form-control" id="price" name="price" value="{{ book.price }}" required>
        </div>
        <button type="submit" class="btn btn-primary">Update Book</button>
        <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancel</a>
    </form>
{% endblock %}

```
## Add CSS for Better UI

### Create Static Folder

1. In the project directory, create a folder named `static`.
2. Inside `static`, create a file named `styles.css` with the following content:

```
.table {
    width: 100%;
    max-width: 100%;
    margin-bottom: 1rem;
    background-color: transparent;
    table-layout: fixed;  /* Change to fixed layout */
}

.table th, .table td {
    padding: 0.75rem;
    vertical-align: top;
    border-top: 1px solid #dee2e6;
    word-wrap: break-word;  /* Ensure text wraps */
    overflow-wrap: break-word;  /* Ensure text wraps */
}

.table th:nth-child(1),
.table td:nth-child(1) {
    width: 10%;  /* Adjust width of Title column */
}

.table th:nth-child(2),
.table td:nth-child(2) {
    width: 10%;  /* Adjust width of Author column */
}

.table th:nth-child(3),
.table td:nth-child(3) {
    width: 50%;  /* Adjust width of Description column */
}

.table th:nth-child(4),
.table td:nth-child(4) {
    width: 10%;  /* Adjust width of Price column */
}

.table th:nth-child(5),
.table td:nth-child(5) {
    width: 20%;  /* Adjust width of Actions column */
}
.edit-button {
    margin-right: 10px; /* Adjust the amount of space as needed */
}

```
## Add Requirement to Text File

### Create requirements.txt

1. In the project directory, create a file named `requirements.txt`.
2. Add product details in the following format:

```plaintext
Flask
Flask-SQLAlchemy
Flask-JWT-Extended
gunicorn
pymysql
```

## Run the Application

### Run the Flask App

1. In Visual Studio Code, set the startup file to `app.py` if not already set.
2. Click **Run** or press **F5** to start the server.
3. Open your web browser and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Push to GitHub

### Initialize Git

1. In your project directory, open a terminal and run:

    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    ```

### Create a GitHub Repository

1. Go to GitHub and create a new repository named `OnlineBookstore`.

### Push to GitHub

1. Follow the instructions provided by GitHub to push your local repository to GitHub:

    ```bash
    git remote add origin https://github.com/yourusername/OnlineBookStore.git
    git branch -M main
    git push -u origin main
    ```

## Deploy to Google Cloud Platform

1. **Install Google Cloud SDK**: Follow the instructions to install the Google Cloud SDK [https://cloud.google.com/sdk/docs/install-sdk].
2. **Create a New Project**: Go to the Google Cloud Console and create a new project.
3. **Enable Billing**: Ensure billing is enabled for your project.
4. **Deploy the Application**:

    1. In your project directory, create an `app.yaml` file with the following content:

       ``` yaml
        
          runtime: python39
           entrypoint: gunicorn -b :$PORT app:app

           instance_class: F2

           env_variables:
                  SQLALCHEMY_DATABASE_URI: "mysql+pymysql://aarya:aarya123@/book?unix_socket=/cloudsql/online-bookstore-428523:us-central1:bookstore"
                  JWT_SECRET_KEY: "your_jwt_secret_key"

         beta_settings:
                 cloud_sql_instances: "online-bookstore-428523:us-central1:bookstore"
       
           
    2. Deploy your application:
    
       ```bash
        gcloud app deploy
        ```
    3. Access your deployed application at `https://<your-project-id>.appspot.com`.



# Screenshot of the website

### Main Page:

<img width="1438" alt="Screenshot 2024-07-06 at 7 24 22 PM" src="https://github.com/aaryamaster/Online-BookStore/assets/75297750/70985e40-03d8-4501-bd6e-8774f1d31a52">

### Add Page:

<img width="1438" alt="Screenshot 2024-07-06 at 7 44 19 PM" src="https://github.com/aaryamaster/Online-BookStore/assets/75297750/2fabffaf-f74b-4360-863b-88170d073d3e">

### Edit Page:

<img width="1438" alt="Screenshot 2024-07-06 at 7 44 27 PM" src="https://github.com/aaryamaster/Online-BookStore/assets/75297750/9f4be4db-64ba-4db5-9b8c-d431a4b363f2">

### Book Detail Page:

<img width="1438" alt="Screenshot 2024-07-06 at 7 45 40 PM" src="https://github.com/aaryamaster/Online-BookStore/assets/75297750/07a319b9-90ae-4663-bc98-6408f487d4ee">



