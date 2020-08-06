from datetime import datetime

from flask import Blueprint,render_template,request,redirect,url_for
from flask_login import current_user, login_required

from sqlalchemy import or_

from app.extensions import db, jobmanager
from app.models import Jobs
from app.utils import runjob

main = Blueprint('main',__name__)

@main.route('/')
@main.route('/index')
def index():
    pending = Jobs.query.filter(
        or_(Jobs.status =='Pending',Jobs.status=='Retrying')
    )
    done = Jobs.query.filter(
        or_(Jobs.status =='Success',Jobs.status=='Failed')
    )

    return render_template('temp/index.html',pending=pending,done=done)

@main.route('/newjob',methods=['GET','POST'])
def newjob():
    if request.method == 'POST':
        date = datetime.strptime(request.form['start'],'%Y-%m-%dT%H:%M')
        newjob = Jobs(
            name = request.form['name'],
            task = request.form['task'],
            status = 'Pending',
            start = date,
            active = bool(request.form.get('active'))
        )

        db.session.add(newjob)
        db.session.commit()
        
        if newjob.active == 'date':
            jobmanager.add_job(
                str(newjob.id),
                func=runjob,
                trigger=date,
                run_date=newjob.start,
                args=[newjob],
                misfire_grace_time=10,
            )
        else:
            minutes = int(request.form['minutes'])
            hours = int(request.form['hours'])
            days = int(request.form['days'])
            weeks = int(request.form['weeks'])

            jobmanager.add_job(
                str(newjob.id),
                func=runjob,
                trigger='interval',
                start_date=newjob.start,
                minutes = minutes,
                hours = hours,
                days = days, 
                weeks = weeks,
                args=[newjob],
                jitter=10,
            )

        jobmanager.remove_all_jobs() 
        return redirect(url_for('main.index'))
    
    return render_template('temp/newjob.html')