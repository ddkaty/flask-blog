from app import db
from app.forms import LoginForm, PostForm, EditUserForm, UserForm
from app.models import Post, User, Comment
from flask import Blueprint, render_template, redirect, url_for, request
from flask.ext.login import login_user, logout_user, current_user, \
    login_required

mod = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin',
    template_folder='../templates/admin'
)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = form.user  # verified and fetched by form validator
        login_user(user, remember=form.remember.data)
        return redirect(url_for('admin.overview'))
    return render_template('login.html', form=form)


@mod.route('/logout')
@login_required
def logout():
    """Logout authenticated user."""
    logout_user()
    return redirect(url_for('frontend.index'))


@mod.route('/')
@login_required
def overview():
    """View admin overview."""
    return render_template('overview.html')


@mod.route('/users')
@login_required
def users():
    """View users."""
    users = User.query.filter_by_latest()
    return render_template('user/list.html', users=users)


@mod.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    """Create new user."""
    form = UserForm()
    if form.validate_on_submit():
        user = User(form.name.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.users'))
    return render_template('user/new.html', form=form)


@mod.route('/users/edit/<name>', methods=['GET', 'POST'])
@login_required
def edit_user(name):
    """Edit user specified by username."""
    user = User.query.filter_by_name_or_404(name)
    form = EditUserForm(name=user.name)
    if form.validate_on_submit():
        user.name = form.name.data
        db.session.commit()
        return redirect(url_for('admin.users'))
    return render_template('user/edit.html', user=user, form=form)


@mod.route('/users/delete/<name>', methods=['GET', 'POST'])
@login_required
def delete_user(name):
    """Delete user by specified username."""
    user = User.query.filter_by_name_or_404(name)
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin.users'))
    return render_template(
        'delete.html',
        title='Delete User',
        what=user.name,
        action=url_for('admin.delete_user', name=user.name)
    )


@mod.route('/posts')
@login_required
def posts():
    """View all posts."""
    posts = Post.query.filter_by_latest()
    return render_template('post/list.html', posts=posts)


@mod.route('/posts/user/<name>')
def posts_by_user(name):
    """View all posts published by specified author."""
    user = User.query.filter_by_name_or_404(name=name)
    return render_template('post/list.html', user=user, posts=user.posts)


@mod.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Add new post."""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(form.title.data, form.body.data, current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('admin.posts'))
    return render_template('post/new.html', form=form)


@mod.route('/posts/edit/<path:slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    """Edit post with specified slug."""
    post = Post.query.slug_or_404(slug=slug)
    form = PostForm(prev_title=post.title, title=post.title, body=post.body)
    if form.validate_on_submit():
        post.edit(form.title.data, form.body.data)
        db.session.commit()
        return redirect(url_for('admin.posts'))
    return render_template('post/edit.html', post=post, form=form)


@mod.route('/posts/delete/<path:slug>', methods=['GET', 'POST'])
@login_required
def delete_post(slug):
    """Delete post with specified slug."""
    post = Post.query.slug_or_404(slug=slug)
    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('admin.posts'))
    return render_template(
        'delete.html',
        title='Delete Post',
        what=post.title,
        action=url_for('admin.delete_post', slug=post.slug)
    )


@mod.route('/posts/comments/<path:slug>')
@login_required
def post_comments(slug):
    """View comments for specified slug."""
    post = Post.query.slug_or_404(slug=slug)
    return render_template('comment/list.html',
                           post=post,
                           comments=post.comments)


@mod.route('/comments/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    """Delete comment with specified id."""
    comment = Comment.query.get_or_404(id)
    if request.method == 'POST':
        post_id = comment.post_id
        db.session.delete(comment)
        db.session.commit()
        # redirect to the remaining post comments
        slug = Post.query.get_or_404(post_id).slug
        return redirect(url_for('admin.post_comments', slug=slug))
    return render_template(
        'delete.html',
        title='Delete Comment',
        what='comment',
        action=url_for('admin.delete_comment', id=comment.id)
    )
