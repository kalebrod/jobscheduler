from subprocess import Popen,TimeoutExpired,PIPE
from datetime import datetime,timedelta

from .extensions import db,jobmanager
from .models import Jobs

reschedule = lambda time : time + timedelta(minutes=10)

def runjob(job,attemp=1):
    print('Job %s starting ......' %job.name)

    PROC = Popen(['python',job.task], stdout=PIPE, stderr=PIPE,close_fds=True)

    try: 
        outs,errs = PROC.communicate(timeout=1)
    
    except TimeoutExpired:
        PROC.kill()
        update_status(job.id,'Error')
    
    if errs:
        update_status(job.id,'Retrying')

    update_status(job.id,'Success')

    print('Job %s finished......' %job.name)


def update_status(jobid,status):
    with jobmanager.app.app_context():
        t = Jobs.query.get(jobid)
        t.status = status
        
        db.session.commit()