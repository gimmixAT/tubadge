from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
from random import randint


def index(request):
    #here comes the testing

    output = 'Test:<br/>'

    count_semester = 10
    count_teachers = 5
    teachers = []
    interval_courses = [2, 5]

    interval_badges = [1, 20]
    interval_badges_variance = [-1, 1]

    interval_student_count = [10, 500]
    interval_student_count_variance = [10, 500]

    interval_badge_count = [0, 100]
    interval_badge_count_variance = [-5, 5]

    output += 'Semester: ' + str(count_semester) + '<br/>'
    output += 'Teachers: ' + str(count_teachers) + '<br/>'
    output += 'Courses per Teacher: ' + str(interval_courses[0]) + ' - ' + str(interval_courses[1]) + '<br/>'
    output += 'Students per Course: ' + str(interval_student_count[0]) + ' - ' + str(interval_student_count[1]) + ' | variance: '+ str(interval_student_count_variance[0]) + ' , ' + str(interval_student_count_variance[1]) +'<br/>'
    output += 'Badges per Course: ' + str(interval_badges[0]) + ' - ' + str(interval_badges[1]) + ' | variance: '+ str(interval_badges_variance[0]) + ' , ' + str(interval_badges_variance[1]) +'<br/>'
    output += 'Badges issued: ' + str(interval_badge_count[0]) + ' - ' + str(interval_badge_count[1]) + ' | variance: '+ str(interval_badge_count_variance[0]) + ' , ' + str(interval_badge_count_variance[1]) +'<br/>'

    #create teachers
    output += '<br/><br/>'
    output += 'Creating Teachers, Courses &amp; Badges:'

    for t in range(count_teachers):
        teachers.append(
            Teacher(
                count_semester,
                randint(interval_courses[0], interval_courses[1]),
                interval_student_count,
                interval_badges,
                interval_badges_variance,
                interval_badge_count,
                interval_badge_count_variance
            )
        )

    #iterate semesters
    output += '<br/><br/>'
    output += 'Iterating Semesters:'

    for semester in range(count_semester):
        for teacher in teachers:
            teacher.issue_badges(semester)

    output += '<br/><br/>'

    for teacher in teachers:
        output += teacher.to_string() + '<br/><br/>'

    return render_to_response('simple.html', {'output': output})


class Teacher:

    def __init__(self,
                 semesters,
                 count_courses,
                 interval_student_count,
                 interval_badges,
                 interval_badges_variance,
                 interval_issued,
                 interval_issued_variance):

        self.courses = []
        self.semesters = semesters

        for c in range(count_courses):
            stud_min = randint(interval_student_count[0], interval_student_count[1])
            self.courses.append(
                Course(
                    self,
                    semesters,
                    [stud_min, randint(stud_min, interval_student_count[1])],
                    interval_badges,
                    [interval_issued[0], randint(interval_issued[0], interval_issued[1])],
                    interval_issued_variance
                )
            )

    def issue_badges(self, semester):
        for course in self.courses:
            course.issue_badges(semester)

    def semester_badge_count(self, semester, value = -1):
        count = 0

        for course in self.courses:
            count += course.semester_badge_count(semester, value)

        return count

    def total_badge_count(self, value = -1):
        count = 0

        for course in self.courses:
            count += course.total_badge_count(value)

        return count

    def total_badge_mean(self, value = -1):
        return float(self.total_badge_count(value)) / (float(self.semesters) + float(len(self.courses)))

    def total_badge_variance(self, value = -1):
        mean = float(self.total_badge_mean(value))

        out = 0

        for s in range(0,self.semesters):
            out += pow(float(self.semester_badge_count(s, value)) - mean, 2)

        return pow(out / float(self.total_badge_count(value) - 1), 0.5)

    def to_string(self):
        output = 'Teacher:<br/>'
        output += str(len(self.courses)) + ' Courses: <br/>'
        output += str(self.total_badge_count()) + ' Badges issued. (mean: '+ str(self.total_badge_count() / self.semesters) +') <br/>'

        for c in self.courses:
            output += c.to_string() + '<br/>'

        return output




class Course:

    def __init__(self, teacher, semesters, interval_student_count, interval_badges, interval_issued, interval_variance):
        self.teacher = teacher
        self.badges = []
        self.students = [0] * semesters
        self.student_count = 0
        self.interval_variance = interval_variance
        self.interval_students = interval_student_count
        for c in range(randint(interval_badges[0], interval_badges[1])):
            self.badges.append(
                Badge(
                    self,
                    semesters,
                    interval_issued,
                    interval_variance
                )
            )

    def issue_badges(self, semester):
        self.students[semester] = randint(self.interval_students[0], self.interval_students[1])
        self.student_count += self.students[semester]
        for badge in self.badges:
            badge.issue(semester, self.students[semester])

    def total_badge_count(self, value = -1):
        count = 0;
        for b in self.badges:
            if(value < 0 or b.value == value):
                count += b.total_count

        return count

    def semester_badge_count(self, semester, value = -1):
        count = 0;
        for b in self.badges:
            if(value < 0 or b.value == value):
                count += b.issue_count[semester]

        return count

    def total_student_count(self):
        return self.student_count

    def to_string(self):
        output = 'Course:<br/>'
        output += str(len(self.badges)) + ' Badges: <br/>'
        output += str(self.total_badge_count()) + ' Badges issued. <br/>'
        output += str(self.student_count) + ' Students. <br/>'

        output += '<div style="display:-moz-box; -moz-box-pack:end; -moz-box-align:end; display:-webkit-box; -webkit-box-pack:end; -webkit-box-align:end;">'
        for c in self.students:
            output += '<div style="display:inline-block; border:1px solid #fff; width:33px;">'
            output += '<div style="background-color:#3300ff; height:'+str(float(c) / float(self.interval_students[1]) * 100.0)+'px;"></div>'
            output += '<div style="background-color:#ffffff; padding:3px;">'+str(c)+'</div></div>'

        output += '</div><br style="clear:both;"/>'

        for b in self.badges:
            output += b.to_string() + '<br/>'

        return output


class Badge:

    def __init__(self, course, semesters, interval, interval_variance):
        self.course = course
        self.value = randint(0, 2); #gold silver bronze
        self.factors = [2, 1, 0.5]
        self.issue_count = [0] * semesters
        self.total_count = 0
        self.interval_per_semester = interval
        self.interval_variance = interval_variance

    def issue(self, semester, students):
        self.issue_count[semester] = min(students, max(0, randint(self.interval_per_semester[0], self.interval_per_semester[1]) + randint(self.interval_variance[0], self.interval_variance[1])))
        self.total_count += self.issue_count[semester]

    def to_string(self):
        output = 'Bagde (' + str(self.value) + ') issued:<br/>'
        output += 'total: '+str(self.total_count)+'<br/>'

        output += '<div style="display:inline-block;"><div style="display:-moz-box; -moz-box-pack:end; -moz-box-align:end; display:-webkit-box; -webkit-box-pack:end; -webkit-box-align:end;">'
        for c in self.issue_count:
            output += '<div style="display:inline-block; border:1px solid #fff; width:33px;">'
            output += '<div style="background-color:#ff0000; height:'+str(c)+'px;"></div>'
            output += '<div style="background-color:#ffffff; padding:3px;">'+str(c)+'</div></div>'

        output += '</div><br style="clear:both;"/></div>'
        output += '<div style="display:inline-block; margin: 0 0 0 10px;"><b>Value:</b> '+str(self.calc_value())+'<br/><b>Cred.:</b> '+str(self.calc_cred())+'</div>'

        return output

    def mean(self):
        return float(self.total_count) / float(len(self.issue_count))

    def variance(self):
        mean = self.mean()
        out = 0
        for s in range(0,len(self.issue_count)):
            out += pow(float(self.issue_count[s]) - mean, 2)

        return pow(out / float(self.total_count - 1), 0.5)

    def calc_value(self):
        #return pow(1.0 / (float(self.course.total_student_count()) / float(self.total_count)), self.factors[self.value])
        return 1 - pow(float(self.total_count) / float(self.course.total_student_count()), self.factors[self.value]);
        #return self.value

    def calc_cred(self):
        #return #str(self.course.teacher.total_badge_count(self.value)) \
               #+ " - " + str(self.course.teacher.total_badge_count()) \
               #+ " -> " + str((float(self.course.teacher.total_badge_count(self.value)) / float(self.course.teacher.total_badge_count())))\
        return str(1 - pow((float(self.course.teacher.total_badge_count(self.value)) / float(self.course.teacher.total_badge_count())), self.factors[self.value]))