import os
import shlex
from subprocess import Popen,PIPE
from datetime import datetime,timedelta

from .extensions import db,jobmanager
from .models import Jobs


reschedule = lambda time : time + timedelta(minutes=3)

def runjob(job,attemp=1):
    # Might remove prints in a future
    print('Job {} - {} starting.'.format(job.name,job.id))

    command = shlex.split(job.task)
     
    PROC = Popen(command, stdout=PIPE, stderr=PIPE,close_fds=True)
    outs,errs = PROC.communicate(timeout=180) # 3 minutes should be enough

    if PROC.returncode:
        logger(job.id,job.name,errs)

        if attemp > 2:
            print('Error on job {} - {}. Attemp {}, abandoning task.'.format(job.name,job.id,attemp))
            return update_status(job.id,'Failed')

        print('Error on job {} - {}. Attemp {}, retrying.'.format(job.name,job.id,attemp))

        finish_time = datetime.now().replace(second=0, microsecond=0)
        newjob = update_status(job.id,'Retrying',reschedule(finish_time))

        return jobmanager.add_job(
            str(job.id),
            func=runjob,
            trigger='date',
            run_date=reschedule(finish_time),
            args=[newjob,attemp+1]
        )

    update_status(job.id,'Success')
    logger(job.name,job.id,b'Job successfully finished.')
    print('Job {} - {} successfully finished.'.format(job.name,job.id))


def update_status(jobid,status,time=False):
    with jobmanager.app.app_context(): 
    # Had to call app_context this way to work
        
        temp = Jobs.query.get(jobid)
        temp.status = status

        if time:
            temp.start = time
        
        db.session.commit()
    
        return Jobs.query.get(jobid)

def logger(id,name,pipe):
    with open('app/logs/logs.txt','a+') as logger:
        logger.write('\n')

        for line in pipe.decode().split('\r\n'):
            # print('{} - {}: {}'.format(id,name,str(line)))
            logger.write('{} - {}: {}\n'.format(id,name,line))
        
