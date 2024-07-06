from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://aarya:aarya123@/book?unix_socket=/cloudsql/online-bookstore-428523:us-central1:bookstore'
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
