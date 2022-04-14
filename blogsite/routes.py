import os
import secrets
from blogsite import app, db, bcrypt
from flask import render_template, flash, redirect, url_for, request, abort
from blogsite.form import LoginForm, RegistrationForm, UpdateNameForm, UpdatePasswordForm, UpdatePictureForm, BlogForm
from blogsite.models import User, Blog
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image


@app.route('/home')
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    blog = Blog.query.order_by(Blog.id.desc()).paginate(page=page, per_page=10)
    return render_template("index.html", title="Home", blogs=blog)


@app.route('/user_blog/<int:user_id>')
def user_blog(user_id):
    page = request.args.get('page', 1, type=int)
    blog = Blog.query.filter_by(user_id=user_id).order_by(Blog.id.desc()).paginate(page=page, per_page=10)
    return render_template('userBlog.html', title=blog.items[0].author.name, blogs=blog)


@app.route('/logs')
def logs():
    total_blog = Blog.query.count()
    total_user = User.query.count()
    return render_template('logs.html', title='Logs', total_blog=total_blog, total_user=total_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, form.remember.data)
            flash(f"Logged In as {user.name}", 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash("Login Failed! Please Check username and password!", 'danger')

    return render_template("login.html", title="Login", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hash_password)

        db.session.add(user)
        db.session.commit()

        flash(f"Activation Link Sent to \"{form.email.data}\"", 'success')

        return redirect(url_for('register'))

    return render_template("register.html", title="Register", form=form)


def save_picture(form_picture,dir , x, y):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    pic_fn = random_hex + f_ext

    save_path = os.path.join(app.root_path, f'static/{dir}', pic_fn)
    output_size = (x, y)

    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(save_path)

    return pic_fn


def save_file(form_data, dir):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_data.filename)

    file_fn = random_hex + f_ext
    save_path = os.path.join(app.root_path, f'static/{dir}', file_fn)

    form_data.save(save_path)

    return file_fn


def delete_file(filename, dir):
    if filename:
        path = os.path.join(app.root_path, f'static/{dir}', filename)
        os.remove(path)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    imagefile = url_for('static', filename=f'profile_pic/{current_user.profile_pic}')

    name_form = UpdateNameForm()
    password_form = UpdatePasswordForm()
    profile_form = UpdatePictureForm()

    if name_form.validate_on_submit():
        current_user.name = name_form.name.data

        db.session.commit()
        flash('Account Name Updated', 'success')

        return redirect(url_for('account'))

    if password_form.validate_on_submit():
        current_user.password = bcrypt.generate_password_hash(password_form.new_password.data)

        db.session.commit()
        flash('Account Password Updated', 'success')

        return redirect(url_for('account'))

    if profile_form.validate_on_submit():

        picture_file = save_picture(profile_form.picture.data, 'profile_pic', 125, 125)
        current_user.profile_pic = picture_file

        db.session.commit()
        flash('Profile Pic Updated', 'success')

        return redirect(url_for('account'))

    return render_template('account.html', title='Account', image_file=imagefile, nameForm=name_form, passForm=password_form, profileForm=profile_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged Out! Login in again to see posts!", 'success')
    return redirect(url_for('index'))


@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    form = BlogForm()
    if form.validate_on_submit():
        image_name, audio_name, video_name = None, None, None

        if form.image.data:
            image_name = save_picture(form.image.data, 'image', 1114, 415)

        if form.audio.data:
            audio_name = save_file(form.audio.data, 'Audio')

        if form.video.data:
            video_name = save_file(form.video.data, 'Video')

        blog = Blog(title=form.title.data, content=form.content.data,
                    image=image_name, audio=audio_name, video=video_name, author=current_user)

        db.session.add(blog)
        db.session.commit()

        flash("Blog Published Successfully", 'success')

        return redirect(url_for('blog', blog_id=blog.id))
    return render_template('create_blog.html', title='New Blog', form=form, legend='New Blog')


@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)

    return render_template('blog.html', title=blog.title, blog=blog)


@app.route('/blog/<int:blog_id>/update', methods=['GET', 'POST'])
@login_required
def update_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)

    if blog.author != current_user:
        abort(403)

    form = BlogForm()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data

        if form.image.data:
            delete_file(blog.image, 'image')
            blog.image = save_file(form.image.data, 'image')

        if form.audio.data:
            delete_file(blog.audio, 'audio')
            blog.audio = save_file(form.audio.data, 'audio')

        if form.video.data:
            delete_file(blog.video, 'video')
            blog.video = save_file(form.video.data, 'video')

        db.session.commit()
        flash('You Blog has been Updated!', 'success')

        return redirect(url_for('blog', blog_id=blog_id))
    else:
        form.title.data = blog.title
        form.content.data = blog.content

    return render_template('create_blog.html', title='Update Blog', form=form, legend='Update Blog')


@app.route('/blog/<int:blog_id>/delete')
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)

    if blog.author != current_user:
        abort(403)

    delete_file(blog.image, 'image')
    delete_file(blog.audio, 'audio')
    delete_file(blog.video, 'video')

    db.session.delete(blog)
    db.session.commit()

    flash('Blog Deleted Successfully!', 'success')

    return redirect(url_for('index'))

