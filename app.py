from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# إعدادات الإيميل
class EmailConfig:
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_USERNAME = 'enter_u_gamil_account'
    EMAIL_PASSWORD = 'ricmoyjkbkcsycdn'
    FROM_NAME = 'متجر MyShop'

# إعدادات قاعدة البيانات MySQL
class DatabaseConfig:
    HOST = 'databasewep52.mysql.database.azure.com'  # أو عنوان السيرفر بتاعك
    DATABASE = 'myshop'
    USER = 'dbadminsarhan1'       # اسم المستخدم بتاعك
    PASSWORD = 'Mohamed2192002$'       # كلمة المرور بتاعك
    
    @classmethod
    def get_connection(cls):
        try:
            connection = mysql.connector.connect(
                host=cls.HOST,
                database=cls.DATABASE,
                user=cls.USER,
                password=cls.PASSWORD,
                charset='utf8mb4',
                autocommit=False
            )
            return connection
        except Error as e:
            print(f"Database connection error: {e}")
            return None

# دالة إرسال الإيميل
def send_confirmation_email(user_email, user_name, order_id, product_name, total_price):
    try:
        print(f"🔄 Sending confirmation email to: {user_email}")
        
        # إنشاء الرسالة
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{EmailConfig.FROM_NAME} <{EmailConfig.EMAIL_USERNAME}>"
        msg['To'] = user_email
        msg['Subject'] = f"تأكيد الطلب #{order_id} - {EmailConfig.FROM_NAME}"
        
        # نص الإيميل (HTML)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تأكيد الطلب</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">🎉 تم تأكيد طلبك!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">شكراً لك {user_name}</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h2 style="color: #333; margin-top: 0;">📦 تفاصيل الطلب</h2>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold;">رقم الطلب:</td>
                                <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #667eea; font-weight: bold;">#{order_id}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold;">المنتج:</td>
                                <td style="padding: 10px 0; border-bottom: 1px solid #eee;">{product_name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold;">المبلغ الإجمالي:</td>
                                <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #28a745; font-weight: bold; font-size: 18px;">${total_price}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px 0; font-weight: bold;">الحالة:</td>
                                <td style="padding: 10px 0;">
                                    <span style="background: #d1fae5; color: #059669; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">مؤكد ✅</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-right: 4px solid #2196f3;">
                        <h3 style="color: #1565c0; margin-top: 0;">📋 الخطوات التالية</h3>
                        <ul style="color: #424242; line-height: 1.6;">
                            <li>سيتم التواصل معك خلال 24 ساعة لتأكيد تفاصيل الشحن</li>
                            <li>سيتم شحن طلبك خلال 2-3 أيام عمل</li>
                            <li>ستصلك رسالة تتبع الشحن على هذا الإيميل</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="color: #666; font-size: 16px;">شكراً لاختيارك متجرنا! 🛒</p>
                        <p style="color: #999; font-size: 14px;">تاريخ التأكيد: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        © 2025 {EmailConfig.FROM_NAME} - جميع الحقوق محفوظة
                    </p>
                    <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                        هذه رسالة تأكيد تلقائية، يرجى عدم الرد عليها
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # إضافة المحتوى للرسالة
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # إرسال الرسالة
        server = smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT)
        server.starttls()
        server.login(EmailConfig.EMAIL_USERNAME, EmailConfig.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EmailConfig.EMAIL_USERNAME, user_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to: {user_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False

# دالة تحديث حالة الطلب
def update_order_status(order_id, new_status):
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            
            # التحقق من وجود عمود updated_at
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'updated_at'
            """, (DatabaseConfig.DATABASE,))
            
            has_updated_at = cursor.fetchone() is not None
            
            # استخدام الاستعلام المناسب حسب وجود العمود
            if has_updated_at:
                cursor.execute("""
                    UPDATE orders 
                    SET status = %s, updated_at = %s 
                    WHERE id = %s
                """, (new_status, datetime.now(), order_id))
            else:
                cursor.execute("""
                    UPDATE orders 
                    SET status = %s 
                    WHERE id = %s
                """, (new_status, order_id))
            
            connection.commit()
            rows_affected = cursor.rowcount
            
            cursor.close()
            connection.close()
            
            if rows_affected > 0:
                print(f"✅ Order {order_id} status updated to: {new_status}")
                return True
            else:
                print(f"❌ No order found with ID: {order_id}")
                return False
                
    except Error as e:
        print(f"❌ Update order status error: {e}")
        return False

# دالة إضافة عمود updated_at إذا لم يكن موجود
def add_updated_at_column():
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            
            # التحقق من وجود العمود
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'updated_at'
            """, (DatabaseConfig.DATABASE,))
            
            if not cursor.fetchone():
                print("⚠️ Adding updated_at column to orders table...")
                cursor.execute("""
                    ALTER TABLE orders 
                    ADD COLUMN updated_at TIMESTAMP NULL DEFAULT NULL
                """)
                connection.commit()
                print("✅ updated_at column added successfully!")
            else:
                print("✅ updated_at column already exists")
            
            cursor.close()
            connection.close()
            return True
                
    except Error as e:
        print(f"❌ Add updated_at column error: {e}")
        return False

# API تأكيد الطلب مع إرسال الإيميل
@app.route('/api/confirm-order', methods=['POST'])
def confirm_order_api():
    print("📍 API: Confirming order")
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({'success': False, 'message': 'Order ID is required'}), 400
        
        # الحصول على تفاصيل الطلب
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT o.*, u.name as user_name, u.email as user_email, 
                       p.name as product_name
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN products p ON o.product_id = p.id
                WHERE o.id = %s
            """, (order_id,))
            
            order = cursor.fetchone()
            cursor.close()
            connection.close()
            
            # if not order:
            #     return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
            # if order['status'] == 'confirmed':
            #     return jsonify({'success': False, 'message': 'الطلب مؤكد مسبقاً'}), 400
            
            # تحديث حالة الطلب
            if update_order_status(order_id, 'confirmed'):
                # إرسال الإيميل
                email_sent = send_confirmation_email(
                    user_email=order['user_email'],
                    user_name=order['user_name'],
                    order_id=order['id'],
                    product_name=order['product_name'],
                    total_price=f"{order['total_price']:.2f}"
                )
                
                # تسجيل النشاط
                log_activity(
                    order['user_id'], 
                    'order_confirmed', 
                    f'Order {order_id} confirmed and email sent: {"Yes" if email_sent else "No"}'
                )
                
                return jsonify({
                    'success': True, 
                    'message': f'تم تأكيد الطلب بنجاح! {"وتم إرسال إيميل للعميل" if email_sent else "لكن فشل إرسال الإيميل"}',
                    'email_sent': email_sent
                })
            else:
                return jsonify({'success': False, 'message': 'فشل في تأكيد الطلب'}), 500
        else:
            return jsonify({'success': False, 'message': 'خطأ في الاتصال بقاعدة البيانات'}), 500
            
    except Exception as e:
        print(f"❌ Confirm order API error: {e}")
        return jsonify({'success': False, 'message': 'خطأ في الخادم'}), 500

# باقي الكود كما هو...
# (يتم نسخ جميع الدوال الأخرى من الكود الأصلي)

# دالة تسجيل النشاطات مع التحقق من وصول البيانات
def log_activity(user_id, action, details=None):
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            user_agent = request.headers.get('User-Agent', 'unknown')
            
            query = """
                INSERT INTO activity_log (user_id, action, details, ip_address, user_agent, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (user_id, action, details, ip_address, user_agent, datetime.now())
            
            cursor.execute(query, values)
            connection.commit()
            
            # التحقق من أن البيانات وصلت
            inserted_id = cursor.lastrowid
            print(f"✅ Activity logged successfully with ID: {inserted_id}")
            
            cursor.close()
            connection.close()
            return True
    except Error as e:
        print(f"❌ Activity logging error: {e}")
        return False

# دالة التحقق من وجود المستخدم
def get_user_by_username(username):
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, name, email, password_hash, created_at
                FROM users 
                WHERE username = %s AND is_active = 1
            """, (username,))
            
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user:
                print(f"✅ User found: {user['username']} (ID: {user['id']})")
            else:
                print(f"❌ User not found: {username}")
                
            return user
        return None
    except Error as e:
        print(f"❌ Get user error: {e}")
        return None

# دالة التحقق من البريد الإلكتروني
def get_user_by_email(email):
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT id, username FROM users WHERE email = %s AND is_active = 1", (email,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            exists = result is not None
            print(f"{'✅' if exists else '❌'} Email check for {email}: {'Found' if exists else 'Not found'}")
            return exists
        return False
    except Error as e:
        print(f"❌ Email check error: {e}")
        return False

# دالة إنشاء مستخدم جديد مع التحقق
def create_user(username, name, email, password):
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            password_hash = generate_password_hash(password)
            
            query = """
                INSERT INTO users (username, name, email, password_hash, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (username, name, email, password_hash, datetime.now(), datetime.now())
            
            cursor.execute(query, values)
            connection.commit()
            
            user_id = cursor.lastrowid
            print(f"✅ User created successfully: {username} (ID: {user_id})")
            
            # التحقق من أن المستخدم تم إنشاؤه
            cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
            created_user = cursor.fetchone()
            print(f"✅ Verification - Created user: ID={created_user[0]}, Username={created_user[1]}, Email={created_user[2]}")
            
            cursor.close()
            connection.close()
            return user_id
        return None
    except Error as e:
        print(f"❌ Create user error: {e}")
        return None

# دالة الحصول على المنتجات
def get_products():
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, description, price, original_price, discount_percentage, 
                       image_url, category, features, created_at
                FROM products 
                WHERE is_active = 1
                ORDER BY created_at DESC
            """)
            
            products = cursor.fetchall()
            print(f"✅ Retrieved {len(products)} products from database")
            
            cursor.close()
            connection.close()
            
            # تحويل JSON features إلى list
            for product in products:
                if product['features']:
                    try:
                        product['features'] = json.loads(product['features'])
                    except json.JSONDecodeError:
                        product['features'] = []
                else:
                    product['features'] = []
            
            return products
        return []
    except Error as e:
        print(f"❌ Get products error: {e}")
        return []

# دالة الحصول على منتج واحد
def get_product_by_id(product_id):
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, description, price, original_price, discount_percentage, 
                       image_url, category, features
                FROM products 
                WHERE id = %s AND is_active = 1
            """, (product_id,))
            
            product = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if product:
                print(f"✅ Product found: {product['name']} (ID: {product['id']})")
                if product['features']:
                    try:
                        product['features'] = json.loads(product['features'])
                    except json.JSONDecodeError:
                        product['features'] = []
            else:
                print(f"❌ Product not found with ID: {product_id}")
            
            return product
        return None
    except Error as e:
        print(f"❌ Get product error: {e}")
        return None

# دالة إنشاء طلب جديد مع التحقق
def create_order(user_id, product_id, hours_needed, unit_price):
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            total_price = hours_needed * unit_price
            
            query = """
                INSERT INTO orders (user_id, product_id, hours_needed, unit_price, total_price, status, order_date)
                VALUES (%s, %s, %s, %s, %s, 'pending', %s)
            """
            values = (user_id, product_id, hours_needed, unit_price, total_price, datetime.now())
            
            cursor.execute(query, values)
            connection.commit()
            
            order_id = cursor.lastrowid
            print(f"✅ Order created successfully: ID={order_id}, User={user_id}, Product={product_id}, Total={total_price}")
            
            cursor.close()
            connection.close()
            return order_id
        return None
    except Error as e:
        print(f"❌ Create order error: {e}")
        return None

# دالة الحصول على طلبات المستخدم
def get_user_orders(user_id):
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT o.*, p.name as product_name, p.image_url as product_image
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE o.user_id = %s
                ORDER BY o.order_date DESC
            """, (user_id,))
            
            orders = cursor.fetchall()
            print(f"✅ Retrieved {len(orders)} orders for user ID: {user_id}")
            
            cursor.close()
            connection.close()
            return orders
        return []
    except Error as e:
        print(f"❌ Get user orders error: {e}")
        return []

# دالة الحصول على جميع الطلبات للأدمن
def get_all_orders():
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT o.id, o.user_id, o.product_id, o.hours_needed, o.unit_price, 
                       o.total_price, o.status, o.order_date,
                       u.username, u.name as user_name, u.email,
                       p.name as product_name, p.image_url as product_image
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                LEFT JOIN products p ON o.product_id = p.id
                ORDER BY o.order_date DESC
            """)
            
            orders = cursor.fetchall()
            print(f"✅ Retrieved {len(orders)} total orders from database")
            
            cursor.close()
            connection.close()
            return orders
        return []
    except Error as e:
        print(f"❌ Get all orders error: {e}")
        return []

# الصفحة الرئيسية
@app.route('/')
def home():
    print("📍 Accessing home route")
    if 'user_id' in session:
        print(f"✅ User logged in: {session.get('username')} (ID: {session.get('user_id')})")
        return redirect(url_for('product'))
    else:
        print("❌ No user session found, redirecting to login")
        return redirect(url_for('login'))

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("📍 Accessing login route")
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        print(f"🔍 Login attempt for username: {username}")
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return render_template('login.html')
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_name'] = user['name']
            
            print(f"✅ Login successful for: {username}")
            log_activity(user['id'], 'login', f'User {username} logged in successfully')
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('product'))
        else:
            print(f"❌ Login failed for: {username}")
            log_activity(None, 'login_failed', f'Failed login attempt for username: {username}')
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('login.html')

# صفحة إنشاء الحساب
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("📍 Accessing signup route")
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        print(f"🔍 Signup attempt for: {username} ({email})")
        
        # التحقق من البيانات
        if not all([username, name, email, password, confirm_password]):
            flash('جميع الحقول مطلوبة', 'error')
        elif len(username) < 3:
            flash('اسم المستخدم يجب أن يكون 3 أحرف على الأقل', 'error')
        elif len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
        elif password != confirm_password:
            flash('كلمة المرور وتأكيدها غير متطابقتين', 'error')
        elif get_user_by_username(username):
            flash('اسم المستخدم موجود بالفعل', 'error')
        elif get_user_by_email(email):
            flash('البريد الإلكتروني مسجل من قبل', 'error')
        else:
            # إنشاء المستخدم الجديد
            user_id = create_user(username, name, email, password)
            
            if user_id:
                print(f"✅ User created successfully: {username}")
                log_activity(user_id, 'signup', f'New user registered: {username}')
                flash('تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن', 'success')
                return redirect(url_for('login'))
            else:
                print(f"❌ Failed to create user: {username}")
                flash('حدث خطأ في إنشاء الحساب. يرجى المحاولة مرة أخرى', 'error')
    
    return render_template('signup.html')

# صفحة المنتجات
@app.route('/product')
def product():
    print("📍 Accessing product route")
    
    if 'user_id' not in session:
        flash('يرجى تسجيل الدخول أولاً', 'error')
        return redirect(url_for('login'))
    
    print(f"✅ Loading products for user: {session.get('username')}")
    
    products = get_products()
    if not products:
        print("⚠️ No products found, adding sample product")
        add_sample_product()
        products = get_products()
    
    return render_template('product.html', 
                         user_name=session.get('user_name'),
                         products=products)

# API لإنشاء طلب
@app.route('/api/create-order', methods=['POST'])
def create_order_api():
    print("📍 API: Creating order")
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        product_id = data.get('product_id', 1)
        hours_needed = int(data.get('hours_needed', 1))
        unit_price = float(data.get('unit_price', 69.0))
        
        print(f"🔍 Order data: Product={product_id}, Hours={hours_needed}, Price={unit_price}")
        
        if not all([product_id, hours_needed, unit_price]):
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'المنتج غير موجود'}), 404
        
        order_id = create_order(session['user_id'], product_id, hours_needed, unit_price)
        
        if order_id:
            log_activity(session['user_id'], 'order_created', f'Order {order_id} created for product {product_id}')
            return jsonify({
                'success': True, 
                'message': 'تم إنشاء الطلب بنجاح!',
                'order_id': order_id
            })
        else:
            return jsonify({'success': False, 'message': 'فشل في إنشاء الطلب'}), 500
            
    except Exception as e:
        print(f"❌ Order creation API error: {e}")
        return jsonify({'success': False, 'message': 'خطأ في الخادم'}), 500

# صفحة الطلبات
@app.route('/orders')
def orders():
    print("📍 Accessing orders route")
    
    if 'user_id' not in session:
        flash('يرجى تسجيل الدخول أولاً', 'error')
        return redirect(url_for('login'))
    
    user_orders = get_user_orders(session['user_id'])
    return render_template('orders.html', 
                         user_name=session.get('user_name'),
                         orders=user_orders)

# صفحة تسجيل الخروج
@app.route('/logout')
def logout():
    print("📍 User logging out")
    
    user_id = session.get('user_id')
    if user_id:
        log_activity(user_id, 'logout', 'User logged out')
        print(f"✅ User {session.get('username')} logged out")
    
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

# دالة إضافة منتج تجريبي
def add_sample_product():
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
            product_count = cursor.fetchone()[0]
            
            if product_count == 0:
                features = json.dumps([
                    "Active Noise Cancellation",
                    "50 Hours Battery Life", 
                    "Hi-Fi High Definition Sound",
                    "IPX7 Water Resistant",
                    "Fast Charging - 15 min = 3 hours"
                ])
                
                query = """
                    INSERT INTO products (name, description, price, original_price, discount_percentage, 
                                        image_url, category, features, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    'Wireless Bluetooth Headphones',
                    'High-quality wireless headphones with advanced noise cancellation technology. Long-lasting battery up to 50 hours, sleek lightweight design provides exceptional comfort all day long.',
                    69.00,
                    99.00,
                    29,
                    'https://i.pinimg.com/736x/93/b5/77/93b5776860e7fd5205389fddd8bc810a.jpg',
                    'إلكترونيات',
                    features,
                    datetime.now(),
                    datetime.now()
                )
                
                cursor.execute(query, values)
                connection.commit()
                
                product_id = cursor.lastrowid
                print(f"✅ Sample product added successfully with ID: {product_id}")
            else:
                print(f"✅ Products already exist ({product_count} products found)")
            
            cursor.close()
            connection.close()
            return True
    except Error as e:
        print(f"❌ Add sample product error: {e}")
        return False

# دالة اختبار شاملة لقاعدة البيانات
def test_database_connection():
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            
            tables_info = {}
            tables = ['users', 'products', 'orders', 'activity_log', 'user_sessions']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                tables_info[table] = count
                print(f"✅ Table {table}: {count} records")
            
            cursor.execute("SELECT VERSION()")
            db_version = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return {
                'status': 'success',
                'version': db_version,
                'tables': tables_info
            }
        else:
            return {'status': 'failed', 'error': 'Connection failed'}
            
    except Error as e:
        print(f"❌ Database test error: {e}")
        return {'status': 'error', 'error': str(e)}

# صفحة عرض جميع الطلبات للأدمن - محدثة مع زرار التأكيد
@app.route('/admin/all-orders')
def admin_all_orders():
    print("📍 Admin: Viewing all orders")
    
    orders = get_all_orders()
    orders_count = len(orders)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>جميع الطلبات - لوحة التحكم</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{ 
                background: white; 
                padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                max-width: 1400px;
                margin: 0 auto;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #f1f5f9;
            }}
            .title {{
                color: #1e293b;
                font-size: 32px;
                font-weight: 700;
                margin: 0;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .stats {{
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                color: white;
                padding: 12px 20px;
                border-radius: 10px;
                font-weight: 600;
            }}
            .btn-group {{
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }}
            .btn {{ 
                background: #4f46e5; 
                color: white; 
                padding: 12px 20px; 
                text-decoration: none; 
                border-radius: 8px; 
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-weight: 500;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }}
            .btn:hover {{ 
                background: #4338ca; 
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
            }}
            .btn-secondary {{
                background: #64748b;
            }}
            .btn-secondary:hover {{
                background: #475569;
            }}
            .btn-success {{
                background: #10b981;
                padding: 8px 16px;
                font-size: 12px;
            }}
            .btn-success:hover {{
                background: #059669;
            }}
            .btn-success:disabled {{
                background: #9ca3af;
                cursor: not-allowed;
                transform: none;
            }}
            .btn-danger {{
                background: #ef4444;
                padding: 8px 16px;
                font-size: 12px;
            }}
            .btn-danger:hover {{
                background: #dc2626;
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            th, td {{ 
                padding: 16px; 
                text-align: right; 
                border-bottom: 1px solid #e2e8f0;
                vertical-align: middle;
            }}
            th {{ 
                background: linear-gradient(135deg, #f8fafc, #f1f5f9);
                font-weight: 600;
                color: #374151;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            tr:hover {{
                background-color: #f8fafc;
            }}
            .status-badge {{
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .status-pending {{
                background: #fef3c7;
                color: #d97706;
            }}
            .status-confirmed {{
                background: #d1fae5;
                color: #059669;
            }}
            .status-cancelled {{
                background: #fee2e2;
                color: #dc2626;
            }}
            .price {{
                font-weight: 700;
                color: #059669;
                font-size: 16px;
            }}
            .product-image {{
                width: 50px;
                height: 50px;
                object-fit: cover;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .user-info {{
                display: flex;
                flex-direction: column;
                gap: 4px;
            }}
            .username {{
                font-weight: 600;
                color: #1e293b;
                font-size: 16px;
            }}
            .user-detail {{
                font-size: 12px;
                color: #64748b;
            }}
            .actions-cell {{
                text-align: center;
                width: 180px;
            }}
            .action-buttons {{
                display: flex;
                gap: 8px;
                justify-content: center;
                align-items: center;
            }}
            .loading {{
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .toast {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: #059669;
                color: white;
                padding: 16px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                z-index: 1000;
                transform: translateX(400px);
                transition: transform 0.3s ease;
            }}
            .toast.show {{
                transform: translateX(0);
            }}
            .toast.error {{
                background: #ef4444;
            }}
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                background: #f8fafc;
                border-radius: 10px;
                margin: 20px 0;
            }}
            .empty-icon {{
                font-size: 64px;
                margin-bottom: 16px;
                opacity: 0.5;
            }}
            .empty-title {{
                font-size: 24px;
                font-weight: 600;
                color: #64748b;
                margin-bottom: 8px;
            }}
            .empty-text {{
                color: #94a3b8;
                font-size: 16px;
            }}
            @media (max-width: 768px) {{
                .container {{
                    padding: 20px;
                    margin: 10px;
                }}
                .header {{
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                }}
                .btn-group {{
                    flex-wrap: wrap;
                    justify-content: center;
                }}
                table {{
                    font-size: 14px;
                }}
                th, td {{
                    padding: 8px 6px;
                }}
                .action-buttons {{
                    flex-direction: column;
                    gap: 4px;
                }}
                .actions-cell {{
                    width: 120px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">
                    📦 جميع الطلبات
                </h1>
                <div class="stats">
                    إجمالي الطلبات: {orders_count}
                </div>
            </div>
            
            <div class="btn-group">
                <a href="{url_for('test_database')}" class="btn btn-secondary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19 7L5 7L12 14L19 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    العودة لاختبار قاعدة البيانات
                </a>
                <a href="{url_for('view_recent_activities')}" class="btn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                        <path d="M12 1V4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        <path d="M12 20V23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    النشاطات الأخيرة
                </a>
                <button onclick="window.location.reload()" class="btn btn-success">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 12A9 9 0 0 1 12 3C16.97 3 21 7.03 21 12S16.97 21 12 21" stroke="currentColor" stroke-width="2"/>
                        <path d="M3 12L7 8L3 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    تحديث
                </button>
            </div>
    """
    
    if orders:
        html_content += """
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>رقم الطلب</th>
                            <th>المستخدم</th>
                            <th>المنتج</th>
                            <th>عدد الساعات</th>
                            <th>سعر الوحدة</th>
                            <th>الإجمالي</th>
                            <th>الحالة</th>
                            <th>تاريخ الطلب</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for order in orders:
            # تحديد لون الحالة
            if order['status'] == 'pending':
                status_class = 'status-pending'
                status_text = 'قيد الانتظار'
            elif order['status'] == 'confirmed':
                status_class = 'status-confirmed'
                status_text = 'مؤكد'
            elif order['status'] == 'cancelled':
                status_class = 'status-cancelled'
                status_text = 'ملغي'
            else:
                status_class = 'status-pending'
                status_text = order['status']
            
            # تنسيق التاريخ
            order_date = order['order_date'].strftime('%Y-%m-%d %H:%M') if order['order_date'] else 'غير محدد'
            
            # معلومات المستخدم (بدون تكرار الإيميل)
            username = order['username'] or 'مستخدم محذوف'
            user_name = order['user_name'] or 'غير محدد'
            email = order['email'] or 'غير محدد'
            
            # معلومات المنتج
            product_name = order['product_name'] or 'منتج محذوف'
            product_image = order['product_image'] or 'https://via.placeholder.com/50'
            
            # أزرار الإجراءات
            confirm_button = ''
            cancel_button = ''
            
            if order['status'] == 'pending':
                confirm_button = f'''
                    <button onclick="confirmOrder({order['id']}, '{email}', '{user_name}', '{product_name}', '{order['total_price']:.2f}')" 
                            class="btn btn-success" id="confirm-btn-{order['id']}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        تأكيد وإرسال إيميل
                    </button>
                '''
                cancel_button = f'''
                    <button onclick="cancelOrder({order['id']})" 
                            class="btn btn-danger" id="cancel-btn-{order['id']}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        إلغاء
                    </button>
                '''
            elif order['status'] == 'confirmed':
                confirm_button = '''
                    <span style="color: #059669; font-size: 12px; font-weight: 600;">
                        ✅ تم التأكيد
                    </span>
                '''
            
            html_content += f"""
                <tr>
                    <td><strong>#{order['id']}</strong></td>
                    <td>
                        <div class="user-info">
                            <span class="username">{user_name}</span>
                            <span class="user-detail">@{username}</span>
                        </div>
                    </td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <img src="{product_image}" alt="{product_name}" class="product-image" onerror="this.src='https://via.placeholder.com/50'">
                            <span>{product_name}</span>
                        </div>
                    </td>
                    <td>{order['hours_needed']} ساعة</td>
                    <td>{order['unit_price']:.2f} $</td>
                    <td><span class="price">{order['total_price']:.2f}$</span></td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                    <td>{order_date}</td>
                    <td class="actions-cell">
                        <div class="action-buttons">
                            {confirm_button}
                            {cancel_button}
                        </div>
                    </td>
                </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        """
    else:
        html_content += """
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <div class="empty-title">لا توجد طلبات حتى الآن</div>
                <div class="empty-text">سيتم عرض جميع الطلبات هنا عند إنشائها</div>
            </div>
        """
    
    html_content += f"""
        </div>
        
        <!-- Toast Notification -->
        <div id="toast" class="toast"></div>
        
        <script>
            // دالة عرض التنبيهات
            function showToast(message, isError = false) {{
                const toast = document.getElementById('toast');
                toast.textContent = message;
                toast.className = isError ? 'toast error show' : 'toast show';
                
                setTimeout(() => {{
                    toast.classList.remove('show');
                }}, 4000);
            }}
            
            // دالة تأكيد الطلب
            async function confirmOrder(orderId, userEmail, userName, productName, totalPrice) {{
                const confirmBtn = document.getElementById(`confirm-btn-${{orderId}}`);
                const cancelBtn = document.getElementById(`cancel-btn-${{orderId}}`);
                
                // تأكيد من المستخدم
                if (!confirm(`هل تريد تأكيد الطلب رقم #${{orderId}} وإرسال إيميل إلى ${{userEmail}}؟`)) {{
                    return;
                }}
                
                // تعطيل الأزرار وإظهار التحميل
                confirmBtn.disabled = true;
                cancelBtn.disabled = true;
                confirmBtn.innerHTML = '<div class="loading"></div> جاري الإرسال...';
                
                try {{
                    const response = await fetch('/api/confirm-order', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            order_id: orderId
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        showToast(result.message, false);
                        
                        // تحديث واجهة المستخدم
                        const row = confirmBtn.closest('tr');
                        const statusCell = row.querySelector('.status-badge');
                        const actionsCell = row.querySelector('.actions-cell');
                        
                        statusCell.className = 'status-badge status-confirmed';
                        statusCell.textContent = 'مؤكد';
                        
                        actionsCell.innerHTML = `
                            <span style="color: #059669; font-size: 12px; font-weight: 600;">
                                ✅ تم التأكيد
                            </span>
                        `;
                        
                        console.log('✅ Order confirmed successfully:', orderId);
                        
                        // تحديث الصفحة بعد 2 ثانية
                        setTimeout(() => {{
                            window.location.reload();
                        }}, 2000);
                    }} else {{
                        showToast(result.message || 'فشل في تأكيد الطلب', true);
                        
                        // إعادة تفعيل الأزرار
                        confirmBtn.disabled = false;
                        cancelBtn.disabled = false;
                        confirmBtn.innerHTML = `
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            تأكيد وإرسال إيميل
                        `;
                    }}
                }} catch (error) {{
                    console.error('❌ Confirm order error:', error);
                    showToast('خطأ في الاتصال بالخادم', true);
                    
                    // إعادة تفعيل الأزرار
                    confirmBtn.disabled = false;
                    cancelBtn.disabled = false;
                    confirmBtn.innerHTML = `
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        تأكيد وإرسال إيميل
                    `;
                }}
            }}
            
            // دالة إلغاء الطلب
            async function cancelOrder(orderId) {{
                if (!confirm(`هل تريد إلغاء الطلب رقم #${{orderId}}؟`)) {{
                    return;
                }}
                
                // يمكن إضافة API لإلغاء الطلب هنا
                showToast('سيتم إضافة وظيفة إلغاء الطلب قريباً', false);
            }}
            
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('✅ Admin Orders Page Loaded with Email Functionality');
                console.log('📊 Total Orders: {orders_count}');
                console.log('📧 Email Config: Gmail SMTP Ready');
                
                // Add click effects to table rows
                const rows = document.querySelectorAll('tbody tr');
                rows.forEach(row => {{
                    row.addEventListener('click', function(e) {{
                        // لا تفعل شيء إذا تم النقر على زرار
                        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {{
                            return;
                        }}
                        
                        this.style.backgroundColor = '#e0f2fe';
                        setTimeout(() => {{
                            this.style.backgroundColor = '';
                        }}, 200);
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

# صفحة اختبار قاعدة البيانات الشاملة
@app.route('/admin/test-db')
def test_database():
    print("📍 Testing database connection")
    
    db_test = test_database_connection()
    
    if db_test['status'] == 'success':
        html_content = f"""
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; }}
            .error {{ color: #dc3545; }}
            .info {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; }}
            .btn {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }}
        </style>
        <div class="container">
            <h2 class="success">✅ Database Connection Successful</h2>
            
            <div class="info">
                <strong>MySQL Version:</strong> {db_test['version']}<br>
                <strong>Database:</strong> myshop<br>
                <strong>Connection Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            
            <h3>Tables Status:</h3>
            <table>
                <tr><th>Table Name</th><th>Records Count</th><th>Status</th></tr>
        """
        
        for table, count in db_test['tables'].items():
            status = "✅ Active" if count > 0 else "⚠️ Empty"
            html_content += f"<tr><td>{table}</td><td>{count}</td><td>{status}</td></tr>"
        
        html_content += f"""
            </table>
            
            <h3>Quick Actions:</h3>
            <a href="{url_for('view_recent_activities')}" class="btn">View Recent Activities</a>
            <a href="{url_for('admin_all_orders')}" class="btn">View All Orders</a>
            <a href="{url_for('product')}" class="btn">Back to Products</a>
            
            <h3>Connection Details:</h3>
            <div class="info">
                <strong>Host:</strong> {DatabaseConfig.HOST}<br>
                <strong>Database:</strong> {DatabaseConfig.DATABASE}<br>
                <strong>User:</strong> {DatabaseConfig.USER}
            </div>
        </div>
        """
        
        return html_content
    else:
        return f"""
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .error {{ color: #dc3545; }}
        </style>
        <div class="container">
            <h2 class="error">❌ Database Connection Failed</h2>
            <p><strong>Error:</strong> {db_test.get('error', 'Unknown error')}</p>
            <p>Please check your database configuration in the app.py file.</p>
        </div>
        """

# عرض النشاطات الأخيرة
@app.route('/admin/recent-activities')
def view_recent_activities():
    print("📍 Viewing recent activities")
    
    try:
        connection = DatabaseConfig.get_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.*, u.username 
                FROM activity_log a 
                LEFT JOIN users u ON a.user_id = u.id 
                ORDER BY a.created_at DESC 
                LIMIT 20
            """)
            
            activities = cursor.fetchall()
            cursor.close()
            connection.close()
            
            html = """
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f8f9fa; }
                .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
            </style>
            <div class="container">
                <h2>Recent Activities</h2>
                <table>
                    <tr><th>ID</th><th>User</th><th>Action</th><th>Details</th><th>IP</th><th>Time</th></tr>
            """
            
            for activity in activities:
                username = activity['username'] or 'Unknown'
                details = activity['details'] or '-'
                ip = activity['ip_address'] or '-'
                time = activity['created_at'].strftime('%Y-%m-%d %H:%M:%S') if activity['created_at'] else '-'
                
                html += f"""
                    <tr>
                        <td>{activity['id']}</td>
                        <td>{username}</td>
                        <td>{activity['action']}</td>
                        <td>{details}</td>
                        <td>{ip}</td>
                        <td>{time}</td>
                    </tr>
                """
            
            html += f"""
                </table>
                <a href="{url_for('test_database')}" class="btn">Back to Database Test</a>
                <a href="{url_for('admin_all_orders')}" class="btn">View All Orders</a>
            </div>
            """
            
            return html
            
    except Exception as e:
        return f"<h2>Error: {e}</h2>"

# معالج الأخطاء
@app.errorhandler(404)
def not_found(error):
    return "<h1>404 - Page Not Found</h1>", 404

@app.errorhandler(500)
def internal_error(error):
    return "<h1>500 - Internal Server Error</h1>", 500

if __name__ == '__main__':
    print("🚀 Starting Flask application with Email Functionality...")
    print("📋 Database Configuration:")
    print(f"   Host: {DatabaseConfig.HOST}")
    print(f"   Database: {DatabaseConfig.DATABASE}")
    print(f"   User: {DatabaseConfig.USER}")
    print("📧 Email Configuration:")
    print(f"   SMTP Server: {EmailConfig.SMTP_SERVER}")
    print(f"   SMTP Port: {EmailConfig.SMTP_PORT}")
    print(f"   From Name: {EmailConfig.FROM_NAME}")
    print("=" * 50)
    
    # اختبار الاتصال عند بدء التشغيل
    db_test = test_database_connection()
    if db_test['status'] == 'success':
        print("✅ Database connection successful!")
        print(f"✅ MySQL Version: {db_test['version']}")
        for table, count in db_test['tables'].items():
            print(f"✅ Table '{table}': {count} records")
        
        # إضافة عمود updated_at إذا لم يكن موجود
        add_updated_at_column()
        
    else:
        print("❌ Database connection failed!")
        print(f"❌ Error: {db_test.get('error', 'Unknown error')}")
    
    print("=" * 50)
    print("🌐 Application URLs:")
    print("   Main: http://localhost:5000")
    print("   Login: http://localhost:5000/login")
    print("   Signup: http://localhost:5000/signup")
    print("   DB Test: http://localhost:5000/admin/test-db")
    print("   All Orders: http://localhost:5000/admin/all-orders")
    print("=" * 50)
    print("⚠️  IMPORTANT: Update Email Configuration!")
    print("   1. Change EmailConfig.EMAIL_USERNAME to your Gmail")
    print("   2. Generate Gmail App Password and update EmailConfig.EMAIL_PASSWORD")
    print("   3. Enable 2-Factor Authentication on your Gmail account")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)