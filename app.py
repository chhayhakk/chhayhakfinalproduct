from flask import Flask, render_template, request
import requests
import sqlite3
import base64
# import io
# from PIL import Image
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
from datetime import date

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['CROP_FOLDER'] = 'static/crop'
MAX_SIZE_MB = 2

channel_id= "@chhayhak_notify_channel"
bot_token = "7143396464:AAEtiHgXPxWQiR8n9QRwkrhIWYyuYQWz4ro"
bot_username ="chhayhakk_bot"

conn = sqlite3.connect('database.db', check_same_thread=False)



@app.route('/')
def product():
    row = conn.execute("""SELECT * FROM tbl_products""")
    product = []
    for item in row:
        product.append(
            {
                'id': item[0],
                'title': item[1],
                'cost': item[2],
                'price': item[3],
                'description': item[4],
                'image_path':item[5],

            }
        )
    return render_template('index.html', product_list=product)
    # product_list = []
    # url = "https://fakestoreapi.com/products"
    # response = requests.get(url)
    # products = response.json()
    # product_list = products
    return render_template('index.html', product_list=product_list)


@app.route('/product')
def allproduct():
    row = conn.execute("""SELECT * FROM tbl_products""")
    product = []
    for item in row:
        product.append(
            {
                'id': item[0],
                'title': item[1],
                'cost': item[2],
                'price': item[3],
                'description': item[4],
                'image_path': item[5]
            }
        )
    return render_template('products.html', product_list=product)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path):
    with Image.open(image_path) as img:
        if img.size > (1920, 1080):
            img = img.resize((1920, 1080), Image.ANTIALIAS)
        img.save(image_path, optimize=True, quality=85)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        title = request.form.get('title')
        cost = request.form.get('cost')
        price = request.form.get('price')
        description = request.form.get('description')
        cropped_image_data = request.form.get('cropped_image_data')
        original_image_data = request.form.get('original_image_data')
        original_filename = request.form.get('original_filename')
        # image_file = request.files.get('image')  # Correct way to get the uploaded file
        original_image_filename = 'no-photo.png'
        cropped_filename = 'no-photo.png'
        if original_image_data:
                image_data = original_image_data.split(',')[1]
                image = base64.b64decode(image_data)
                image_filename = secure_filename(original_filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                
                with open(image_path, 'wb') as f:
                    f.write(image)

                if os.path.getsize(image_path) > 2 * 1024 * 1024:  
                    compress_image(image_path)
        if cropped_image_data:
            cropped_data = cropped_image_data.split(',')[1]
            cropped_image = base64.b64decode(cropped_data)
            cropped_filename = secure_filename(original_filename)
            cropped_image_path = os.path.join(app.config['CROP_FOLDER'], cropped_filename)
            
            with open(cropped_image_path, 'wb') as f:
                f.write(cropped_image)
        # filename = 'no-photo.png'
        # if image_file and allowed_file(image_file.filename):
        #     filename = secure_filename(image_file.filename)
        #     image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #     image_file.save(image_path)

        conn.execute("""
                INSERT INTO tbl_products (title, cost, price, description, image_path)
                VALUES (?, ?, ?, ?, ?)
            """, (title, cost, price, description, cropped_filename))
        
        conn.commit()

    row = conn.execute("""SELECT * FROM tbl_products""")
    product = []
    for item in row:
        product.append(
            {
                'id': item[0],
                'title': item[1],
                'cost': item[2],
                'price': item[3],
                'description': item[4],
                'image_path':item[5],

            }
        )

    
    return render_template('add_product.html', product_list=product)

   


@app.route('/edit_product', methods=['GET','POST'])
def edit_product():
    product_id = request.args.get('id')
    
    def get_product_details(product_id):
        row = conn.execute("SELECT * FROM tbl_products WHERE id = ?", (product_id,)).fetchone()
        return {
            'id': row[0],
            'title': row[1],
            'cost': row[2],
            'price': row[3],
            'description': row[4],
            'image_path': row[5]
        }
    
    current_product = get_product_details(product_id)

    
    if request.method == 'POST':
        title = request.form.get('title')
        cost = request.form.get('cost')
        price = request.form.get('price')
        description = request.form.get('description')
        # image_file = request.files.get('image')
        
        cropped_image_data = request.form.get('cropped_image_data')
        original_image_data = request.form.get('original_image_data')
        original_filename = request.form.get('original_filename')
        
        cropped_image_filename = current_product['image_path']
        
        if original_image_data:
            image_data = original_image_data.split(',')[1]
            image = base64.b64decode(image_data)
            original_image_filename = secure_filename(original_filename)
            original_image_path = os.path.join(app.config['UPLOAD_FOLDER'], original_image_filename)
            
            with open(original_image_path, 'wb') as f:
                f.write(image)

            if os.path.getsize(original_image_path) > 2 * 1024 * 1024:  # 2MB
                compress_image(original_image_path)
        
        if cropped_image_data:
            cropped_data = cropped_image_data.split(',')[1]
            cropped_image = base64.b64decode(cropped_data)
            cropped_image_filename = secure_filename(original_filename)
            cropped_image_path = os.path.join(app.config['CROP_FOLDER'], cropped_image_filename)
            
            with open(cropped_image_path, 'wb') as f:
                f.write(cropped_image)
        
    #     if image_file and allowed_file(image_file.filename):
    #         filename = secure_filename(image_file.filename)
    #         image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #         image_file.save(image_path)
    #     else:
    #         cropped_filename = current_product['image_path']
        query = """
                UPDATE tbl_products 
                SET title = ?, cost = ?, price = ?, description = ?, image_path = ?
                WHERE id = ?
            """
        conn.execute(query, (title, cost, price, description, cropped_image_filename, product_id))
        conn.commit()
        
        current_product = get_product_details(product_id)
    return render_template('edit_product.html',current_product=current_product)

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = request.form.get('product_id')
    current_product = {}
    row = conn.execute("SELECT * FROM tbl_products")
    for item in row:
            current_product['id'] = item[0]
            current_product['title'] = item[1]
            current_product['description'] = item[4]
            current_product['price'] = item[3]
            current_product['image_path'] = item[5]

        # Delete the product
    conn.execute("DELETE FROM tbl_products WHERE id = ?", (product_id,))
    conn.commit()

    return render_template('add_product.html', current_product=current_product)
  
   

@app.route('/review')
def review():
    product_id = request.args.get('id')
    current_product = {}
    row = conn.execute("""SELECT * FROM tbl_products where id = ?""",(product_id,))
    for item in row:
        current_product['id'] = item[0]
        current_product['title'] = item[1]
        current_product['description'] = item[4]
        current_product['price'] = item[3]
        current_product['image_path'] = item[5]

    
            
        

    # product_id = request.args.get('id')
    # url = "https://fakestoreapi.com/products/{}".format(product_id)
    # response = requests.get(url)
    # current_product = response.json()
    return render_template('review.html', current_product=current_product)


@app.route('/checkout')
def checkout():
    current_product = {}
    product_id = request.args.get('id')
    row = conn.execute("""SELECT * FROM tbl_products where id = ?""",(product_id,))
    for item in row:
        current_product['id'] = item[0]
        current_product['title'] = item[1]
        current_product['description'] = item[4]
        current_product['price'] = item[3]
        current_product['image_path'] = item[5]
        

    # url = "https://fakestoreapi.com/products/{}".format(product_id)
    # response = requests.get(url)
    # current_product = response.json()
    return render_template('checkout.html', current_product=current_product)


@app.post('/submit_order')
def sumbit_order():
    current_product = []
    product_id = request.form.get('product_id')
    url = "https://fakestoreapi.com/products/{}".format(product_id)
    response = requests.get(url)
    current_product = response.json()
    name = request.form.get('fullname')
    phone = request.form.get('phone')
    email = request.form.get('email')


    html = (
        "<strong>🧾 {inv_no}</strong>\n"
        "<code>📆 {date}</code>\n"
        "<code>------------------------------</code>\n"
    )
    html += "<code>Product Name: {}</code>\n".format(current_product['title'])
    html += "<code>Qty: 1</code>\n"
    html += "<code>Price: ${:.2f} </code>\n".format(current_product['price'])
    html += "<code>----------------------------------------------</code>\n"
    html += "<code>Total: ${:.2f} </code>\n".format(current_product['price'])
    html += "<code>----------------------------------------------</code>\n"

    html += "<strong>Paid by: {}</strong>\n".format(name)
    html += "<strong>Phone Number: {}</strong>\n".format(phone)
    html += "<strong>Email: {}</strong>\n".format(email)
    html += "<strong>Total: ${:.2f}</strong>\n".format(current_product['price'])

    html = html.format(
        inv_no='INV0001',
        date=date.today()
    )
    # res = requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML".format(bot_token, channel_id,html))

    image_url = current_product['image']
    res = requests.get(
        "https://api.telegram.org/bot{}/sendPhoto".format(bot_token),
        params={
            'chat_id': channel_id,
            'photo': image_url,
            'caption': html,
            'parse_mode': 'HTML'
        }
    )
    return render_template('index.html',current_product=current_product)


if __name__ == '__main__':
    app.run()
