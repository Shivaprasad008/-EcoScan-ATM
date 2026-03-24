import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, RecycleTransaction
from bottle_scanner import scan_bottle
import matplotlib
matplotlib.use('Agg') # Used to generate plots in web app without displaying GUI
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super-secret-key-12345'
    
    # SQLite Database config
    base_dir = os.path.abspath(os.path.dirname(__name__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Uploads folder for bottles and graphs
    UPLOAD_FOLDER = os.path.join(base_dir, 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    db.init_app(app)
    
    # ------------------ ROUTES ------------------

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name = request.form.get('username')
            mobile = request.form.get('mobile_number')
            password = request.form.get('password')
            
            # Check if user exists
            user = User.query.filter_by(mobile_number=mobile).first()
            if user:
                flash('Mobile number already registered.', 'danger')
                return redirect(url_for('signup'))
                
            new_user = User(
                username=name,
                mobile_number=mobile,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        return render_template('login.html', is_signup=True)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            mobile = request.form.get('mobile_number')
            password = request.form.get('password')
            
            user = User.query.filter_by(mobile_number=mobile).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')
                
        return render_template('login.html', is_signup=False)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        user = User.query.get(session['user_id'])
        transactions = RecycleTransaction.query.filter_by(user_id=user.id).order_by(RecycleTransaction.timestamp.desc()).all()
        
        # Calculate stats
        total_bottles = sum(t.bottles_inserted for t in transactions)
        
        # Generate Impact Graph for the user
        graph_url = generate_impact_graph(user.id)
        
        return render_template('dashboard.html', user=user, transactions=transactions, total_bottles=total_bottles, graph_url=graph_url)

    @app.route('/scan', methods=['GET', 'POST'])
    def scan():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        if request.method == 'POST':
            if 'bottle_image' not in request.files:
                flash('No image uploaded.', 'danger')
                return redirect(url_for('scan'))
                
            file = request.files['bottle_image']
            if file.filename == '':
                flash('No selected file.', 'danger')
                return redirect(url_for('scan'))
                
            if file:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                
                # Use OpenCV scanner
                is_valid, message = scan_bottle(filepath)
                
                if is_valid:
                    POINTS_PER_BOTTLE = 10
                    user = User.query.get(session['user_id'])
                    
                    # Create transaction
                    txn = RecycleTransaction(user_id=user.id, bottles_inserted=1, points_earned=POINTS_PER_BOTTLE)
                    user.points += POINTS_PER_BOTTLE
                    
                    db.session.add(txn)
                    db.session.commit()
                    
                    flash(f'Success! Bottle detected. You earned {POINTS_PER_BOTTLE} points.', 'success')
                else:
                    flash(f'Scan failed: {message}', 'danger')
                    
                return redirect(url_for('dashboard'))
                
        return render_template('scan.html')

    @app.route('/admin')
    def admin():
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access denied.', 'danger')
            return redirect(url_for('dashboard'))
            
        users = User.query.order_by(User.points.desc()).all()
        return render_template('admin.html', users=users)

    # Helper function to generate graph
    def generate_impact_graph(user_id):
        user = User.query.get(user_id)
        txns = RecycleTransaction.query.filter_by(user_id=user_id).all()
        
        if not txns:
            return None
            
        data = [{'date': t.timestamp.date(), 'bottles': t.bottles_inserted} for t in txns]
        df = pd.DataFrame(data)
        
        # Aggregate by date
        df_grouped = df.groupby('date').sum().reset_index()
        
        plt.figure(figsize=(6, 4))
        plt.plot(df_grouped['date'], df_grouped['bottles'], marker='o', color='#2ecc71', linewidth=2)
        plt.title('Daily Bottle Recycling Trend')
        plt.xlabel('Date')
        plt.ylabel('Bottles Recycled')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        filename = f'graph_{user_id}.png'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        plt.savefig(filepath)
        plt.close()
        
        return url_for('static', filename=f'uploads/{filename}')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
