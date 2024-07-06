from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:aaryamaster@localhost/bookstore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Set your secret key for sessions
db = SQLAlchemy(app)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)  # DECIMAL type for precise monetary values

    def __repr__(self):
        return f'<Book {self.id}, {self.title}>'

# Create all tables based on defined models
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        price = Decimal(request.form['price'].strip('$'))  # Convert price to Decimal after stripping '$'

        new_book = Book(title=title, author=author, description=description, price=price)

        try:
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            print(f"Error adding book: {e}")
            # Handle the error as needed
            return "Error adding book"

    return render_template('add_book.html')

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return render_template('book_detail.html', book=book)

@app.route('/books/<int:id>/edit', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)

    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.description = request.form['description']
        book.price = Decimal(request.form['price'].strip('$'))

        try:
            db.session.commit()
            return redirect(url_for('get_book', id=id))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating book: {e}")
            # Handle the error as needed
            return "Error updating book"

    return render_template('edit_book.html', book=book)

@app.route('/books/<int:id>/delete', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)

    try:
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting book: {e}")
        # Handle the error as needed
        return "Error deleting book"

if __name__ == '__main__':
    app.run(debug=True)
