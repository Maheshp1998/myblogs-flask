from datetime import datetime
from flask import redirect,render_template,request,Flask
from flask_login import login_required,current_user,login_user,logout_user
from models import *
from sqlalchemy import func

golbal_all_category_no = CategoryMaster.category_id
golbal_all_category_name  = CategoryMaster.category_name

app = Flask (__name__)
app.secret_key = "itStopNotchSecret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"



db.init_app(app)
login.init_app(app)




def get_all_categories():
    global global_all_category_no, global_all_category_name
    all_category_info = db.session.query(CategoryMaster.category_id, CategoryMaster.category_name)
    all_category_info = list(all_category_info)
    global_all_category_no, global_all_category_name = zip(*all_category_info)

@app.before_first_request
def create_all():
    get_all_categories()   

@app.route('/')
def index():
    return redirect('/register')   
 
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return render_template('blogs_home.html')
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if UserModel.query.filter_by(email=email).first():
            return "Email Already Exists"
        
        user = UserModel(email=email,username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # return redirect('/blogs')
        return redirect('login')
    return render_template('register.html')

@app.route('/addcatepage')
def addcatepage():
    return render_template('addcate.html')
 

@app.route('/addcate', methods=['GET','POST'])
def addcate():
    category_id = request.form.get('category_id')
    category_name = request.form.get('category_name')
    
    cate=CategoryMaster(category_id=category_id,category_name=category_name)
    db.session.add(cate)
    db.session.commit()
    return render_template('addcate.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return render_template('blogs_home.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = UserModel.query.filter_by(email=email).first()
        if user is not None and user.check_password(request.form.get('password')):
            login_user(user)
            return render_template('blogs_home.html')
        else:
            msg = "invalid credentials"
            return render_template("register.html",msg=msg)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect ('/register')    

@app.route('/blog')
def blog():
    if current_user.is_authenticated:
        return render_template('blogs_home.html')
    else:
        return redirect('/register')
    
# @app.route('/createblogpage')
# def createblogpage():
     
    
    
@app.route('/createblog',methods=["GET","POST"])
def create_blog():
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        blog_text = request.form.get('blog_text')
        today = datetime.now()
        blog_user_id = current_user.id
        blog_read_count = 0
        blog_rating_count = 0

        newBlog = BlogModel(category_id=category_id,
                   blog_user_id = blog_user_id,
                   blog_text = blog_text,
                   blog_creation_date = today,
                   blog_read_count = blog_read_count,
                   blog_rating_count = blog_rating_count )
        db.session.add(newBlog)
        db.session.commit()
        return redirect('/blog')
    else:
        return render_template('create_blog.html',all_category_id = global_all_category_no, all_category_name = global_all_category_name)
        
    
@app.route('/viewBlog')
@login_required
def view_blog():
    all_self_blogs = BlogModel.query.filter(BlogModel.blog_user_id==current_user.id).all()
    return render_template ('view_blog.html',all_self_blogs=all_self_blogs,all_categories = global_all_category_name)

@app.route('/self_blog_detail/<int:blog_model_id>/<string:blog_model_category>', methods=['GET','POST'])
@login_required
def self_blog_detail(blog_model_id,blog_model_category):
    blog_model = BlogModel.query.get(blog_model_id)
    if request.method == 'POST':
        if request.form['action'] == 'Update':
            blog_model.blog_text = request.form.get('blog_text')
        else:
            BlogModel.query.filter_by(id = blog_model_id).delete()
        db.session.commit()
        return redirect('/viewBlog')
    return render_template('/self_blog_detail.html',blog_id=blog_model_id, blog_categories = blog_model_category,blog_text = blog_model.blog_text)

@app.route('/listAllBlogs')  
def list_all_blogs():
    all_blogs = BlogModel.query.all()
    all_users = UserModel.query.all()
    print(all_blogs)
    return render_template('list_all_blogs.html',all_blogs=all_blogs, all_users=all_users, all_categories = global_all_category_name)

@app.route('/blogDetail/<int:blog_id>/<string:username>/<string:category>', methods=['GET','POST'])
@login_required
def blog_detail(blog_id, username, category):
    blog = BlogModel.query.get(blog_id)
    if request.method == 'GET':
        if current_user.id != blog.blog_user_id:
            blog.blog_read_count = blog.blog_read_count + 1
            db.session.commit()
        rating = db.session.query(func.avg(BlogComment.blog_rating)).filter(BlogComment.blog_id == int(blog_id)).first()[0]
        return render_template('/blog_detail.html',blog=blog, rating=rating, author=username,category=category)
    else:
        rate = request.form.get('rating')
        comment = request.form.get('comment')
        blog_id = request.form.get('blog_id')
        oldComment = BlogComment.query.filter(BlogComment.blog_id == blog_id).filter(BlogComment.comment_user_id == current_user.id).first()
        today = datetime.now()

        if oldComment == None:
            blog.blog_rating_count = blog.blog_rating_count + 1

            newComment = BlogComment(
                blog_id = blog_id,
                comment_user_id = current_user.id,
                blog_comment = comment,
                blog_rating = rate,
                blog_comment_date = today            
            )
            db.session.add(newComment)
        else:
            oldComment.blog_comment = comment
            oldComment.blog_rating = rate
        db.session.commit()
        return redirect('/blog')

with app.app_context():
    db.create_all()

if __name__  == "__main__":
    app.run(debug=True)