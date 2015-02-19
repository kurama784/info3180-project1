# coding=utf-8;

import os

from flask import render_template, request, redirect, url_for, \
  send_from_directory, flash, jsonify

from app import app  
from models import User, db
from forms import ProfileForm


def _request_is_ajax():
    return request.headers['Content-Type'] == 'application/json'

  
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def hello_world():
    return redirect(url_for('profiles'))


@app.route('/create_db')
def create_db():
    db.create_all()
    return "Created"


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data

            if not User.query.filter_by(username=username).first():
                user = User(username=username,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            age=form.age.data)

                db.session.add(user)
                db.session.commit()

                uploaded_file = request.files['image']
                if uploaded_file and allowed_file(uploaded_file.filename):
                    filename = 'user_profile_{0}.{1}'.format(
                        user.user_id, uploaded_file.filename.split('.')[-1]
                    )
                    uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                                    filename))
                    user.image = filename
                    db.session.commit()

                    return redirect(url_for('profiles'))

            # User already exist. Can't create
            flash(u"User with username %s already exist" % username)

        for field, errors in form.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                ))

    return render_template('profile_form.html', form=form)


@app.route('/profiles', methods=['GET', 'POST'])
def profiles():
    users = User.query.all()

    if _request_is_ajax() and request.method == 'POST':
        json_res = {}
        for user in users:
            json_res.update({
                'username': user.username,
                'userid': user.user_id
            })
        return jsonify(json_res)

    return render_template('profiles_list.html', users=users)


@app.route('/profile/<int:user_id>')
def profile_detail(user_id):
    user = User.query.get(user_id)

    if not user:
        return redirect(url_for('profiles'))

    if _request_is_ajax() and request.method == 'POST':
        return jsonify({
            "userid": user.user_id,
            "username": user.username,
            "image": user.get_image_url(),
            "sex": user.get_sex_display(),
            "age": user.age,
            "profile_add_on": user.added_on.strftime("%a, %d %b %Y"),
            "high_score": user.high_score,
            "tdollars": user.tdollars,
            })

    return render_template('profile.html', user=user)


@app.route('/uploads/<path:path>')
def send_uploads(path):
    return send_from_directory(app.config['UPLOAD_FOLDER'], path)
  

@app.route('/profile/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_profile(user_id):
  user = User.query.get(user_id)

  if user:
    db.session.delete(user)
    db.session.commit()

  return redirect(url_for('profiles'))
  
  