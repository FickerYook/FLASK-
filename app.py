from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
app.secret_key = "super secret key"
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

#home
@app.route('/home')
def home():
    username=session['username'] 
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT username FROM users')
    usernames = cursor.fetchall()
    total_users = len(usernames)
    cursor.close()
    return render_template('home.html',username=username,usernames=usernames, total_users=total_users)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
        record = cursor.fetchone()

        if record:
            session['loggedin'] = True
            session['username'] = record[1]
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password. Please try again.'
    return render_template('index.html', msg=msg)

# Show table product
@app.route('/table')
def table():
    username=session['username'] 
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM products')
    product = cursor.fetchall()
    cursor.close()
    return render_template('table.html',product=product)


# add products
@app.route('/add_products', methods=['GET', 'POST'])
def add_products():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        image = request.files['image']

        if image:
            image_filename = image.filename
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO products (name, price, description, image) VALUES (%s, %s, %s, %s)", (name, price, description, image_filename))
            mysql.connection.commit()
            cursor.close()
            image.save(f"static/images/{image_filename}")
            return redirect(url_for('table'))
        
    return render_template('add_product.html')

######## DETAIL ####################
@app.route('/product_details/<int:id>')
def product_details(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    product = cursor.fetchone()
    cursor.close()

    return render_template('detail.html', product=product)
#######################################################################

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        image = request.files['image']

        if image:
            image_filename = image.filename
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE products SET name=%s, price=%s, description=%s, image=%s WHERE id=%s", (name, price, description, image_filename, id))
            mysql.connection.commit()
            cursor.close()
            image.save(f"static/images/{image_filename}")
            flash('ข้อมูลสินค้าถูกแก้ไขเรียบร้อย', 'success')
            return redirect(url_for('table'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()
    cursor.close()

    return render_template('edit_product.html', product=product)




# Logout ###########################################################
@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('username',None)
    session.clear
    return redirect(url_for('login'))

# DELETE ###############################################################
@app.route('/delete_product/<int:id>')
def delete_product(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('ลบสินค้าเรียบร้อยแล้ว!', 'success')
    return redirect(url_for('table'))

if __name__ == '__main__':
    app.run(debug=True)