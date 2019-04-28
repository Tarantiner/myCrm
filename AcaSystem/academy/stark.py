from stark.service.v1 import site
from academy import models
from academy.views.school import SchoolHandler
from academy.views.userinfo import UserInfolHandler
from academy.views.depart import DepartHandler
from academy.views.classes import ClassesHandler
from academy.views.course import CourseHandler
from academy.views.develop import DevelopHandler
from academy.views.pub_customer import PubCustomerHandler
from academy.views.pri_customer import PriCustomerHandler
from academy.views.consult import ConsultRecordHandler
from academy.views.payment import PaymentHandler
from academy.views.check_payment_record import CheckPaymentRecordHandler
from academy.views.student import StudentHandler
from academy.views.score_record import ScoreHandler
from academy.views.homework import HomeworkHandler
from academy.views.course_record import CourseRecordHandler


site.register(models.UserInfo, UserInfolHandler)
site.register(models.School, SchoolHandler)
site.register(models.Department, DepartHandler)
site.register(models.Classes, ClassesHandler)
site.register(models.Course, CourseHandler)
site.register(models.Development, DevelopHandler)
site.register(models.Customer, PubCustomerHandler, prev='pub')
site.register(models.Customer, PriCustomerHandler, prev='pri')
site.register(models.ConsultRecord, ConsultRecordHandler)
site.register(models.PaymentRecord, PaymentHandler)
site.register(models.PaymentRecord, CheckPaymentRecordHandler, prev='check')
site.register(models.Student, StudentHandler)
site.register(models.ScoreRecord, ScoreHandler)
site.register(models.Homework, HomeworkHandler)
site.register(models.CourseRecord, CourseRecordHandler)
