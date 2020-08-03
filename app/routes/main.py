from datetime import datetime

from flask import Blueprint,render_template,request,redirect,url_for
from flask_login import current_user, login_required

from app.extensions import db, jobmanager
from app.models import Jobs
from app.utils import runjob

main = Blueprint('main',__name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('temp/index.html',jobs=Jobs.query.all())

@main.route('/newjob',methods=['GET','POST'])
def newjob():
    if request.method == 'POST':
        date = datetime.strptime(request.form['start'],'%Y-%m-%dT%H:%M')
        newjob = Jobs(
            name = request.form['name'],
            task = request.form['task'],
            status = 'Pending',
            start = date,
        )

        db.session.add(newjob)
        db.session.commit()
        
        jobmanager.add_job(
            str(newjob.id),
            func=runjob,
            trigger='date',
            run_date=newjob.start,
            args=[newjob]
        )

        return redirect(url_for('main.index'))
    
    return render_template('temp/newjob.html')