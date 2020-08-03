from subprocess import Popen,TimeoutExpired,PIPE
from datetime import datetime,timedelta

from .extensions import db,jobmanager
from .models import Jobs

reschedule = lambda time : time + timedelta(minutes=1)

def runjob(job,attemp=1):
    print('Job %s starting ......' %job.name)

    PROC = Popen(['python',job.task], stdout=PIPE, stderr=PIPE,close_fds=True)

    try: 
        outs,errs = PROC.communicate(timeout=1)
    
    except TimeoutExpired:
        PROC.kill()
        update_status(job.id,'Error')
    
    if errs:
        if attemp > 2:
            print('Error on Job %s. Attemp %s ,abandoning task ......' %(job.name,attemp))
            return update_status(job.id,'Error')

        print('Error on Job %s. Attemp %s ,retrying ......' %(job.name,attemp))
        newjob = update_status(job.id,'Retrying',reschedule(job.start))

        return jobmanager.add_job(
            str(job.id),
            func=runjob,
            trigger='date',
            run_date=reschedule(job.start),
            args=[newjob,attemp+1]
        )

    update_status(job.id,'Success')

    print('Job %s finished ......' %job.name)


def update_status(jobid,status,time=False):
    with jobmanager.app.app_context():
        temp = Jobs.query.get(jobid)
        temp.status = status

        if time:
            temp.start = time
        
        db.session.commit()
    
        return Jobs.query.get(jobid)
